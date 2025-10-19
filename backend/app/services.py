import json
import torch
import numpy as np
from PIL import Image
import requests
import os
from io import BytesIO
from langchain_core.prompts import PromptTemplate
from .core import (
    index, 
    llm, 
    text_embedder, 
    clip_model, 
    clip_processor, 
    DEVICE
)

# --- 1. Analytics Service ---

def get_analytics_data():
    """Loads the pre-computed analytics JSON data."""
    try:
        file_path = os.path.join("app", "data", "analytics_summary.json")
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "Analytics file not found."}
    except Exception as e:
        return {"error": str(e)}

# --- 2. Recommendation Service ---

def get_text_embedding(text: str):
    """Generates a text embedding."""
    return text_embedder.encode(text)

def get_image_embedding_from_text(text: str):
    """Generates an 'image' embedding from a text query using CLIP."""
    # We process the *text* with the CLIP processor to get a vector
    # that can be compared against image vectors.
    with torch.no_grad():
        inputs = clip_processor(
            text=text, 
            return_tensors="pt", 
            padding=True
        ).to(DEVICE)
        text_features = clip_model.get_text_features(**inputs)
    return text_features.cpu().numpy().flatten()

def create_hybrid_query_vector(text_query: str):
    """Creates a hybrid vector from a text query."""
    # 1. Get text embedding (384 dims)
    text_vec = get_text_embedding(text_query)
    
    # 2. Get image-space embedding from text (512 dims)
    image_vec = get_image_embedding_from_text(text_query)
    
    # 3. Concatenate (896 dims)
    hybrid_vec = np.concatenate([text_vec, image_vec])
    return hybrid_vec.tolist()

def query_pinecone(vector: list, top_k: int = 5):
    """Queries the Pinecone index."""
    if index is None:
        raise ConnectionError("Pinecone index is not initialized.")
    
    results = index.query(
        vector=vector,
        top_k=top_k,
        include_metadata=True
    )
    return results['matches']

# --- 3. GenAI Service ---

# Setup the LangChain prompt template 
template = """
You are a creative marketing assistant. Your task is to write a short,
engaging, and creative product description (2-3 sentences) for a furniture website.
Do NOT just list the features. Make it sound appealing.

Product Details:
- Title: {title}
- Category: {category}

Your Creative Description:
"""
prompt_template = PromptTemplate.from_template(template)
llm_chain = prompt_template | llm

def generate_creative_description(title: str, category: str):
    """Generates a creative description using the GenAI model."""
    if llm is None:
        raise ConnectionError("LLM model is not initialized.")
        
    try:
        response = llm_chain.invoke({
            "title": title,
            "category": category
        })
        return response.content
    except Exception as e:
        print(f"GenAI call failed: {e}")
        return "Discover a wonderful new addition for your home."