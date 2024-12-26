import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from elasticsearch import Elasticsearch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)
CORS(app)

# Đặt các biến môi trường trực tiếp trong mã
os.environ["ELASTICSEARCH_HOST"] = "https://d93143eb81aa40ae9b186eeee81a1adc.us-central1.gcp.cloud.es.io"
os.environ["ELASTICSEARCH_USER"] = "elastic"
os.environ["ELASTICSEARCH_PASSWORD"] = "YgZyYW1VLobvLzpWvVup0ZwE"

# Sử dụng các biến môi trường để khởi tạo Elasticsearch client
es = Elasticsearch(
    hosts=[os.getenv("ELASTICSEARCH_HOST")],
    http_auth=(os.getenv("ELASTICSEARCH_USER"), os.getenv("ELASTICSEARCH_PASSWORD"))
)
vectorizer = TfidfVectorizer()
reduced_matrix = np.load('reduced_matrix.npy')

def find_similar_sentences(input_sentence, vectorizer, reduced_matrix):
    input_vec = vectorizer.transform([input_sentence])
    similarities = cosine_similarity(input_vec, reduced_matrix)
    similar_indices = similarities.argsort()[0][-5:][::-1]
    return similar_indices

def get_sentence_by_index(output, idx):
    return output[idx]

def similar(input_sentence, sentence):
    input_vec = vectorizer.transform([input_sentence])
    sentence_vec = vectorizer.transform([sentence])
    return cosine_similarity(input_vec, sentence_vec)[0][0]

@app.route('/search', methods=['POST'])
def search_sentence():
    input_sentence = request.json['text']
    similar_indices = find_similar_sentences(input_sentence, vectorizer, reduced_matrix)
    
    found = False
    results = []
    for idx in similar_indices:
        sentence = get_sentence_by_index(output, idx)
        similarity = similar(input_sentence, sentence)
        if similarity >= 0.8:
            results.append({"sentence": sentence, "similarity": similarity})
            found = True

    if found:
        return jsonify({"input_sentence": input_sentence, "results": results})
    else:
        return jsonify({"input_sentence": input_sentence, "results": "No similar sentence found."})

if __name__ == '__main__':
    app.run(debug=True)