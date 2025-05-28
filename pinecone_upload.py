import os
import psycopg2
from dotenv import load_dotenv
from google.generativeai import configure, embed_content
from pinecone import Pinecone, ServerlessSpec

# === Load environment variables ===
load_dotenv()

# === Configure Gemini ===
configure(api_key=os.getenv("GOOGLE_API_KEY"))

# === Function to get embedding from Gemini 1.5 Flash ===
def get_embedding(text):
    result = embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return result["embedding"]

# === Connect to PostgreSQL ===
conn = psycopg2.connect(
    dbname="sarvamAI_DB",
    user="postgres",
    password=os.getenv("POSTGRES_PASSWORD"),
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# === Initialize Pinecone client ===
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = os.getenv("PINECONE_INDEX_NAME")
pinecone_env = os.getenv("PINECONE_ENVIRONMENT")  # (Optional if you want to use it)

# Check if index exists, create if not
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768,  # Gemini embedding dimension
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",      # Adjust if your environment is different
            region="us-west-2"  # Adjust to your Pinecone environment region
        )
    )

# Connect to the index
index = pc.Index(index_name)

# === Fetch restaurant data with cuisines and features ===
cursor.execute("""
    SELECT r.id, r.name, r.city, r.description,
           array_agg(DISTINCT c.name) AS cuisines,
           array_agg(DISTINCT f.name) AS features
    FROM restaurants r
    LEFT JOIN restaurant_cuisines rc ON r.id = rc.restaurant_id
    LEFT JOIN cuisines c ON rc.cuisine_id = c.id
    LEFT JOIN restaurant_features rf ON r.id = rf.restaurant_id
    LEFT JOIN features f ON rf.feature_id = f.id
    GROUP BY r.id;
""")
rows = cursor.fetchall()

# === Prepare and upsert embeddings ===
vectors = []

for row in rows:
    restaurant_id, name, city, description, cuisines, features = row

    if not description:
        continue

    cuisines_str = ", ".join(cuisines) if cuisines else ""
    features_str = ", ".join(features) if features else ""

    combined_text = f"{description}\nCuisines: {cuisines_str}\nFeatures: {features_str}"

    metadata = {
        "restaurant_id": restaurant_id,
        "name": name,
        "city": city,
        "cuisines": cuisines,
        "features": features,
    }

    embedding = get_embedding(combined_text)
    vectors.append((str(restaurant_id), embedding, metadata))

# Upsert vectors to Pinecone index
index.upsert(vectors)

print("Embeddings successfully inserted into Pinecone.")

# === Cleanup ===
cursor.close()
conn.close()
