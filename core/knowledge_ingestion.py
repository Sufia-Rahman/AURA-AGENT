import os

from .rag import RAGEngine


class KnowledgeIngestion:

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".txt"
    }

    def __init__(
        self,
        knowledge_dir="knowledge"
    ):

        self.knowledge_dir = knowledge_dir

        self.rag = RAGEngine(
            knowledge_dir=knowledge_dir
        )

        os.makedirs(
            self.knowledge_dir,
            exist_ok=True
        )

    def scan(self):

        files = []

        for filename in os.listdir(
            self.knowledge_dir
        ):

            file_path = os.path.join(
                self.knowledge_dir,
                filename
            )

            if not os.path.isfile(
                file_path
            ):
                continue

            extension = os.path.splitext(
                filename
            )[1].lower()

            if extension in self.SUPPORTED_EXTENSIONS:

                files.append(
                    file_path
                )

        return sorted(
            files
        )

    def ingest_new_documents(self):

        results = []

        current_files = {
            os.path.basename(
                path
            )
            for path in self.scan()
        }

        indexed_files = {
            item.get("source")
            for item in self.rag.documents
        }

        removed_files = (
            indexed_files -
            current_files
        )

        for filename in removed_files:

            removed = self.rag.remove_file(
                filename
            )

            if removed:

                results.append(
                    {
                        "file": filename,
                        "chunks": -removed,
                        "status": "removed"
                    }
                )

        for file_path in self.scan():

            filename = os.path.basename(
                file_path
            )

            chunk_count = self.rag.ingest_file(
                file_path
            )

            if chunk_count > 0:

                results.append(
                    {
                        "file": filename,
                        "chunks": chunk_count,
                        "status": "indexed"
                    }
                )

        return results