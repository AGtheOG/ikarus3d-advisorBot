import json
import os
import numpy as np
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# The '.' imports are crucial. They mean "import from the current package".
# This is why the 'app' folder structure is important.
from .core import (
    index, 
    llm, 
    multimodal_embedder
)

# --- 1. Analytics Service ---

def get_analytics_data():
    """Loads the pre-computed analytics JSON data."""
    # This robust path finds the file relative to *this* services.py file
    file_path = os.path.join(os.path.dirname(__file__), "data", "analytics_summary.json")
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "Analytics file not found."}
    except Exception as e:
        return {"error": str(e)}

# --- 2. Recommendation Service ---

def get_query_embedding(text: str):
    """
    Generates an embedding for a text query using our single multimodal model.
    """
    if multimodal_embedder is None:
        raise ConnectionError("Multimodal embedder is not initialized.")
    
    # Encode the text query into the same 512-dim space
    vector = multimodal_embedder.encode(text)
    return vector.tolist() # Convert to list for Pinecone

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

# --- 3. GenAI Service (using LangChain) ---

# Setup the LangChain prompt template 
template = """
You are a creative marketing assistant. Your task is to write a short,
engaging, and creative product description (2-3 sentences) for a furniture website.
Do NOT just list the features. Make it sound appealing.

Product Details:
- Title: {title}
- Categories: {categories}

Your Creative Description:
"""
prompt_template = PromptTemplate.from_template(template)

# Use modern LangChain Expression Language (LCEL) to build the chain
# This chains the prompt, to the model, to an output parser
llm_chain = prompt_template | llm | StrOutputParser()

def generate_creative_description(title: str, categories: str):
    """Generates a creative description using the GenAI model."""
    if llm is None:
        raise ConnectionError("LLM model is not initialized.")
        
    try:
        # 'invoke' is the standard way to run an LCEL chain
        response = llm_chain.invoke({
            "title": title,
            "categories": categories # This key must match the template
        })
        return response
    except Exception as e:
        print(f"GenAI call failed: {e}")
        # Provide a safe fallback description
        return "Discover a wonderful new addition for your home."