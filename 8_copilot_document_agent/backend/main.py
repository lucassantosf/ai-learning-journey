import uvicorn
from src.interfaces.api_controller import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)