from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    """The request model for a user's query."""
    prompt: str

class Product(BaseModel):
    """The data model for a single product."""
    id: str
    title: str
    price: float
    brand: Optional[str] = None
    category: Optional[str] = None
    image_url: str
    
class RecommendationResponse(BaseModel):
    """The response model for a recommendation."""
    product: Product
    generated_description: str