import sys
import os

# Add root directory to sys.path so 'app.main' and other internal imports work smoothly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set writeable cache paths for Vercel's read-only environment
os.environ["FASTEMBED_CACHE_PATH"] = "/tmp/fastembed_cache"
os.environ["HF_HOME"] = "/tmp/hf_home"

# Import your FastAPI instance from app/main.py
from app.main import app

# Export app for Vercel Serverless Function engine
__all__ = ["app"]