import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from elasticsearch import Elasticsearch

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

def find_similar_sentences(input_sentence):
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
        score = hit['_score']
        results.append({"sentence": sentence, "score": score})
    return results

@app.route('/search', methods=['POST'])
def search_sentence():
    try:
        input_sentence = request.json['text']
        print(f"Received input: {input_sentence}")
        results = find_similar_sentences(input_sentence)
        
        # Lọc các câu có điểm số >= 0.8 (tùy chỉnh ngưỡng này theo yêu cầu của bạn)
        filtered_results = [result for result in results if result['score'] >= 0.8]
        print(f"Filtered results: {filtered_results}")

        if filtered_results:
            return jsonify({"input_sentence": input_sentence, "results": filtered_results})
        else:
            return jsonify({"input_sentence": input_sentence, "results": "No similar sentence found."})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
