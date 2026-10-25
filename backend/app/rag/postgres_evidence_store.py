from __future__ import annotations

import re
import uuid

from sqlalchemy import desc, func

from app.database.connection import SessionLocal
from app.database.models import Evidence


class PostgresEvidenceStore:

    @staticmethod
    def _payload(item: Evidence) -> dict:
        return {
            "evidence_id": item.id,
            "claim": item.claim,
            "supporting_text": item.supporting_text,
            "source_url": item.source_url or "",
            "evidence_type": item.evidence_type or "",
            "confidence": item.confidence or 0,
            "limitations": item.limitations or [],
            "research_id": item.research_id,
        }

    def add_evidence_batch(
        self,
        evidence_items: list[dict],
        research_id: str,
    ) -> list[str]:
        if not evidence_items:
            return []

        session = SessionLocal()
        ids = []
        try:
            for item in evidence_items:
                evidence_id = str(uuid.uuid4())
                row = Evidence(
                    id=evidence_id,
                    research_id=research_id,
                    claim=item.get("claim") or "",
                    supporting_text=item.get("supporting_text") or "",
                    source_url=item.get("source_url") or "",
                    evidence_type=item.get("evidence_type") or "",
                    confidence=item.get("confidence") or 0,
                    limitations=item.get("limitations") or [],
                )
                session.add(row)
                ids.append(evidence_id)

            session.commit()
            return ids
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def search(
        self,
        query: str,
        research_id: str,
        limit: int = 8,
    ) -> list[dict]:
        session = SessionLocal()
        try:
            # OR across cleaned terms keeps a multi-question research query
            # from becoming so restrictive that it hides relevant evidence.
            tokens = re.findall(r"[a-z0-9]+", (query or "").lower())
            stop_words = {
                "a", "an", "and", "are", "as", "at", "be", "by", "can",
                "do", "does", "for", "from", "how", "in", "into", "is",
                "it", "of", "on", "or", "the", "to", "using", "was",
                "what", "when", "where", "which", "why", "with",
            }
            tokens = [
                token for token in tokens
                if len(token) >= 2 and token not in stop_words
            ]
            tsquery_text = " | ".join(dict.fromkeys(tokens))

            if tsquery_text:
                vector = func.to_tsvector(
                    "simple",
                    func.concat_ws(" ", Evidence.claim, Evidence.supporting_text),
                )
                tsquery = func.to_tsquery("simple", tsquery_text)
                rank = func.ts_rank(vector, tsquery)
                matches = (
                    session.query(Evidence, rank.label("score"))
                    .filter(
                        Evidence.research_id == research_id,
                        vector.op("@@")(tsquery),
                    )
                    .order_by(rank.desc(), desc(Evidence.confidence))
                    .limit(limit)
                    .all()
                )
                if matches:
                    return [
                        {
                            "id": row.id,
                            "score": float(score or 0),
                            "payload": self._payload(row),
                        }
                        for row, score in matches
                    ]

            # If no terms match, return this run's evidence by confidence so
            # synthesis still has evidence without requiring a vector service.
            rows = (
                session.query(Evidence)
                .filter(Evidence.research_id == research_id)
                .order_by(desc(Evidence.confidence))
                .limit(limit)
                .all()
            )
            return [
                {
                    "id": row.id,
                    "score": float(row.confidence or 0),
                    "payload": self._payload(row),
                }
                for row in rows
            ]
        finally:
            session.close()
