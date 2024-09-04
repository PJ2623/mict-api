from pprint import pprint
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
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


file_path = "./Law_1-Rule_of_Law.pdf"
loader = PyPDFLoader(file_path, extract_images=True)

data = loader.load()


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

results: dict = rag_chain.invoke(
    {
        "input": "What is the processes for enacting and applying laws must be fair and transparent"
    }
)

pprint(results.get("answer"))
