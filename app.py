from flask import Flask, render_template, request, jsonify
import pandas as pd
import faiss
import os
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

gemini_model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

app = Flask(__name__)

df = pd.read_csv("college_website_data.csv")

data = []

for _, row in df.iterrows():
    data.append({
        "title": row["title"],
        "content": row["content"],
        "url": row["url"]
    })

documents = []

for item in data:
    documents.append(
        f"""
Title: {item['title']}
Content: {item['content']}
URL: {item['url']}
"""
    )

embed_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

embeddings = embed_model.encode(
    documents,
    batch_size=32,
    show_progress_bar=True,
    convert_to_numpy=True
).astype("float32")

faiss.normalize_L2(embeddings)

dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)

index.add(embeddings)


def retrieve_context(query, k=5):

    query_embedding = embed_model.encode(
        [query],
        convert_to_numpy=True
    ).astype("float32")

    faiss.normalize_L2(query_embedding)

    distances, indices = index.search(
        query_embedding,
        k
    )

    retrieved_docs = []

    for idx in indices[0]:
        if idx < len(documents):
            retrieved_docs.append(
                documents[idx]
            )

    return "\n\n".join(retrieved_docs)


def generate_answer(query):

    context = retrieve_context(query)

    prompt = f"""
You are an AI assistant for a college website.

User Question:
{query}

Retrieved Website Data:
{context}

Instructions:
1. Answer ONLY using the retrieved information.
2. Do not hallucinate.
3. If information is unavailable, say:
"The requested information was not found in the website data."
4. Include URLs when available.
5. Give structured responses.

Answer:
"""

    response = gemini_model.generate_content(prompt)

    return response.text


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    query = data["message"]

    answer = generate_answer(query)

    return jsonify({
        "response": answer
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )