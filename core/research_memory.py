import json
import os
from datetime import datetime


class ResearchMemory:

    def __init__(self, file_path="research_memory.json"):
        self.file_path = file_path
        self.records = self._load()

    def _load(self):
        if not os.path.exists(self.file_path):
            return []

        try:
            with open(
                self.file_path,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            return data if isinstance(data, list) else []

        except (json.JSONDecodeError, OSError):
            return []

    def _save(self):
        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                self.records,
                file,
                indent=2,
                ensure_ascii=False
            )

    def add_record(
        self,
        query,
        plan,
        answer,
        sources=None
    ):
        record = {
            "id": len(self.records) + 1,
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "plan": plan,
            "answer": answer,
            "sources": sources or []
        }

        self.records.append(record)

        if len(self.records) > 100:
            self.records = self.records[-100:]

        self._save()

        return record

    def recent(self, limit=5):
        return self.records[-limit:]

    def search(self, keyword):
        keyword = keyword.lower()

        results = []

        for record in self.records:
            query = record.get("query", "").lower()
            answer = record.get("answer", "").lower()

            if keyword in query or keyword in answer:
                results.append(record)

        return results

    def get_sources(self, research_id):
        for record in self.records:
            if record.get("id") == research_id:
                return record.get("sources", [])

        return []

    def summary(self, limit=5):
        records = self.recent(limit)

        if not records:
            return "No previous research is available."

        lines = []

        for record in records:
            sources = record.get("sources", [])

            lines.append(
                f"Research #{record['id']}: "
                f"{record['query']}\n"
                f"Result: {record['answer'][:500]}\n"
                f"Sources: {len(sources)}"
            )

        return "\n\n".join(lines)