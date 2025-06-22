import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import ChatOpenAI
from utils import count_tokens, load_vectorstore
from routes import route_question
from api_fetchers import (
    get_weather,
    get_place_info,
    get_wikidata_summary,
    get_celesta_data
)


app = Flask(__name__)

theKey = "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"
client = OpenAI(api_key=theKey)

vs = load_vectorstore(theKey)
retriever = vs.as_retriever()

llm = ChatOpenAI(api_key=theKey, model_name="gpt-3.5-turbo")
compressor = LLMChainExtractor.from_llm(llm)
compressed_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=retriever
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_question = data.get("question", "")
    route = route_question(user_question)

    if route == "weather":
        context = get_weather()
    elif route == "place":
        place = user_question.split("where is")[-1].strip()
        context = get_place_info(place)
    elif route == "wikidata":
        term = user_question.split("about")[-1].strip()
        context = get_wikidata_summary(term)
    elif route == "celesta": 
        import re
        match = re.search(r'celesta.*?for ([\w\s]+) ([a-z]+)(?: (\d{4}(?:, *\d{4})*))?', user_question.lower())
        if match:
            city = match.group(1).strip()
            indicator = match.group(2).strip()
            years = match.group(3)
            years = [int(y) for y in years.split(",") if y] if years else None
        else:
            city = "Prague"
            indicator = "evi"
            years = None
        context = get_celesta_data(city, indicator, years=years, username="ivan", password="Ivan12345")
    else:
        context = "No relevant API fetcher for this question."

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Answer ONLY using the context provided. If unsure, say 'I don’t know based on the current data.'"},
            {"role": "user", "content": f"Question: {user_question}\n\nContext from API fetcher:\n{context}"}
        ]
    )

    reply = response.choices[0].message.content
    return jsonify({"answer": reply, "context": context})


if __name__ == "__main__":
    app.run(debug=True)
