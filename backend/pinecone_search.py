from pinecone import Pinecone
import os
from google.generativeai import configure, embed_content

configure(api_key=os.getenv("GOOGLE_API_KEY"))

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX_NAME")
index = pc.Index(index_name)

def get_embedding(text):
    result = embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return result["embedding"]

def normalize_text(text):
    if not text:
        return text
    return " ".join(word.capitalize() for word in text.split())

def query_pinecone(query_text, city_filter=None, cuisine_filter=None, top_k=3):
    query_embedding = get_embedding(query_text)
    filters = {}
    if city_filter:
        city_filter = normalize_text(city_filter)  # Normalize city filter case
        filters["city"] = {"$eq": city_filter}
    if cuisine_filter:
        cuisine_filter = normalize_text(cuisine_filter)  # Normalize cuisine filter case
        filters["cuisines"] = {"$in": [cuisine_filter]}
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        filter=filters if filters else None,
        include_metadata=True
    )
    return results.matches
