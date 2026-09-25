import json
import os
from datetime import datetime


class ReflectionMemory:

    def __init__(self, file_path="reflection_memory.json"):

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

        except (
            json.JSONDecodeError,
            OSError
        ):

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

    def add_record(self, reflection):

        record = {
            "id": len(self.records) + 1,
            "timestamp": datetime.now().isoformat(),
            "reflection": reflection
        }

        self.records.append(record)

        if len(self.records) > 200:
            self.records = self.records[-200:]

        self._save()

        return record

    def recent(self, limit=10):

        return self.records[-limit:]

    def latest(self):

        if not self.records:
            return None

        return self.records[-1]

    def get_strategies(self, limit=10):

        strategies = []

        for record in self.records[-limit:]:

            reflection = record.get(
                "reflection",
                {}
            )

            strategy = reflection.get(
                "improvement_strategy"
            )

            if strategy:
                strategies.append(strategy)

        return strategies

    def strategy_context(self, limit=10):

        strategies = self.get_strategies(
            limit=limit
        )

        if not strategies:
            return (
                "No previous improvement strategies "
                "are available."
            )

        lines = [
            "PREVIOUS IMPROVEMENT STRATEGIES:"
        ]

        for index, strategy in enumerate(
            strategies,
            start=1
        ):

            lines.append(
                f"{index}. {strategy}"
            )

        return "\n".join(lines)