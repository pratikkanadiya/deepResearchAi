import os
from functools import lru_cache
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings

load_dotenv()

embedding_model = os.getenv("MODEL_NAME") or "BAAI/bge-small-en-v1.5"


@lru_cache(maxsize=2)
def _load_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)

class EmbeddingTool:

    def __init__(
        self,
        model_name: str = embedding_model
    ):
        self.model = _load_model(model_name)

    def embed_text(
        self,
        text: str
    ) -> list[float]:

        vector = self.model.encode(
            text,
            normalize_embeddings=True
        )

        return vector.tolist()

    def embed_documents(
        self,
        texts: list[str]
    ) -> list[list[float]]:

        vectors = self.model.encode(
            texts,
            normalize_embeddings=True
        )

        return vectors.tolist()


if __name__ == "__main__":

    embedding_tool = EmbeddingTool()

    text = (
        "Artificial intelligence can assist "
        "medical diagnosis."
    )

    vector = embedding_tool.embed_text(text)

    print("Vector length:", len(vector))
    print("First 10 values:", vector[:10])
