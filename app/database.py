import os
from pymongo import MongoClient

# Try to get Mongo URI from Streamlit secrets (frontend case)
try:
    import streamlit as st
    MONGO_URI = st.secrets.get("mongo", {}).get("uri")
except Exception:
    MONGO_URI = None

# Fallback to environment variable (backend / Docker case)
if not MONGO_URI:
    MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("❌ No MongoDB URI found. Set it in .streamlit/secrets.toml or as MONGO_URI env variable.")

# Connect to MongoDB
client = MongoClient(MONGO_URI)

db = client["TO_DO_APP"]
users_collection = db["users"]
todos_collection = db["todos"]
