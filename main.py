import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string

# Download NLTK data if not already downloaded
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Load FAQ from JSON file
with open('faq.json', 'r') as file:
    FAQ = json.load(file)

# Define a function to preprocess text data
def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [word for word in tokens if word not in string.punctuation]
    tokens = [word for word in tokens if word not in stopwords.words('english')]
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return tokens

# Preprocess the FAQ questions once
processed_FAQ = {question: preprocess_text(question) for question in FAQ}

# Define a function to find the best match for the user query
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

# Define the chatbot function
def chatbot():
    print("Welcome to the Business Chatbot! How can I assist you today?")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Chatbot: Thank you for visiting! Have a great day!")
            break
        response = find_best_match(user_input)
        print(f"Chatbot: {response}")

# Start the chatbot
if __name__ == "__main__":
    chatbot()
