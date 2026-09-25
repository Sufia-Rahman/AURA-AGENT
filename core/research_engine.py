import json
from urllib.parse import urlparse

from .evidence import EvidenceScorer


class ResearchEngine:

    def __init__(self, client, model):
        self.client = client
        self.model = model

    def _extract_sources(self, response):

        sources = []
        seen = set()

        for item in response.output:

            annotations = getattr(
                item,
                "annotations",
                None
            )

            if not annotations:
                continue

            for annotation in annotations:

                url = getattr(
                    annotation,
                    "url",
                    None
                )

                title = getattr(
                    annotation,
                    "title",
                    None
                )

                if not url or url in seen:
                    continue

                seen.add(url)

                parsed = urlparse(url)

                sources.append(
                    {
                        "title": title or "Untitled source",
                        "url": url,
                        "domain": parsed.netloc
                    }
                )

        return sources

    def research(self, goal, plan):

        steps = plan.get(
            "steps",
            []
        )

        findings = []

        for step in steps[:5]:

            action = step.get(
                "action",
                ""
            )

            purpose = step.get(
                "purpose",
                ""
            )

            research_prompt = f"""
You are AURA's autonomous research engine.

Overall goal:
{goal}

Research step:
{action}

Purpose:
{purpose}

Research the step using current web information.

Requirements:

- Prefer primary and authoritative sources.
- Compare multiple sources when useful.
- Separate facts from interpretation.
- Identify conflicting information.
- Do not invent missing information.
- Support important claims with evidence.
- Assess the reliability of the information found.

Return:

1. Key findings
2. Important evidence
3. Conflicting or uncertain information
4. Reliability assessment
5. Source-supported conclusion
"""

            response = self.client.responses.create(
                model=self.model,
                input=research_prompt,
                tools=[
                    {
                        "type": "web_search"
                    }
                ]
            )

            raw_sources = self._extract_sources(
                response
            )

            sources = EvidenceScorer.score_sources(
                raw_sources
            )

            findings.append(
                {
                    "step": step.get("step"),
                    "action": action,
                    "purpose": purpose,
                    "findings": response.output_text.strip(),
                    "sources": sources
                }
            )

        return findings

    @staticmethod
    def format_findings(findings):

        if not findings:
            return "No research findings available."

        sections = []

        for finding in findings:

            source_lines = []

            for source in finding.get(
                "sources",
                []
            ):

                source_lines.append(
                    f"- {source['title']} "
                    f"({source['domain']}) "
                    f"[Evidence Score: "
                    f"{source['evidence_score']}/100]: "
                    f"{source['url']}"
                )

            sources_text = (
                "\n".join(source_lines)
                if source_lines
                else "No source metadata available."
            )

            sections.append(
                f"""
Research Step {finding['step']}

Action:
{finding['action']}

Purpose:
{finding['purpose']}

Findings:
{finding['findings']}

Sources:
{sources_text}
"""
            )

        return "\n".join(
            sections
        )

    def validate_research(
        self,
        goal,
        findings
    ):

        if not findings:

            return {
                "confidence": 0,
                "assessment": (
                    "No research was available "
                    "for validation."
                )
            }

        research_context = (
            self.format_findings(
                findings
            )
        )

        validation_prompt = f"""
You are AURA's research validation module.

Research goal:
{goal}

Research findings:
{research_context}

Evaluate the reliability of this research.

Consider:

- quality of sources
- evidence scores
- agreement between sources
- supporting evidence
- conflicting information
- uncertainty
- completeness

Return a JSON object with exactly:

{{
    "confidence": 0,
    "assessment": "brief explanation"
}}

Confidence must be an integer from 0 to 100.

Do not invent evidence.
"""

        response = self.client.responses.create(
            model=self.model,
            input=validation_prompt
        )

        text = response.output_text.strip()

        try:

            result = json.loads(
                text
            )

            confidence = int(
                result.get(
                    "confidence",
                    0
                )
            )

            confidence = max(
                0,
                min(
                    confidence,
                    100
                )
            )

            return {
                "confidence": confidence,
                "assessment": result.get(
                    "assessment",
                    "No assessment available."
                )
            }

        except (
            json.JSONDecodeError,
            ValueError,
            TypeError
        ):

            return {
                "confidence": 0,
                "assessment": (
                    "Research validation "
                    "could not be parsed."
                )
            }

    def synthesize(
        self,
        goal,
        findings,
        validation=None
    ):

        if not findings:

            return {
                "answer": (
                    "No research findings are available."
                ),
                "sources": []
            }

        research_context = (
            self.format_findings(
                findings
            )
        )

        validation_context = (
            str(validation)
            if validation
            else "No validation available."
        )

        synthesis_prompt = f"""
You are AURA's research synthesis module.

Overall research goal:
{goal}

Collected research:
{research_context}

Research validation:
{validation_context}

Synthesize the research into one reliable answer.

Instructions:

- Combine evidence across research steps.
- Prefer stronger and more authoritative evidence.
- Consider evidence scores.
- Do not invent facts.
- Resolve contradictions only when evidence supports doing so.
- Clearly mention uncertainty.
- Consider the research confidence assessment.
- Distinguish facts from reasoning.
- Give a clear structured answer.
"""

        response = self.client.responses.create(
            model=self.model,
            input=synthesis_prompt
        )

        sources = []

        for finding in findings:

            for source in finding.get(
                "sources",
                []
            ):

                if source not in sources:
                    sources.append(
                        source
                    )

        sources.sort(
            key=lambda item: item.get(
                "evidence_score",
                0
            ),
            reverse=True
        )

        return {
            "answer": response.output_text.strip(),
            "sources": sources
        }