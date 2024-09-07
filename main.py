from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from src import models

from fastapi.responses import HTMLResponse

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from src.routers import auth, users, posts, polls, announcements, sentiments, bot

from contextlib import asynccontextmanager

from pprint import pprint
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, Runnable
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

embeddings = OllamaEmbeddings(
    model="gemma2:2b",
)

model = ChatOllama(
    model="gemma2:2b",
)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://192.168.178.103:8000/api/v1/bot/chat");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

chat_bot = {}


file_path = "./Law_1-Rule_of_Law.pdf"
loader = PyPDFLoader(file_path, extract_images=True)

data = loader.load()


def init_bot():
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    splits = text_splitter.split_documents(data)

    print("Done splitting")

    vector_store = Chroma.from_documents(documents=splits, embedding=embeddings)

    print("Done creating vector store")

    retriever = vector_store.as_retriever()

    print("Done creating retriever")

    system_prompt = (
        " You are an AI assistant for question-answering about Namibian policy."
        "Use the following pieces of retrieved context to answer"
        "the question. If you don't know the answer, you can say 'I don't know'."
        "\n\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    qa_chain = create_stuff_documents_chain(model, prompt)
    rag_chain = create_retrieval_chain(retriever, qa_chain)

    print("Done creating chains")
    return rag_chain


async def initialize_database():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    database = client["mict-hackathon"]
    await init_beanie(
        database,
        document_models=[
            models.User,
            models.VerifiedUser,
            models.Poll,
            models.Post,
            models.Announcements,
        ],
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    chat_bot["rag_chain"] = init_bot()
    await initialize_database()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="MICT Hackathon API",
    description="API for the MICT Hackathon",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/bot/", tags=["Bot"])
async def get():
    return HTMLResponse(html)


@app.websocket("/api/v1/bot/chat")
async def chat_with_bot(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive_text()
        response = chat_bot["rag_chain"].invoke({"input": data})
        await websocket.send_text(response["answer"])


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(polls.router)
app.include_router(announcements.router)
app.include_router(sentiments.router)
