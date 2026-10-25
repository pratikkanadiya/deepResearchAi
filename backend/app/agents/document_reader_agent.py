from typing import List

from pydantic import BaseModel

from app.tools.document_reader import (
    DocumentReaderTool
)


class Document(BaseModel):
    url: str
    title: str
    content: str
    content_length: int
    status_code: int


class DocumentReaderResult(BaseModel):
    documents: List[Document]


class DocumentReaderAgent:

    def __init__(self):

        self.reader = DocumentReaderTool()

    def read_documents(
        self,
        urls: List[str]
    ) -> DocumentReaderResult:

        documents = []

        for url in urls:

            try:

                result = self.reader.read(
                    url
                )

                documents.append(
                    Document(
                        url=result["url"],
                        title=result["title"],
                        content=result["content"],
                        content_length=result[
                            "content_length"
                        ],
                        status_code=result[
                            "status_code"
                        ]
                    )
                )

            except Exception as e:

                print(
                    f"Failed to read {url}: {e}"
                )

        return DocumentReaderResult(
            documents=documents
        )


if __name__ == "__main__":

    agent = DocumentReaderAgent()

    urls = [
        "https://example.com"
    ]

    result = agent.read_documents(urls)

    for document in result.documents:

        print("\n-------------------------")
        print("TITLE:", document.title)
        print("URL:", document.url)
        print(
            "CONTENT LENGTH:",
            document.content_length
        )
        print(
            "CONTENT:",
            document.content[:1000]
        )