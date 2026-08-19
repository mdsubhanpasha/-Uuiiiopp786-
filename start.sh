#!/bin/bash

# Start FastAPI backend in the background
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit UI in the foreground
streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0
