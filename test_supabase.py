import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "documents")

print(f"Connecting to: {url}")
print(f"Target Bucket: {bucket}")

try:
    supabase = create_client(url, key)
    # Test bucket listing
    buckets = supabase.storage.list_buckets()
    print("Buckets found in project:", [b.name for b in buckets])

    # Test file upload
    test_bytes = b"Hello World Test"
    res = supabase.storage.from_(bucket).upload(
        path="test_connection.txt",
        file=test_bytes,
        file_options={"upsert": "true"}
    )
    print("✅ Storage Upload Success! Path:", res)
except Exception as e:
    print("❌ Storage Test Failed with Error:", e)