import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

def process_document(text: str):
    """
    In a real scenario, this would chunk the text, embed it with GoogleGenerativeAIEmbeddings,
    and store it in Pinecone. Then it would use ChatGoogleGenerativeAI to generate questions based on the context.
    """
    has_keys = os.getenv("GOOGLE_API_KEY") and os.getenv("PINECONE_API_KEY")

    if has_keys:
        pass

    questions = []
    for i in range(1, 21):
        questions.append({
            "id": i,
            "text": f"Based on the document, what is the significance of concept {i}?",
            "citation": f"Page {min(i%5 + 1, len(text)//1000 + 1)}, Paragraph {i%3 + 1}"
        })
    return questions
