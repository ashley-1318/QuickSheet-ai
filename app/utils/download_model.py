
import os
from sentence_transformers import SentenceTransformer

# Define the model to download
MODEL_NAME = "sentence-transformers/paraphrase-MiniLM-L3-v2"
CACHE_FOLDER = os.environ.get("SENTENCE_TRANSFORMERS_HOME", "/app/models_cache")

print(f"Downloading model {MODEL_NAME} to {CACHE_FOLDER}...")
model = SentenceTransformer(MODEL_NAME, cache_folder=CACHE_FOLDER)
print("Model downloaded successfully.")
