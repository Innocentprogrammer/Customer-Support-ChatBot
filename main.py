import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import tkinter as tk
from tkinter import scrolledtext

# Download NLTK data if not already downloaded
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Load FAQ from JSON file
with open('faq.json', 'r') as file:
    FAQ = json.load(file)

# Function to preprocess text
def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [word for word in tokens if word not in string.punctuation]
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return tokens

# Preprocess the FAQ questions once
processed_FAQ = {question: preprocess_text(question) for question in FAQ}

# Function to find the best match for the user query
def find_best_match(user_query):
    processed_query = preprocess_text(user_query)
    max_overlap = 0
    best_match = None

    for question, processed_question in processed_FAQ.items():
        overlap = len(set(processed_query) & set(processed_question))
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = question

    if best_match:
        return FAQ[best_match]
    else:
        return "I'm sorry, I don't have an answer for that. Can you please provide more details?"

# Function to send message
def send_message():
    user_input = entry.get()
    if user_input.lower() in ['exit', 'quit', 'bye']:
        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, "Chatbot: Thank you for visiting! Have a great day!\n")
        chat_log.config(state=tk.DISABLED)
        root.after(2000, root.destroy)
    else:
        response = find_best_match(user_input)
        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, f"You: {user_input}\n")
        chat_log.insert(tk.END, f"Chatbot: {response}\n")
        chat_log.config(state=tk.DISABLED)
        entry.delete(0, tk.END)

# Create GUI using Tkinter
root = tk.Tk()
root.title("Business Chatbot")

# Chat log frame
frame = tk.Frame(root)
scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Chat log label
chat_log_label = tk.Label(frame, text="Chat Log")
chat_log_label.pack(pady=10)

# Chat log
chat_log = scrolledtext.ScrolledText(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, width=50, height=20)
chat_log.pack(side=tk.LEFT, fill=tk.BOTH)
scrollbar.config(command=chat_log.yview)
chat_log.config(state=tk.DISABLED)  # Make chat log uneditable
frame.pack(pady=10)

# User input
entry_label = tk.Label(root, text="Enter your message below:")
entry_label.pack()

# User input field
entry = tk.Entry(root, width=50)
entry.pack(pady=10)

# Send button
send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack()

# Start the chatbot
root.mainloop()
