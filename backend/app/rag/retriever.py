from app.rag.postgres_evidence_store import PostgresEvidenceStore


class EvidenceRetriever:

    def __init__(self, evidence_store: PostgresEvidenceStore | None = None):
        self.evidence_store = evidence_store or PostgresEvidenceStore()

    def retrieve(
        self,
        query: str,
        research_id: str,
        limit: int = 8
    ) -> list[dict]:

        results = self.evidence_store.search(
            query=query,
            research_id=research_id,
            limit=limit
        )

        return results


if __name__ == "__main__":

    retriever = EvidenceRetriever()

    results = retriever.retrieve(
        "impact of artificial intelligence "
        "on medical diagnosis"
    )

    for result in results:

        print("\n-------------------")
        print("Score:", result["score"])

        payload = result["payload"]

        print(
            "Claim:",
            payload.get("claim")
        )

        print(
            "Source:",
            payload.get("source_url")
        )
