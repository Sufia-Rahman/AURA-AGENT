import datetime
import json
import os
import re


class AURA:
    """
    AURA — Autonomous Universal Research & Reasoning Agent

    Current capabilities:
    - Conversation
    - Persistent memory
    - User name memory
    - Personal facts memory
    - Memory retrieval
    - Time/date awareness
    - Calculator
    - Basic conversational responses
    """

    def __init__(self):
        self.memory_file = "aura_memory.json"
        self.memory = []
        self.user_name = None

        self.load_memory()

        # Recover saved name
        for item in self.memory:
            if item.get("type") == "user_name":
                self.user_name = item.get("value")

    # =========================================================
    # MEMORY SYSTEM
    # =========================================================

    def load_memory(self):
        """Load AURA's permanent memory."""

        if not os.path.exists(self.memory_file):
            self.memory = []
            return

        try:
            with open(
                self.memory_file,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            if isinstance(data, list):
                self.memory = data
            else:
                self.memory = []

        except (json.JSONDecodeError, OSError):
            self.memory = []

    def save_memory(self):
        """Save AURA's memory permanently."""

        try:
            with open(
                self.memory_file,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    self.memory,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

        except OSError:
            print("AURA: I could not save my memory.")

    # =========================================================
    # CONVERSATION MEMORY
    # =========================================================

    def remember(self, user_input, response):
        """Save a conversation."""

        self.memory.append({
            "type": "conversation",
            "user": user_input,
            "response": response,
            "time": datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        })

        self.save_memory()

    # =========================================================
    # USER NAME
    # =========================================================

    def remember_name(self, name):
        """Remember user's name."""

        self.user_name = name

        # Remove previous saved names
        self.memory = [
            item
            for item in self.memory
            if item.get("type") != "user_name"
        ]

        self.memory.append({
            "type": "user_name",
            "value": name,
            "time": datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        })

        self.save_memory()

    def get_user_name(self):
        """Return user's remembered name."""

        return self.user_name

    # =========================================================
    # PERSONAL FACT MEMORY
    # =========================================================

    def remember_fact(self, key, value):
        """Remember a personal fact."""

        # Remove previous value for same key
        self.memory = [
            item
            for item in self.memory
            if not (
                item.get("type") == "personal_fact"
                and item.get("key") == key
            )
        ]

        self.memory.append({
            "type": "personal_fact",
            "key": key,
            "value": value,
            "time": datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        })

        self.save_memory()

    def get_personal_facts(self):
        """Return all saved personal facts."""

        facts = []

        for item in self.memory:
            if item.get("type") == "personal_fact":
                facts.append(item)

        return facts

    # =========================================================
    # MEMORY SEARCH
    # =========================================================

    def search_memory(self, keyword):
        """Search saved conversations and facts."""

        keyword = keyword.lower().strip()
        results = []

        for item in self.memory:

            if item.get("type") == "conversation":

                user_text = item.get("user", "").lower()
                aura_text = item.get("response", "").lower()

                if (
                    keyword in user_text
                    or keyword in aura_text
                ):
                    results.append(item)

            elif item.get("type") == "personal_fact":

                key = str(item.get("key", "")).lower()
                value = str(item.get("value", "")).lower()

                if keyword in key or keyword in value:
                    results.append(item)

        return results

    # =========================================================
    # MEMORY SUMMARY
    # =========================================================

    def memory_summary(self):
        """Create a readable summary of AURA's memory."""

        parts = []

        if self.user_name:
            parts.append(
                f"Your name is {self.user_name}."
            )

        facts = self.get_personal_facts()

        for fact in facts:

            key = fact.get("key")
            value = fact.get("value")

            parts.append(
                f"You told me that your {key} is {value}."
            )

        if not parts:
            return (
                "I don't have any personal information "
                "about you yet."
            )

        return " ".join(parts)

    # =========================================================
    # CALCULATOR
    # =========================================================

    def calculate(self, expression):
        """Calculate a basic mathematical expression."""

        expression = expression.strip()

        # Only allow mathematical characters
        if not re.fullmatch(
            r"[0-9+\-*/().%\s]+",
            expression
        ):
            return None

        try:
            result = eval(
                expression,
                {"__builtins__": {}},
                {}
            )

            return result

        except Exception:
            return None

    # =========================================================
    # MAIN THINKING SYSTEM
    # =========================================================

    def think(self, user_input):

        text = user_input.strip()
        lower = text.lower()

        # =====================================================
        # EMPTY INPUT
        # =====================================================

        if not text:

            return "Please say something."

        # =====================================================
        # NAME
        # =====================================================

        if lower.startswith("my name is "):

            name = text[11:].strip()

            if name:

                self.remember_name(name)

                response = (
                    f"Nice to meet you, {name}. "
                    "I'll remember your name."
                )

                self.remember(user_input, response)

                return response

        # =====================================================
        # ASK NAME
        # =====================================================

        if (
            "what is my name" in lower
            or "what's my name" in lower
            or "do you know my name" in lower
            or "do you remember my name" in lower
        ):

            if self.user_name:

                response = (
                    f"Your name is {self.user_name}."
                )

            else:

                response = (
                    "I don't know your name yet. "
                    "Tell me by saying: My name is ..."
                )

            self.remember(user_input, response)

            return response

        # =====================================================
        # PERSONAL FACTS
        # =====================================================

        if lower.startswith("i am "):

            value = text[5:].strip()

            if value:

                self.remember_fact(
                    "identity",
                    value
                )

                response = (
                    f"Got it. I'll remember that you are {value}."
                )

                self.remember(user_input, response)

                return response

        if lower.startswith("i'm "):

            value = text[4:].strip()

            if value:

                self.remember_fact(
                    "identity",
                    value
                )

                response = (
                    f"Got it. I'll remember that you are {value}."
                )

                self.remember(user_input, response)

                return response

        # =====================================================
        # LIKES
        # =====================================================

        if lower.startswith("i like "):

            value = text[7:].strip()

            if value:

                self.remember_fact(
                    "favorite/like",
                    value
                )

                response = (
                    f"I'll remember that you like {value}."
                )

                self.remember(user_input, response)

                return response

        # =====================================================
        # DISLIKES
        # =====================================================

        if lower.startswith("i don't like "):

            value = text[13:].strip()

            if value:

                self.remember_fact(
                    "dislike",
                    value
                )

                response = (
                    f"I'll remember that you don't like {value}."
                )

                self.remember(user_input, response)

                return response

        # =====================================================
        # MEMORY SUMMARY
        # =====================================================

        if (
            "what do you remember about me" in lower
            or "what do you remember" in lower
            or "tell me what you remember" in lower
        ):

            response = self.memory_summary()

            self.remember(user_input, response)

            return response

        # =====================================================
        # MEMORY SEARCH
        # =====================================================

        if lower.startswith("do you remember "):

            keyword = text[16:].strip()

            if keyword:

                results = self.search_memory(keyword)

                if results:

                    response = (
                        f"Yes. I found {len(results)} "
                        f"related memory item(s) about {keyword}."
                    )

                else:

                    response = (
                        f"I don't remember anything specifically "
                        f"about {keyword}."
                    )

                self.remember(user_input, response)

                return response

        # =====================================================
        # GREETING
        # =====================================================

        if lower in [
            "hi",
            "hello",
            "hey",
            "hii",
            "helo",
            "good morning",
            "good afternoon",
            "good evening"
        ]:

            if self.user_name:

                response = (
                    f"Hello {self.user_name}! "
                    "I am AURA. How can I help you?"
                )

            else:

                response = (
                    "Hello! I am AURA. "
                    "How can I help you?"
                )

            self.remember(user_input, response)

            return response

        # =====================================================
        # THANK YOU
        # =====================================================

        if lower in [
            "thank you",
            "thanks",
            "thank u",
            "thankyou"
        ]:

            response = (
                "You're welcome! "
                "I'm always happy to help you."
            )

            self.remember(user_input, response)

            return response

        # =====================================================
        # WHO ARE YOU
        # =====================================================

        if (
            "who are you" in lower
            or "what are you" in lower
        ):

            response = (
                "I am AURA — Autonomous Universal "
                "Research & Reasoning Agent."
            )

            self.remember(user_input, response)

            return response

        # =====================================================
        # WHAT CAN YOU DO
        # =====================================================

        if "what can you do" in lower:

            response = (
                "I can remember information, "
                "maintain conversations, remember "
                "personal facts, search my memory, "
                "perform calculations, and tell you "
                "the current time and date."
            )

            self.remember(user_input, response)

            return response

        # =====================================================
        # TIME
        # =====================================================

        if (
            "what time" in lower
            or lower == "time"
            or "current time" in lower
        ):

            current_time = datetime.datetime.now().strftime(
                "%I:%M %p"
            )

            response = (
                f"The current time is {current_time}."
            )

            self.remember(user_input, response)

            return response

        # =====================================================
        # DATE
        # =====================================================

        if (
            "what is today's date" in lower
            or "what date is it" in lower
            or lower == "date"
            or "today's date" in lower
        ):

            current_date = datetime.datetime.now().strftime(
                "%d %B %Y"
            )

            response = (
                f"Today is {current_date}."
            )

            self.remember(user_input, response)

            return response

        # =====================================================
        # HOW ARE YOU
        # =====================================================

        if (
            "how are you" in lower
            or "how r u" in lower
            or "how are u" in lower
        ):

            response = (
                "I am good, thank you. "
                "I am ready to work with you."
            )

            self.remember(user_input, response)

            return response

        # =====================================================
        # CALCULATOR
        # =====================================================

        if lower.startswith("calculate "):

            expression = text[10:].strip()

            result = self.calculate(expression)

            if result is not None:

                response = (
                    f"The answer is {result}."
                )

            else:

                response = (
                    "Sorry, I couldn't calculate that."
                )

            self.remember(user_input, response)

            return response

        # =====================================================
        # DIRECT MATH
        # =====================================================

        if re.fullmatch(
            r"[0-9+\-*/().%\s]+",
            text
        ):

            result = self.calculate(text)

            if result is not None:

                response = (
                    f"The answer is {result}."
                )

                self.remember(user_input, response)

                return response

        # =====================================================
        # POSITIVE RESPONSE
        # =====================================================

        if lower in [
            "good",
            "great",
            "nice",
            "okay",
            "ok",
            "fine"
        ]:

            response = (
                "That's good to hear. "
                "What would you like to do next?"
            )

            self.remember(user_input, response)

            return response

        # =====================================================
        # EXIT
        # =====================================================

        if lower in [
            "exit",
            "quit",
            "bye"
        ]:

            response = (
                "Goodbye! See you again."
            )

            self.remember(user_input, response)

            return response

        # =====================================================
        # DEFAULT
        # =====================================================

        response = (
            f"I understand you said: {text}"
        )

        self.remember(user_input, response)

        return response


# =============================================================
# AURA STARTUP
# =============================================================

if __name__ == "__main__":

    aura = AURA()

    print("=" * 65)
    print(
        "AURA — Autonomous Universal Research & Reasoning Agent"
    )
    print("=" * 65)

    if aura.user_name:

        print(
            f"AURA: Welcome back, {aura.user_name}!"
        )

    else:

        print(
            "AURA: Hello! I am AURA."
        )

    print(
        "AURA: Type 'exit' to quit."
    )

    print()

    # =========================================================
    # MAIN LOOP
    # =========================================================

    while True:

        user_input = input("You: ")

        response = aura.think(user_input)

        print("AURA:", response)

        if user_input.strip().lower() in [
            "exit",
            "quit",
            "bye"
        ]:

            break