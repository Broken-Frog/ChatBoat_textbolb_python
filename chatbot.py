from textblob import TextBlob

# Define intents and their corresponding responses based on keywords
intents = {
    "hours": {
        "keywords": ["hour", "time", "open", "close"],
        "response": "The shop will be open from 9am to 9pm from Sunday to Saturday."
    },
    "return": {
        "keywords": ["return", "refund", "money back"],
        "response": "To get a refund, I will connect you to a live agent."
    }
}

def get_response(message):
    message = message.lower()
    for intent in intents.values():
        if any(keyword in message for keyword in intent["keywords"]):
            return intent["response"]
    sentiment = TextBlob(message).sentiment.polarity
    return "Good to hear that!" if sentiment > 0 else "I'm sorry. How can I help?"

def chat():
    print("Hello! How can I help you?")
    while (user_message := input("You: ").strip().lower()) not in ["exit", "quit", "bye"]:
        print(f"Chatbot: {get_response(user_message)}")
    print("Chatbot: Thanks for chatting with me. Have a great day :)")

if __name__ == "__main__":
    chat()
