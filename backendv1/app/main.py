from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# These '.' imports are correct for the 'app' package structure
from .models import QueryRequest, RecommendationResponse, Product
from .services import (
    get_analytics_data, 
    get_query_embedding,
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
origins = [
    "http://localhost:3000",  # Default React dev server
    "http://localhost:5173",  # Default Vite/React dev server
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
    Main recommendation endpoint.
    Takes a user prompt, finds recommendations, and generates descriptions.
    """
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    try:
        # 1. Create the query vector from the user's prompt
        query_vector = get_query_embedding(request.prompt)
        
        # 2. Query Pinecone for the top 3 matches
        matches = query_pinecone(query_vector, top_k=3)
        
        response_list = []
        for match in matches:
            # 3. Get product data from Pinecone metadata
            metadata = match.get('metadata', {})
            
            # 4. Map metadata to our Product model
            # This is a common place for errors if keys don't match
            product = Product(
                id=match.get('id', 'unknown-id'),
                title=metadata.get('title', 'No Title'),
                price=metadata.get('price', 'N/A'),
                categories=metadata.get('categories', 'Uncategorized'),
                image_url=metadata.get('image_url', '')
            )
            
            # 5. Generate a creative description for each product
            description = generate_creative_description(
                title=product.title,
                categories=product.categories
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
        print(f"Error in /recommend: {e}") # Better logging
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")