from urllib.parse import urlparse


class EvidenceExtractor:

    @staticmethod
    def extract(response):

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


class EvidenceScorer:

    TRUSTED_DOMAINS = [
        ".gov",
        ".edu",
        "who.int",
        "nature.com",
        "arxiv.org",
        "openai.com"
    ]

    @classmethod
    def score_sources(cls, sources):

        scored = []

        for source in sources:

            domain = source.get(
                "domain",
                ""
            ).lower()

            score = 50

            for trusted_domain in cls.TRUSTED_DOMAINS:

                if (
                    domain == trusted_domain
                    or domain.endswith(trusted_domain)
                    or trusted_domain in domain
                ):
                    score += 30
                    break

            score = min(
                score,
                100
            )

            scored.append(
                {
                    **source,
                    "evidence_score": score
                }
            )

        scored.sort(
            key=lambda item: item["evidence_score"],
            reverse=True
        )

        return scored