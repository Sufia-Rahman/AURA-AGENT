from core.assistant import AURA

print("AURA Agent is starting...")

aura = AURA()

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("AURA: Goodbye!")
        break

    response = aura.think(user_input)
    print("AURA:", response)
