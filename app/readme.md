

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

Feel free to ask any questions related to the dataset. I have provided the "User_Queries_Test" file, which contains various use case queries. You can test your questions with it.

[Dataset Details](../dataset.md)
