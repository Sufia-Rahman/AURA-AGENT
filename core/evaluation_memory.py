import json
import os
from datetime import datetime


class EvaluationMemory:

    def __init__(self, file_path="evaluation_memory.json"):

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

    def add_record(
        self,
        question,
        answer,
        evaluation
    ):

        record = {
            "id": len(self.records) + 1,
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "evaluation": evaluation
        }

        self.records.append(record)

        if len(self.records) > 500:
            self.records = self.records[-500:]

        self._save()

        return record

    def recent(self, limit=10):

        return self.records[-limit:]

    def statistics(self):

        if not self.records:

            return {
                "evaluations": 0,
                "average_overall_score": 0,
                "average_factual_grounding": 0,
                "average_relevance": 0,
                "average_completeness": 0,
                "average_source_support": 0,
                "average_hallucination_risk": 0
            }

        evaluations = [
            record.get("evaluation", {})
            for record in self.records
        ]

        def average(field):

            values = [
                evaluation.get(field, 0)
                for evaluation in evaluations
            ]

            return round(
                sum(values) / len(values),
                2
            )

        return {
            "evaluations": len(self.records),
            "average_overall_score": average(
                "overall_score"
            ),
            "average_factual_grounding": average(
                "factual_grounding"
            ),
            "average_relevance": average(
                "relevance"
            ),
            "average_completeness": average(
                "completeness"
            ),
            "average_source_support": average(
                "source_support"
            ),
            "average_hallucination_risk": average(
                "hallucination_risk"
            )
        }