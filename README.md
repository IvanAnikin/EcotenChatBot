# GeoChatbot

GeoChatbot is an interactive Flask-based chatbot that leverages LangChain agent tools to answer questions about weather, places, Wikidata, Celesta API data, and PDF document retrieval (RAG). It uses OpenAI for language understanding and provides a transparent, interactive log of all tool calls and results.

## Features
- **Weather Tool:** Get current weather for any city using WeatherAPI.
- **Place Info Tool:** Retrieve location information using OpenStreetMap Nominatim.
- **Wikidata Tool:** Fetch entity summaries from Wikidata.
- **Celesta Tool:** Query geographical data from the Celesta API.
- **RAG Tool:** Retrieve answers from local PDF documents using a persistent Chroma vector database.
- **Agent Reasoning Log:** All tool calls and results are logged and shown as an interactive JSON table in the web UI.

## Project Structure
```
├── app.py                # Flask app and API endpoints
├── tools.py              # All tool logic and global tool log
├── routes.py             # (Legacy) simple routing logic
├── requirements.txt      # Python dependencies
├── config.env            # API keys and credentials (not tracked in git)
├── templates/
│   └── index.html        # Web frontend
├── documents/            # PDF files for RAG
├── chroma_store/         # Persistent vector DB (auto-generated)
└── ...
```

## Setup
1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment:**
   - Copy `config.env` and fill in your API keys (see example below).

   Example `config.env`:
   ```env
   OPENAI_API_KEY="sk-..."
   WEATHER_API_KEY="..."
   CELESTA_USERNAME="..."
   CELESTA_PASSWORD="..."
   ```
4. **Add PDF documents:**
   - Place your PDF files in the `documents/` folder for RAG.

5. **Run the app:**
   ```bash
   python app.py
   ```
   The app will be available at http://localhost:5000

## Usage
- Open the web UI and ask questions about weather, places, Wikidata, Celesta data, or information in your PDFs.
- The chatbot will display its answer and show a detailed, interactive log of all tool calls and results.

## Dependencies
See `requirements.txt` for all required Python packages.

## Security
- Do **not** commit your `config.env` or API keys to version control.
- The `chroma_store/` and `config.env` are excluded via `.gitignore`.

## License
MIT License

---
*GeoChatbot: AI-powered, transparent, and extensible for geospatial Q&A.*
