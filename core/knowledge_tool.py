from .rag import RAGEngine


class KnowledgeTool:

    def __init__(self):

        self.rag = RAGEngine()

    def definitions(self):

        return [
            {
                "type": "function",
                "name": "search_knowledge",
                "description": (
                    "Search AURA's private knowledge base "
                    "for relevant information from ingested "
                    "PDF and TXT documents."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "query"
                    ],
                    "additionalProperties": False
                }
            }
        ]

    def execute(self, query):

        results = self.rag.search(
            query=query,
            top_k=5
        )

        if not results:

            return (
                "No relevant information was found "
                "in AURA's private knowledge base."
            )

        output = []

        for result in results:

            output.append(
                f"PRIVATE SOURCE: {result['source']}\n"
                f"RELEVANCE: {result['score']:.4f}\n"
                f"CONTENT:\n{result['text']}"
            )

        return "\n\n".join(
            output
        )

    def statistics(self):

        return self.rag.statistics()