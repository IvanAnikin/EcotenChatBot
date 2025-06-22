import os
import requests
import string


def get_weather(location="Prague"):
    response = requests.get(f"https://api.weatherapi.com/v1/current.json",
                            params={"q": location, "key": "5ec32a5beaa94777b66122207251906"})
    data = response.json()
    print(data)
    return data

def get_place_info(query: str) -> str:
    query = query.strip().strip(string.punctuation)
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
    res = requests.get(url, headers={"User-Agent": "YourApp"}).json()
    print(res)
    if res:
        return res
    return "No place info found."

def get_wikidata_summary(query: str) -> str:
    sparql = f"""
    SELECT ?item ?itemLabel ?itemDescription WHERE {{
        ?item rdfs:label "{query}"@en.
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[EN]". }}
    }} LIMIT 1
    """
    url = "https://query.wikidata.org/sparql"
    headers = {"Accept": "application/sparql-results+json"}
    res = requests.get(url, params={"query": sparql}, headers=headers)
    if res.status_code == 200:
        results = res.json()["results"]["bindings"]
        print(results)
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
                    print(f"{label}: {description}")
                    return f"{label}: {description}"
                except Exception as e:
                    return f"Wikidata entry: {entity_url} (no English description found)"
            else:
                return f"Wikidata entry: {entity_url} (failed to fetch entity data)"
    return "No relevant Wikidata info."

def get_celesta_data(city, indicator, years=None, download=False, username=None, password=None):
    import requests
    base_url = "http://35.159.169.103:8000/data"
    params = {
        "city": city,
        "data": indicator,
        "download": str(download).lower()
    }
    if years:
        params["years"] = years
    auth = (username, password) if username and password else None
    try:
        response = requests.get(base_url, params=params, auth=auth)
        response.raise_for_status()
        try:
            return response.json()
        except Exception:
            return response.text
    except Exception as e:
        return f"Celesta API error: {e}"
