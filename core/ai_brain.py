from openai import OpenAI

from .config import API_KEY
from .evidence import EvidenceExtractor


class AIBrain:

    def __init__(self):

        if not API_KEY:

            raise ValueError(
                "API_KEY is missing. Add API_KEY to your .env file."
            )

        self.client = OpenAI(
            api_key=API_KEY
        )

        self.model = "gpt-5.6-luna"

        self.evidence = EvidenceExtractor()

    def respond(
        self,
        user_input,
        user_name=None,
        memory_summary=None,
        tools=None,
        plan=None,
        research_context=None,
        improvement_context=None,
        long_term_context=None
    ):

        text = user_input.strip()

        if not text:

            return {
                "answer": "I'm listening. Tell me what you need.",
                "sources": []
            }

        name_text = user_name or "Unknown"

        memory_text = (
            "No relevant memory available."
        )

        if memory_summary:

            try:

                memory_text = memory_summary()

            except TypeError:

                memory_text = str(
                    memory_summary
                )

        plan_text = (
            str(plan)
            if plan
            else "No execution plan available."
        )

        research_text = (
            research_context
            if research_context
            else "No external research was performed."
        )

        improvement_text = (
            improvement_context
            if improvement_context
            else (
                "No previous improvement strategies "
                "are available."
            )
        )

        long_term_text = (
            long_term_context
            if long_term_context
            else (
                "No relevant long-term memories "
                "are available."
            )
        )

        prompt = f"""
You are AURA — Autonomous Universal Research & Reasoning Agent.

Your job is to understand goals, reason over information,
use appropriate tools, retrieve private knowledge,
use long-term memory, learn from previous performance,
and produce reliable answers.

User name:
{name_text}

Known short-term memory:
{memory_text}

Relevant long-term memory:
{long_term_text}

Execution plan:
{plan_text}

External research findings:
{research_text}

Previous improvement strategies:
{improvement_text}

User request:
{text}

Instructions:

- Follow the execution plan.
- Use relevant long-term memories when they help answer
  the current request.
- Do not treat memory as automatically correct.
- Use memory as contextual information.
- Apply relevant improvement strategies when useful.
- Do not blindly follow irrelevant strategies.
- Use tools when they are useful.
- If the user's question requires information from AURA's
  private documents, use the search_knowledge tool.
- Treat private knowledge results as document evidence.
- When using private knowledge, identify the source filename.
- Do not invent unsupported information.
- Clearly distinguish evidence from reasoning.
- If private knowledge does not contain the answer,
  say so.
- If external research is provided, synthesize it.
- Do not claim web research was performed unless it was.
- Prefer reliable and authoritative information.
- Give a clear, structured final answer.
"""

        conversation = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        tool_definitions = []

        if tools:

            tool_definitions.extend(
                tools.definitions()
            )

        tool_definitions.append(
            {
                "type": "web_search"
            }
        )

        collected_sources = []

        for _ in range(8):

            response = self.client.responses.create(
                model=self.model,
                input=conversation,
                tools=tool_definitions
            )

            conversation.extend(
                response.output
            )

            sources = self.evidence.extract(
                response
            )

            existing_urls = {
                source["url"]
                for source in collected_sources
            }

            for source in sources:

                if source["url"] not in existing_urls:

                    collected_sources.append(
                        source
                    )

                    existing_urls.add(
                        source["url"]
                    )

            tool_calls = [
                item
                for item in response.output
                if item.type == "function_call"
            ]

            if not tool_calls:

                return {
                    "answer": response.output_text.strip(),
                    "sources": collected_sources
                }

            for tool_call in tool_calls:

                if not tools:

                    continue

                result = tools.execute(
                    tool_call.name,
                    tool_call.arguments
                )

                conversation.append(
                    {
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": str(result)
                    }
                )

        return {
            "answer": (
                "I could not complete the task within "
                "the allowed reasoning steps."
            ),
            "sources": collected_sources
        }