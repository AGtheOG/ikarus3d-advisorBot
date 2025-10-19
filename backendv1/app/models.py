from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    """The request model for a user's query."""
    prompt: str

class Product(BaseModel):
    """
    The data model for a single product retrieved from Pinecone.
    These fields MUST match the keys in the 'metadata' you uploaded.
    """
    id: str
    title: str
    price: Optional[str] = "N/A"
    categories: Optional[str] = "Uncategorized"
    image_url: Optional[str] = None
    
class RecommendationResponse(BaseModel):
    """The response model for a single recommendation."""
    product: Product
    generated_description: str