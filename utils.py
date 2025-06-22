import os
import fitz
import tiktoken
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(text))

def load_vectorstore(theKey):
    embeddings = OpenAIEmbeddings(openai_api_key=theKey)

    if os.path.exists(".chroma_store"):
        vectorstore = Chroma(persist_directory=".chroma_store", embedding_function=embeddings)
        print("LOADED")
    else:
        all_docs = []
        for filename in os.listdir("documents"):
            if filename.endswith(".pdf"):
                path = os.path.join("documents", filename)
                text = ""
                with fitz.open(path) as doc:
                    for page in doc:
                        text += page.get_text()
                all_docs.append(Document(page_content=text, metadata={"source": filename}))

        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=800,
            chunk_overlap=100
        )
        chunks = splitter.split_documents(all_docs)
        vectorstore = Chroma(embedding_function=embeddings, persist_directory=".chroma_store")

        current_batch = []
        current_tokens = 0
        max_tokens_per_batch = 100_000  
        for chunk in chunks:
            tokens = count_tokens(chunk.page_content)
            if current_tokens + tokens > max_tokens_per_batch:
                vectorstore.add_documents(current_batch)
                current_batch = []
                current_tokens = 0
            current_batch.append(chunk)
            current_tokens += tokens

        if current_batch:
            vectorstore.add_documents(current_batch)

        vectorstore.persist()

    return vectorstore
