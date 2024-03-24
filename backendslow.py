from google.cloud import storage
from pymongo import MongoClient
from textblob import TextBlob
import whisper
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from openai import OpenAI
import cv2
from deepface import DeepFace
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer

# Import OpenAI credentials from credentials.py
from test_functions.credentials import OPENAI_API_KEY, uri

api_key = OPENAI_API_KEY
client_ai = OpenAI(api_key=api_key)

client = MongoClient(uri)

db = client["UncommonHack"]
collection = db["User_Reports"]

storage_client = storage.Client()

dataset = load_dataset("Amod/mental_health_counseling_conversations")
corpus = [example['Context'] for example in dataset['train']]
model = whisper.load_model('base')


def analyze_sentiment(text):
    prompt_text = (
        "Analyze the following text to determine the person's emotional state and possible reasons for these emotions. "
        "Please write the response as you are talking to the person directly and give them an analysis of their emotional state. "
        "Make sure the response is 3-4 sentences.\n\n"
        f"Text: \"{text}\""
    )

    response = client_ai.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt_text,
        max_tokens=130
    )

    return response.choices[0].text.strip()

@functions_framework.cloud_event
def hello_gcs(cloud_event):
    data = cloud_event.data
    
    bucket_name = data["bucket"]
    file_name = data["name"]


    print(f"Inserted document with _id: {result.inserted_id}")
    print("DONE")


if __name__ == "__main__":
    hello_gcs(None)
