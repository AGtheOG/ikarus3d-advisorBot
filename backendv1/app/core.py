import os
import torch
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_google_genai import ChatGoogleGenerativeAI
from sentence_transformers import SentenceTransformer

# Load environment variables from .env file
load_dotenv()

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not PINECONE_API_KEY or not GOOGLE_API_KEY:
    raise EnvironmentError("API keys (PINECONE_API_KEY, GOOGLE_API_KEY) not set in .env file.")

# --- Client Setup ---

# 1. Pinecone
# Uses the modern pinecone-client (v3.x+)
pc = Pinecone(api_key=PINECONE_API_KEY)

# !! CRITICAL !! This MUST match the index name from your notebook
INDEX_NAME = "product-recommender-clip" 
try:
    index = pc.Index(INDEX_NAME)
    print(f"Connected to Pinecone index: {INDEX_NAME}")
except Exception as e:
    print(f"Error connecting to Pinecone index '{INDEX_NAME}': {e}")
    index = None

# 2. GenAI (Gemini)
try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", 
                                 temperature=0.7, 
                                 google_api_key=GOOGLE_API_KEY)
    print("Gemini 1.5 Flash model loaded.")
except Exception as e:
    print(f"Error loading Gemini model: {e}")
    llm = None

# 3. Multimodal Embedding Model (CLIP)
# Use CPU for inference on the server
DEVICE = torch.device("cpu")

# !! CRITICAL !! This MUST be the exact same model from your notebook
try:
    multimodal_embedder = SentenceTransformer(
        'sentence-transformers/clip-ViT-B-32',
        device=DEVICE
    )
    print("Multimodal (CLIP) embedder loaded.")
except Exception as e:
    print(f"Error loading multimodal embedder: {e}")
    multimodal_embedder = None