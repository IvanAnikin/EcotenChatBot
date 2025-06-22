import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from tools import weather_tool, place_tool, wikidata_tool, celesta_tool, rag_tool, get_and_clear_tool_log, python_interpreter_tool
import json

load_dotenv("config.env")
app = Flask(__name__)
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model_name="gpt-3.5-turbo")

tools = [
    weather_tool,
    place_tool,
    wikidata_tool,
    celesta_tool,
    rag_tool,
    python_interpreter_tool, 
]
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_question = data.get("question", "")
    result = agent.invoke(
        {"input": user_question},
        return_intermediate_steps=True,
    )
    answer = result["output"]
    tool_log = get_and_clear_tool_log()
    context = json.dumps(tool_log, indent=2, ensure_ascii=False) if tool_log else ""
    return jsonify({"answer": answer, "context": context})


if __name__ == "__main__":
    app.run(debug=True)
