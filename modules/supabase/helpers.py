import os
from supabase import create_client, Client
from dotenv import load_dotenv
from nanoid import generate

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = os.getenv("SUPABASE_BUCKET_NAME")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_file(file_bytes, file_name):
    file_name_with_id = f"{generate("1234567890abcdef", 10)}-{file_name}"
    try:
        response = supabase.storage.from_(BUCKET_NAME).upload(
            f"images/{file_name_with_id}", file_bytes
        )
        print("response upload", response, file_name)
        if response.status_code == 200:
            return supabase.storage.from_(BUCKET_NAME).get_public_url(
                f"images/{file_name_with_id}"
            )
        else:
            raise Exception(
                f"Failed to upload file: {response.status_code} {response.data}"
            )
    except Exception as e:
        print("Error while upload to supabase storage", e)


def get_public_url(file_name):
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/images/{file_name}"
