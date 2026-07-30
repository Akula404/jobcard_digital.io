import os
import mimetypes

from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from supabase import create_client


class SupabaseStorage(Storage):

    @property
    def client(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY")

        print("=" * 60)
        print("SUPABASE_URL:", repr(url))
        print("SUPABASE_SERVICE_KEY exists:", bool(key))
        print("=" * 60)

        if not url:
            raise Exception("SUPABASE_URL environment variable is missing.")

        if not key:
            raise Exception("SUPABASE_SERVICE_KEY environment variable is missing.")

        return create_client(url, key)

    def _save(self, name, content):
        name = name.replace("\\", "/")
        content.seek(0)

        mime = mimetypes.guess_type(name)[0] or "application/octet-stream"

        self.client.storage.from_("signatures").upload(
            path=name,
            file=content.read(),
            file_options={
                "content-type": mime,
                "upsert": "true",
            },
        )

        return name

    def url(self, name):
        return self.client.storage.from_("signatures").get_public_url(name)

    def open(self, name, mode="rb"):
        data = self.client.storage.from_("signatures").download(name)
        return ContentFile(data)

    def delete(self, name):
        self.client.storage.from_("signatures").remove([name])

    def exists(self, name):
        return False

    def size(self, name):
        return 0

    def get_available_name(self, name, max_length=None):
        return name