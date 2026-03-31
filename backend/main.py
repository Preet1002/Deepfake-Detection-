from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from transformers import pipeline
from PIL import Image
import io
import uvicorn
import os

app = FastAPI(title="Deepfake Detection API")

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Hugging Face pipeline
# Using a ViT model robust at distinguishing general real vs AI images
model_name = "umm-maybe/AI-image-detector"
os.environ['HF_HUB_ENABLE_HF_TRANSFER'] = '0'

print(f"Loading model '{model_name}'...")
try:
    classifier = pipeline("image-classification", model=model_name, device=-1)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    classifier = None

@app.post("/api/detect")
async def detect_image(file: UploadFile = File(...)):
    if classifier is None:
        raise HTTPException(status_code=500, detail="Model failed to load.")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Run inference
        results = classifier(image)
        
        # results is typically a list of dicts: [{'label': 'FAKE', 'score': 0.99}, ...]
        best_result = max(results, key=lambda x: x['score'])
        
        # The labels might be 'Real' or 'Fake' depending on the model, we normalize to uppercase
        label = best_result['label'].upper()
        # Handle various model outputs
        if label in ['ORIGINAL', 'HUMAN']:
            label = 'REAL'
        elif label == 'ARTIFICIAL':
            label = 'FAKE'
            
        return {
            "label": label,
            "confidence": float(best_result['score'])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount the frontend directory if it exists
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
else:
    print(f"Frontend directory not found at {frontend_dir}. Static files won't be served over the root route yet.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
