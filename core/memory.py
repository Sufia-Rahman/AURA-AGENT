import json
import os


class Memory:

    def __init__(self):
        self.memory_file = "aura_memory.json"
        self.data = {
            "name": None,
            "history": []
        }

        self.load()

    def load(self):
        if os.path.exists(self.memory_file):
            try:
                with open(
                    self.memory_file,
                    "r",
                    encoding="utf-8"
                ) as file:
                    saved_data = json.load(file)

                if isinstance(saved_data, dict):
                    self.data.update(saved_data)

            except Exception:
                pass

    def save(self):
        try:
            with open(
                self.memory_file,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    self.data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception:
            pass

    def get_name(self):
        return self.data.get("name")

    def set_name(self, name):
        self.data["name"] = name
        self.save()

    def add_history(self, user_input, response):
        self.data["history"].append({
            "user": user_input,
            "aura": response
        })

        self.save()

    def get_history(self):
        return self.data.get("history", [])

    def summary(self):
        name = self.get_name()

        if name:
            return f"I remember that your name is {name}."

        return "I don't have any personal information about you yet."