# Chatbot Application

This repository hosts a chatbot application built with FastAPI and Streamlit for interacting with a dataset.

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Using the Chatbot](#using-the-chatbot)
3. [Dataset Details](#dataset-details)

---

## Getting Started

Follow the steps below to set up and run the chatbot application:

### 1. Start the FastAPI Server
Navigate to the `chatbot` directory and run the following command to start the FastAPI backend server:

```bash
cd chatbot
uvicorn main:app --reload
```

### 2. Run the Streamlit App
After starting the server, navigate to the same directory and launch the Streamlit application with the command:

```bash
streamlit run chatbot_app.py
```

### 3. Access the Application
Open your browser and visit [http://localhost:8501/](http://localhost:8501/) to access the chatbot interface.

---

## Using the Chatbot

The chatbot is designed to answer questions related to the dataset:

- You can test its functionality using queries provided in the [`User_Queries_Test`](https://github.com/AfafSaedabdlrahman/procurement-Chatbot/blob/main/app/User_Queries_Test.txt) file, which contains various sample use cases.
- Feel free to explore the dataset by asking any relevant questions directly through the chatbot interface.

---

## Dataset Details

The dataset used in this project contains valuable information for chatbot interactions. For more details, refer to the [Dataset Documentation](https://github.com/AfafSaedabdlrahman/procurement-Chatbot/blob/main/DataSet/dataset.md).

---
