import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import tkinter as tk
from tkinter import scrolledtext
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

# Download NLTK data if not already downloaded
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Load categorized FAQ from JSON file
with open('categorized_faq.json', 'r') as file:
    categorized_FAQ = json.load(file)

# Flatten the FAQ for processing
FAQ = {question: answer for category in categorized_FAQ.values() for question, answer in category.items()}

# Function to call OpenAI API
def ask_openai(question):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ]
    )
    answer = completion.choices[0].message.content
    print(f"Q: {question} | A: {answer}")
    return answer

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
        # Ask OpenAI API if no good match is found
        new_answer = ask_openai(user_query)
        # Update FAQ with the new question and answer
        update_faq(user_query, new_answer)
        return new_answer

# Function to update the FAQ
def update_faq(question, answer):
    # Add to the flat FAQ
    FAQ[question] = answer
    # Find or create the category
    category = "New Questions"
    if category not in categorized_FAQ:
        categorized_FAQ[category] = {}
    categorized_FAQ[category][question] = answer
    # Save to JSON file
    with open('categorized_faq.json', 'w') as file:
        json.dump(categorized_FAQ, file, indent=4)

    # Update processed FAQ
    processed_FAQ[question] = preprocess_text(question)

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

# Function to insert suggested question into entry box
def insert_suggested_question(event):
    selected_question = suggestions_listbox.get(suggestions_listbox.curselection())
    entry.delete(0, tk.END)
    entry.insert(0, selected_question)

# Function to display questions of selected category
def show_questions(event):
    selection = category_listbox.curselection()
    if selection:
        selected_category = category_listbox.get(selection)
        questions = categorized_FAQ[selected_category]
        suggestions_listbox.delete(0, tk.END)
        for question in questions:
            suggestions_listbox.insert(tk.END, question)

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

# Category label
category_label = tk.Label(root, text="Select a Category:")
category_label.pack(pady=10)

# Category listbox
category_listbox = tk.Listbox(root, width=50, height=6)
for category in categorized_FAQ:
    category_listbox.insert(tk.END, category)
category_listbox.pack(pady=10)
category_listbox.bind('<<ListboxSelect>>', show_questions)

# Suggestions label
suggestions_label = tk.Label(root, text="Suggested Questions:")
suggestions_label.pack(pady=10)

# Suggestions listbox
suggestions_listbox = tk.Listbox(root, width=50, height=10)
suggestions_listbox.pack(pady=10)
suggestions_listbox.bind('<<ListboxSelect>>', insert_suggested_question)

# Start the chatbot
root.mainloop()
