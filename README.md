# MICT Hackathon ChatBot API

This API was developed for the MICT Hackathon to support a ChatBot that can provide accurate, real-time information about the Namibian constitution. Built with **FastAPI**, **LangChain**, and **Llama**, the ChatBot leverages **Retrieval-Augmented Generation (RAG)** to deliver up-to-date answers by combining recent data retrieval and large language model capabilities.

While the primary function is to respond with information related to the Namibian constitution, this API also includes several additional features that extend the ChatBot’s capabilities.

---

## Core Technologies

- **FastAPI**: A fast web framework for building APIs.
- **LangChain**: A framework for building applications with language models.
- **Llama**: An advanced language model that powers the ChatBot’s natural language understanding.
- **Retrieval-Augmented Generation (RAG)**: A method to improve accuracy by providing real-time information retrieval.

---

## Key Features

### 1. Namibian Constitution Q&A  
- **Endpoint**: `/chat/constitution`  
- **Method**: `POST`  
- **Description**: The core functionality of this API, enabling the ChatBot to answer questions about the Namibian constitution with high accuracy and relevance.  
- **Input**:  
  - `question` (string): The user's question.  
- **Output**:  
  - `answer` (string): The ChatBot's response based on the latest information.  

### 2. Additional Functionality  
- While this API is designed to focus on constitutional questions, it is not limited to them. Other endpoints exist for general-purpose question-answering, sentiment analysis, and announcements.

---

## Getting Started

To start using the API, clone the repository and install the required packages:

```bash
git clone https://github.com/PJ2623/mict-chatbot.git
cd mict-chatbot
pip install -r requirements.txt
