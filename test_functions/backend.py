from google.cloud import storage
from pymongo import MongoClient
import whisper
from textblob import TextBlob
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from openai import OpenAI
from credentials import OPENAI_API_KEY, uri

client_ai = OpenAI(OPENAI_API_KEY)
import cv2
from deepface import DeepFace
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer

client = MongoClient(uri)

db = client["user_info"]
collection = db["videoanalyses"]

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

def hello_gcs():
    #data = cloud_event.data
    #bucket_name = data["bucket"]
    #file_name = data["name"]

    #bucket = storage_client.bucket(bucket_name)
    #blob = bucket.blob("/Users/siddsatish/Desktop/finer_vid_short.wav")
    temp_video_path = "/Users/siddsatish/Desktop/Screen Recording 2024-01-28 at 11.17.48 AM.mov"
    #blob.download_to_filename("/Users/siddsatish/Desktop/finer_vid_short.wav")
    result = model.transcribe(temp_video_path, fp16=False)

    transcribed_text = result["text"]
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    tokens = word_tokenize(transcribed_text)
    tokens = [token.lower() for token in tokens]
    tokens = [token for token in tokens if token.isalpha()]
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    lemmatizer = WordNetLemmatizer()
    lemmatized = [lemmatizer.lemmatize(token) for token in tokens]

    preprocessed_text = ' '.join(lemmatized)
    print(preprocessed_text)
    corpus.append(transcribed_text)
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray()[-1]
    word_scores = {word: score for word, score in zip(feature_names, tfidf_scores)}
    sorted_word_scores = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)

    sentiment = analyze_sentiment(preprocessed_text)
    print(sentiment)

    cap = cv2.VideoCapture(temp_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    emotions_dict = {}
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        for i in range(int(fps) - 1):
            cap.read()  # Read and discard

        try:
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            try:
                emotions_dict[result[0]['dominant_emotion']] += 1
            except KeyError:
                emotions_dict[result[0]['dominant_emotion']] = 1
            print(result[0]['dominant_emotion'])
        except Exception as e:
            print("Error in emotion detection", e)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print(emotions_dict)
    cap.release()
    cv2.destroyAllWindows()

    # document = {
    #     "event_id": cloud_event["id"],
    #     "event_type": cloud_event["type"],
    #     "bucket": bucket_name,
    #     "file": file_name,
    #     "created": data["timeCreated"],
    #     "updated": data["updated"],
    #     "sentiment": sentiment,
    #     "dominant_emotion": max(emotions_dict, key=emotions_dict.get),
    #
    # }

    # result = collection.insert_one(document)
    # print(f"Inserted document with _id: {result.inserted_id}")
    print("DONE")

hello_gcs()

if __name__ == "__main__":
    hello_gcs(None)
