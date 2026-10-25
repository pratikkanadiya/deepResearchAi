import re
import time
from typing import List

from dotenv import load_dotenv
from app.services.model import get_llm
from langchain_core.prompts import ChatPromptTemplate

from app.schemas.evidence import (
    EvidenceExtractionResult
)

load_dotenv()


class EvidenceExtractorAgent:

    def __init__(self):

        self.llm = get_llm()

        self.structured_llm = (
            self.llm.with_structured_output(
                EvidenceExtractionResult,
                method="json_schema",
                strict=False,
            )
        )

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
You are an evidence extraction agent.

Your task is to extract factual evidence from
the provided documents.

Rules:

1. Only extract claims supported by the documents.

2. Do not invent information.

3. Every claim MUST have a source URL.

4. supporting_text must represent the actual
   evidence found in the document.

5. Clearly identify limitations.

6. Confidence represents confidence that the
   extracted claim is supported by the provided text.

7. Do not write a final research report.

8. Separate evidence from interpretation.

9. If the documents do not contain sufficient
   evidence, return fewer evidence items rather
   than guessing.
"""
            ),
            (
                "human",
                """
Research question:

{question}

Documents:

{documents}
"""
            )
        ])

    def extract(
        self,
        question: str,
        documents: List[dict]
    ) -> EvidenceExtractionResult:

        formatted_documents = []

        for index, document in enumerate(
            documents
        ):

            formatted_documents.append(
                f"""
DOCUMENT {index + 1}

Title:
{document.get("title", "")}

URL:
{document.get("url", "")}

Content:
{document.get("content", "")[:10000]}
"""
            )

        document_text = "\n".join(
            formatted_documents
        )

        chain = self.prompt | self.structured_llm

        inputs = {
            "question": question,
            "documents": document_text,
        }

        # Groq TPM limits are temporary. Honor the retry delay in its error
        # and retry without exposing the raw 429 if the provider recovers.
        for attempt in range(3):
            try:
                return chain.invoke(inputs)
            except Exception as exc:
                message = str(exc)
                is_rate_limit = "429" in message or "rate_limit" in message.lower()
                if not is_rate_limit or attempt == 2:
                    raise

                match = re.search(
                    r"try again in\s+(\d+(?:\.\d+)?)\s*(ms|s|m)",
                    message,
                    flags=re.IGNORECASE,
                )
                if match:
                    delay = float(match.group(1))
                    unit = match.group(2).lower()
                    if unit == "ms":
                        delay /= 1000
                    elif unit == "m":
                        delay *= 60
                else:
                    delay = 3 * (attempt + 1)

                delay = min(max(delay + 0.5, 1), 60)
                print(
                    "Evidence extraction is temporarily rate limited; "
                    f"retrying in {delay:.1f}s ({attempt + 1}/2)."
                )
                time.sleep(delay)


if __name__ == "__main__":

    agent = EvidenceExtractorAgent()

    documents = [
        {
            "title": "Example AI Healthcare Article",
            "url": "https://example.com/ai-healthcare",
            "content": """
            Artificial intelligence systems are being
            evaluated for applications in medical
            diagnosis and clinical decision support.
            """
        }
    ]

    result = agent.extract(
        question=(
            "How is AI being used in healthcare?"
        ),
        documents=documents
    )

    print("\nQUESTION:")
    print(result.question)

    print("\nEVIDENCE:")

    for item in result.evidence:

        print("\n-------------------------")
        print("CLAIM:")
        print(item.claim)

        print("\nSUPPORTING TEXT:")
        print(item.supporting_text)

        print("\nSOURCE:")
        print(item.source_url)

        print("\nTYPE:")
        print(item.evidence_type)

        print("\nCONFIDENCE:")
        print(item.confidence)

        print("\nLIMITATIONS:")
        for limitation in item.limitations:
            print("-", limitation)


