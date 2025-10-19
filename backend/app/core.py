import os
import torch
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_google_genai import ChatGoogleGenerativeAI
from sentence_transformers import SentenceTransformer
from transformers import AutoProcessor, AutoModel

# Load environment variables from .env file
load_dotenv()

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not PINECONE_API_KEY or not GOOGLE_API_KEY:
    raise EnvironmentError("API keys (PINECONE_API_KEY, GOOGLE_API_KEY) not set.")

# --- Client Setup ---

# 1. Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
INDEX_NAME = "product-recommendation"
try:
    index = pc.Index(INDEX_NAME)
    print("Pinecone index loaded.")
except Exception as e:
    print(f"Error connecting to Pinecone index: {e}")
    index = None

# 2. GenAI (Gemini)
try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
    print("Gemini model loaded.")
except Exception as e:
    print(f"Error loading Gemini model: {e}")
    llm = None

# 3. Embedding Models (CPU for the API server)
# Use CPU for inference on the server to save resources
DEVICE = torch.device("cpu")

# Text Embedder
text_embedder = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    device=DEVICE
)
print("Text embedder loaded.")

# Image Embedder (CLIP)
clip_model = AutoModel.from_pretrained(
    "openai/clip-vit-base-patch32"
).to(DEVICE)
clip_processor = AutoProcessor.from_pretrained(
    "openai/clip-vit-base-patch32"
)
print("Image (CLIP) model loaded.")