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

Feel free to ask any questions related to the dataset. I have provided a list of various use case queries in the "Evaluation" folder—please review them for testing. Additionally, I will provide a video demonstrating the best approach and an image showing the results for each Try .

[Dataset Details](../dataset.md)