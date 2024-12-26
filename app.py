import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from elasticsearch import Elasticsearch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

def find_similar_sentences(input_sentence, vectorizer):
    input_vec = vectorizer.transform([input_sentence])
    # Tìm kiếm trong Elasticsearch
    response = es.search(
        index="sentences",
        body={
            "query": {
                "match": {
                    "sentence": input_sentence
                }
            }
        }
    )
    # Lấy các câu và tính toán độ tương đồng
    results = []
    for hit in response['hits']['hits']:
        sentence = hit['_source']['sentence']
        sentence_vec = vectorizer.transform([sentence])
        similarity = cosine_similarity(input_vec, sentence_vec)[0][0]
        results.append({"sentence": sentence, "similarity": similarity})
    return results

@app.route('/search', methods=['POST'])
def search_sentence():
    input_sentence = request.json['text']
    results = find_similar_sentences(input_sentence, vectorizer)
    
    # Lọc các câu có độ tương đồng >= 0.8
    filtered_results = [result for result in results if result['similarity'] >= 0.8]

    if filtered_results:
        return jsonify({"input_sentence": input_sentence, "results": filtered_results})
    else:
        return jsonify({"input_sentence": input_sentence, "results": "No similar sentence found."})

if __name__ == '__main__':
    app.run(debug=True)
