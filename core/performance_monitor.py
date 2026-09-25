class PerformanceMonitor:

    METRICS = [
        "factual_grounding",
        "relevance",
        "completeness",
        "source_support"
    ]

    def __init__(self, evaluation_memory):

        self.evaluation_memory = evaluation_memory

    def analyze(self):

        statistics = self.evaluation_memory.statistics()

        if statistics["evaluations"] == 0:

            return {
                "status": "insufficient_data",
                "message": "No evaluation data is available yet."
            }

        scores = {
            "factual_grounding": statistics[
                "average_factual_grounding"
            ],
            "relevance": statistics[
                "average_relevance"
            ],
            "completeness": statistics[
                "average_completeness"
            ],
            "source_support": statistics[
                "average_source_support"
            ]
        }

        weakest_metric = min(
            scores,
            key=scores.get
        )

        strongest_metric = max(
            scores,
            key=scores.get
        )

        hallucination_risk = statistics[
            "average_hallucination_risk"
        ]

        recommendations = []

        if scores["factual_grounding"] < 70:
            recommendations.append(
                "Improve factual grounding and evidence verification."
            )

        if scores["relevance"] < 70:
            recommendations.append(
                "Improve understanding of the user's actual goal."
            )

        if scores["completeness"] < 70:
            recommendations.append(
                "Improve coverage of all parts of the user's request."
            )

        if scores["source_support"] < 70:
            recommendations.append(
                "Improve source usage and evidence support."
            )

        if hallucination_risk > 30:
            recommendations.append(
                "Increase verification and reduce unsupported claims."
            )

        if not recommendations:
            recommendations.append(
                "Current performance is stable across tracked metrics."
            )

        return {
            "status": "analyzed",
            "evaluations": statistics["evaluations"],
            "overall_score": statistics[
                "average_overall_score"
            ],
            "hallucination_risk": hallucination_risk,
            "metric_scores": scores,
            "strongest_area": strongest_metric,
            "weakest_area": weakest_metric,
            "recommendations": recommendations
        }

    def report(self):

        analysis = self.analyze()

        if analysis["status"] == "insufficient_data":

            return analysis["message"]

        lines = [
            "AURA PERFORMANCE REPORT",
            "",
            f"Evaluations: {analysis['evaluations']}",
            f"Overall Score: {analysis['overall_score']}",
            f"Hallucination Risk: {analysis['hallucination_risk']}",
            "",
            "Metric Scores:"
        ]

        for metric, score in analysis[
            "metric_scores"
        ].items():

            lines.append(
                f"- {metric}: {score}"
            )

        lines.extend(
            [
                "",
                f"Strongest Area: "
                f"{analysis['strongest_area']}",
                f"Weakest Area: "
                f"{analysis['weakest_area']}",
                "",
                "Recommendations:"
            ]
        )

        for recommendation in analysis[
            "recommendations"
        ]:

            lines.append(
                f"- {recommendation}"
            )

        return "\n".join(lines)