# 🤖 Chatbot with Sentiment Analysis (Python + TextBlob)

This is a simple rule-based chatbot implemented in Python that uses keyword-based intent recognition and fallback sentiment analysis via **TextBlob**. If no keywords match, it analyzes the emotional tone of the user's message to generate an empathetic response.

---

## 📌 Features

- ✅ **Intent Matching**: Recognizes user intents based on predefined keyword patterns (e.g., asking about store hours or refund policy).
- ✅ **Sentiment-Based Response**: Analyzes positive or negative sentiments when no keyword matches are found.
- ✅ **Text-Based Interface**: Interacts with users via the command line.
- ✅ **Expandable**: Easy to add more intents and responses.

---

## 🛠 Technologies Used

- **Python 3.6+**
- [TextBlob](https://textblob.readthedocs.io/en/dev/) — for sentiment analysis

---

## 📁 Project Structure

```
chatbot-with-textblob/
├── chatbot.py         # Main chatbot script
├── README.md          # Project documentation
└── requirements.txt   # List of Python dependencies
```

---

## 🚀 How to Run This Project

### 1. Clone the Repository

```bash
git clone https://github.com/Broken-Frog/ChatBoat_textbolb_python.git
cd ChatBoat_textbolb_python
```

### 2. (Optional) Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate    # On Linux/macOS
venv\Scripts\activate     # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
python -m textblob.download_corpora
```

### 4. Run the Chatbot

```bash
python chatbot.py
```

---

## 💬 Sample Conversation

```
You: What time do you open?
Chatbot: The shop will be open from 9am to 9pm from Sunday to Saturday.

You: I bought a product and it is broken. I am so sad.
Chatbot: I'm sorry. How can I help?

You: I'm feeling great today!
Chatbot: Good to hear that!
```

---

## 📦 Add More Intents

To expand the bot's capability, edit the `intents` dictionary in `chatbot.py`:

```python
"greeting": {
    "keywords": ["hello", "hi", "hey"],
    "response": "Hello! How can I assist you today?"
}
```

---

## ✅ To-Do / Future Improvements

- Add logging of chat history
- Create a GUI version (Tkinter / PyQt)
- Add Telegram or Discord integration
- Upgrade NLP using spaCy or transformers

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙋‍♂️ Author

**Your Name**  
GitHub: [@yourusername](https://github.com/yourusername)
