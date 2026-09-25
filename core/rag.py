import hashlib
import json
import math
import os

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


class RAGEngine:

    def __init__(self, knowledge_dir="knowledge"):

        self.knowledge_dir = knowledge_dir
        self.store_file = "knowledge_store_local.json"

        self.embedding_model_name = "all-MiniLM-L6-v2"

        self.embedding_model = SentenceTransformer(
            self.embedding_model_name
        )

        os.makedirs(
            self.knowledge_dir,
            exist_ok=True
        )

        self.documents = self._load_store()

    def _load_store(self):

        if not os.path.exists(self.store_file):
            return []

        try:
            with open(
                self.store_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            return data if isinstance(data, list) else []

        except (
            json.JSONDecodeError,
            OSError
        ):
            return []

    def _save_store(self):

        with open(
            self.store_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.documents,
                file,
                indent=2,
                ensure_ascii=False
            )

    @staticmethod
    def _file_hash(file_path):

        hasher = hashlib.sha256()

        with open(
            file_path,
            "rb"
        ) as file:

            while True:

                chunk = file.read(1024 * 1024)

                if not chunk:
                    break

                hasher.update(chunk)

        return hasher.hexdigest()

    def _extract_text(self, file_path):

        extension = os.path.splitext(
            file_path
        )[1].lower()

        if extension == ".pdf":

            reader = PdfReader(
                file_path
            )

            pages = []

            for page in reader.pages:

                text = page.extract_text()

                if text:
                    pages.append(text)

            return "\n".join(pages)

        if extension == ".txt":

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                return file.read()

        return ""

    def _chunk_text(
        self,
        text,
        chunk_size=1200,
        overlap=200
    ):

        text = " ".join(
            text.split()
        )

        chunks = []

        start = 0

        step = chunk_size - overlap

        while start < len(text):

            end = start + chunk_size

            chunk = text[
                start:end
            ].strip()

            if chunk:
                chunks.append(chunk)

            start += step

        return chunks

    def _embed(self, text):

        embedding = self.embedding_model.encode(
            text,
            normalize_embeddings=True
        )

        return embedding.tolist()

    def ingest_file(self, file_path):

        filename = os.path.basename(
            file_path
        )

        file_hash = self._file_hash(
            file_path
        )

        existing_hashes = {
            item.get("source_hash")
            for item in self.documents
            if item.get("source") == filename
        }

        if file_hash in existing_hashes:
            return 0

        self.documents = [
            item
            for item in self.documents
            if item.get("source") != filename
        ]

        text = self._extract_text(
            file_path
        )

        if not text.strip():

            self._save_store()

            return 0

        chunks = self._chunk_text(
            text
        )

        added = 0

        for index, chunk in enumerate(chunks):

            embedding = self._embed(
                chunk
            )

            self.documents.append(
                {
                    "source": filename,
                    "source_hash": file_hash,
                    "chunk_id": index,
                    "text": chunk,
                    "embedding": embedding
                }
            )

            added += 1

        self._save_store()

        return added

    def remove_file(self, filename):

        before = len(
            self.documents
        )

        self.documents = [
            item
            for item in self.documents
            if item.get("source") != filename
        ]

        removed = (
            before -
            len(self.documents)
        )

        if removed:
            self._save_store()

        return removed

    @staticmethod
    def _cosine_similarity(
        vector_a,
        vector_b
    ):

        dot_product = sum(
            a * b
            for a, b in zip(
                vector_a,
                vector_b
            )
        )

        magnitude_a = math.sqrt(
            sum(
                a * a
                for a in vector_a
            )
        )

        magnitude_b = math.sqrt(
            sum(
                b * b
                for b in vector_b
            )
        )

        if (
            magnitude_a == 0
            or magnitude_b == 0
        ):
            return 0

        return dot_product / (
            magnitude_a *
            magnitude_b
        )

    def search(
        self,
        query,
        top_k=5
    ):

        if not self.documents:
            return []

        query_embedding = self._embed(
            query
        )

        scored = []

        for document in self.documents:

            score = self._cosine_similarity(
                query_embedding,
                document["embedding"]
            )

            scored.append(
                {
                    "source": document["source"],
                    "chunk_id": document["chunk_id"],
                    "text": document["text"],
                    "score": score
                }
            )

        scored.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return scored[:top_k]

    def statistics(self):

        sources = sorted(
            {
                item.get("source")
                for item in self.documents
            }
        )

        return {
            "documents": len(sources),
            "chunks": len(self.documents),
            "sources": sources,
            "embedding_model": self.embedding_model_name
        }