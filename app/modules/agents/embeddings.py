
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config.settings import settings

# Converts user questions into vectors for semantic similarity search.
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=settings.GOOGLE_API_KEY,
    output_dimensionality=768,
)
