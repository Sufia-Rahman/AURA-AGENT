import json
import os
from datetime import datetime


class ReflectionMemory:

    def __init__(
        self,
        file_path="reflection_memory.json",
        max_records=200
    ):

        self.file_path = file_path
        self.max_records = max_records

        self.records = self._load()

    def _load(self):

        if not os.path.exists(
            self.file_path
        ):
            return []

        try:

            with open(
                self.file_path,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if isinstance(data, list):
                return data

            return []

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

    def add_record(
        self,
        reflection
    ):

        if not isinstance(
            reflection,
            dict
        ):
            return {
                "status": "ignored",
                "reason": "Invalid reflection."
            }

        record = {
            "timestamp":
                datetime.now().isoformat(),

            "failure_pattern":
                reflection.get(
                    "failure_pattern",
                    ""
                ),

            "likely_cause":
                reflection.get(
                    "likely_cause",
                    ""
                ),

            "improvement_strategy":
                reflection.get(
                    "improvement_strategy",
                    ""
                ),

            "expected_effect":
                reflection.get(
                    "expected_effect",
                    ""
                )
        }

        if not any(
            record[key]
            for key in [
                "failure_pattern",
                "likely_cause",
                "improvement_strategy",
                "expected_effect"
            ]
        ):

            return {
                "status": "ignored",
                "reason": "Empty reflection."
            }

        self.records.append(record)

        if len(self.records) > self.max_records:

            self.records = (
                self.records[-self.max_records:]
            )

        self._save()

        return {
            "status": "stored",
            "total_records": len(
                self.records
            )
        }

    def recent(
        self,
        limit=10
    ):

        return self.records[-limit:]

    def get_strategies(
        self,
        limit=20
    ):

        strategies = []

        for record in self.records[-limit:]:

            strategy = record.get(
                "improvement_strategy",
                ""
            ).strip()

            if strategy:
                strategies.append(
                    strategy
                )

        return strategies

    def strategy_context(self):

        strategies = (
            self.get_strategies(
                limit=20
            )
        )

        if not strategies:

            return (
                "No previous improvement "
                "strategies are available."
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

    def statistics(self):

        return {
            "total_reflections":
                len(self.records),

            "max_records":
                self.max_records
        }