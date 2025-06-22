def route_question(question: str):
    q = question.lower()
    if "weather" in q:
        return "weather"
    elif "where is" in q:
        return "place"
    elif "wikidata" in q or "encyclopedia" in q:
        return "wikidata"
    elif "celesta" in q:
        return "celesta"
    else:
        return "rag"
