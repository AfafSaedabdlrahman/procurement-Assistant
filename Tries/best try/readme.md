# procurement Chatbot

## How to start the chatbot

First run the fastapi server

```bash
cd chatbot
uvicorn main:app --reload
```

Afterwards, run the streamlit app

```bash
cd chatbot
streamlit run chatbot_app.py
```

Visit http://localhost:8501/ to view the app


## Guide to use the chatbot

You can ask any question related to the dataset. 

[Dataset Details](../dataset.md)