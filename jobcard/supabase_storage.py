import os
import mimetypes

from django.core.files.base import ContentFile
from django.core.files.storage import Storage

from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
SUPABASE_BUCKET = os.environ.get("SUPABASE_BUCKET", "signatures")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class SupabaseStorage(Storage):

    def _save(self, name, content):
        # Convert Windows paths to Unix paths
        name = name.replace("\\", "/")

        content.seek(0)

        mime_type = mimetypes.guess_type(name)[0] or "application/octet-stream"

        result = supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=name,
            file=content.read(),
            file_options={
                "content-type": mime_type,
                "upsert": "true",
            },
        )

        return name

    def delete(self, name):
        supabase.storage.from_(SUPABASE_BUCKET).remove([name])

    def exists(self, name):
        return False

    def size(self, name):
        return 0

    def get_available_name(self, name, max_length=None):
        return name

    def open(self, name, mode="rb"):
        data = supabase.storage.from_(SUPABASE_BUCKET).download(name)
        return ContentFile(data)

    def url(self, name):
        result = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(name)

        if isinstance(result, dict):
            return result["publicUrl"]

        return result