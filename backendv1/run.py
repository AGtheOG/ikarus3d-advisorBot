import uvicorn
import os

if __name__ == "__main__":
    # This runs the 'app' object from the 'app.main' module
    uvicorn.run("app.main:app", 
                host="0.0.0.0", 
                port=8000, 
                reload=True)