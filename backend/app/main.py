from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn

from .models import QueryRequest, RecommendationResponse, Product
from .services import (
    get_analytics_data, 
    create_hybrid_query_vector, 
    query_pinecone, 
    generate_creative_description
)

# Initialize the FastAPI app
app = FastAPI(
    title="Product Recommendation API",
    description="API for furniture recommendation, analytics, and GenAI.",
    version="1.0.0"
)

# --- CORS Middleware ---
# This allows your React frontend to communicate with this backend.
origins = [
    "http://localhost:3000",  # Default React dev server
    "http://localhost:5173",  # Default Vite dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---

@app.get("/api")
async def root():
    return {"message": "Product Recommendation API is running."}

@app.get("/api/analytics")
async def get_analytics():
    """
    Endpoint for the analytics page. 
    Returns the pre-computed JSON data.
    """
    data = get_analytics_data()
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data

@app.post("/api/recommend", response_model=List[RecommendationResponse])
async def recommend_products(request: QueryRequest):
    """
    Main recommendation endpoint. [cite: 5, 7]
    Takes a user prompt, finds recommendations, and generates descriptions. [cite: 31]
    """
    try:
        # 1. Create the query vector from the user's prompt
        query_vector = create_hybrid_query_vector(request.prompt)
        
        # 2. Query Pinecone for the top 3 matches
        matches = query_pinecone(query_vector, top_k=3)
        
        response_list = []
        for match in matches:
            # 3. Get product data from Pinecone metadata
            metadata = match['metadata']
            product = Product(
                id=match['id'],
                title=metadata.get('title', 'No Title'),
                price=metadata.get('price', 0.0),
                brand=metadata.get('brand', 'Unknown'),
                category=metadata.get('category', 'General'),
                image_url=metadata.get('image_url', '')
            )
            
            # 4. Generate a creative description for each product [cite: 31]
            description = generate_creative_description(
                title=product.title,
                category=product.category
            )
            
            response_list.append(
                RecommendationResponse(
                    product=product,
                    generated_description=description
                )
            )
            
        return response_list

    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# --- Main execution ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)