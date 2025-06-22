import os
import re
import requests
import string
import json
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools import Tool

load_dotenv("config.env")

GLOBAL_TOOL_LOG = []

CHROMA_DIR = os.path.join(os.getcwd(), "chroma_store")
docs_dir = os.path.join(os.getcwd(), "documents")
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

if os.path.exists(CHROMA_DIR) and os.listdir(CHROMA_DIR):
    vectordb = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
else:
    pdf_files = [os.path.join(docs_dir, f) for f in os.listdir(docs_dir) if f.endswith(".pdf")]
    all_docs = []
    for pdf in pdf_files:
        loader = PyPDFLoader(pdf)
        all_docs.extend(loader.load())
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = splitter.split_documents(all_docs)
    vectordb = Chroma.from_documents(split_docs, embeddings, persist_directory=CHROMA_DIR)
    vectordb.persist()
retriever = vectordb.as_retriever()

def log_tool_result(tool_name, input_val, result):
    GLOBAL_TOOL_LOG.append({
        "tool": tool_name,
        "input": input_val,
        "result": result
    })

def weather_tool_func(q):
    match = re.search(r"weather in ([\w\s]+)", q.lower())
    city = match.group(1).strip() if match else "Prague"
    response = requests.get("https://api.weatherapi.com/v1/current.json",
                            params={"q": city, "key": os.getenv("WEATHER_API_KEY")})
    data = response.json()
    log_tool_result("weather", city, data)
    return data

def place_tool_func(q):
    match = re.search(r"where is ([\w\s]+)", q.lower())
    place = match.group(1).strip() if match else q
    url = f"https://nominatim.openstreetmap.org/search?q={place}&format=json"
    res = requests.get(url, headers={"User-Agent": "YourApp"}).json()
    log_tool_result("place", place, res)
    if res:
        return res
    return "No place info found."

def wikidata_tool_func(q):
    query = q.strip()
    sparql = f"""
    SELECT ?item ?itemLabel ?itemDescription WHERE {{
        ?item rdfs:label "{query}"@en.
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[EN]". }}
    }} LIMIT 1
    """
    url = "https://query.wikidata.org/sparql"
    headers = {"Accept": "application/sparql-results+json"}
    res = requests.get(url, params={"query": sparql}, headers=headers)
    result = None
    if res.status_code == 200:
        results = res.json()["results"]["bindings"]
        if results:
            entity_url = results[0]['item']['value']
            entity_id = entity_url.split("/")[-1]
            api_url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
            entity_res = requests.get(api_url)
            if entity_res.status_code == 200:
                entity_data = entity_res.json()
                try:
                    description = entity_data['entities'][entity_id]['descriptions']['en']['value']
                    label = entity_data['entities'][entity_id]['labels']['en']['value']
                    result = f"{label}: {description}"
                except Exception:
                    result = f"Wikidata entry: {entity_url} (no English description found)"
            else:
                result = f"Wikidata entry: {entity_url} (failed to fetch entity data)"
    if not result:
        result = "No relevant Wikidata info."
    log_tool_result("wikidata", query, result)
    return result

def celesta_tool_func(q):
    match = re.search(r"for ([\w\s]+) ([a-z]+)(?: (\d{4}(?:, *\d{4})*))?", q.lower())
    if match:
        city = match.group(1).strip()
        indicator = match.group(2).strip()
        years = match.group(3)
        years = [int(y) for y in years.split(",") if y] if years else None
    else:
        city = "Prague"
        indicator = "evi"
        years = None
    base_url = "http://35.159.169.103:8000/data"
    params = {
        "city": city,
        "data": indicator,
        "download": "false"
    }
    if years:
        params["years"] = years
    auth = (os.getenv("CELESTA_USERNAME"), os.getenv("CELESTA_PASSWORD"))
    try:
        response = requests.get(base_url, params=params, auth=auth)
        response.raise_for_status()
        try:
            result = response.json()
        except Exception:
            result = response.text
    except Exception as e:
        result = f"Celesta API error: {e}"
    log_tool_result("celesta", f"city={city}, indicator={indicator}, years={years}", result)
    return result

def rag_tool_func(q):
    relevant_docs = retriever.get_relevant_documents(q)
    context = "\n".join([doc.page_content for doc in relevant_docs])
    log_tool_result("rag", q, context)
    return context if context else "No relevant information found in documents."

def get_and_clear_tool_log():
    global GLOBAL_TOOL_LOG
    log = GLOBAL_TOOL_LOG.copy()
    GLOBAL_TOOL_LOG = []
    return log


rag_tool = Tool(
    name="DocumentRAG",
    func=rag_tool_func,
    description="Retrieve information from PDF documents in the /documents folder. Input should be a question or topic.",
)
weather_tool = Tool(
    name="Weather",
    func=weather_tool_func,
    description="Get the current weather for Prague or a specified city.",
)
place_tool = Tool(
    name="PlaceInfo",
    func=place_tool_func,
    description="Get information about a place. Input should be the place name.",
)
wikidata_tool = Tool(
    name="Wikidata",
    func=wikidata_tool_func,
    description="Get a summary from Wikidata. Input should be the term to look up.",
)
celesta_tool = Tool(
    name="CelestaData",
    func=celesta_tool_func,
    description="Get geographical data from the Celesta API. Input should specify city and indicator.",
)

