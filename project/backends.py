from django.core.files.storage import get_storage_class
from storages.backends.s3boto import S3BotoStorage


class CachedS3BotoStorage(S3BotoStorage):
    """
    S3 storage backend that saves the files locally, too.
    """
    def __init__(self, *args, **kwargs):
        super(CachedS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()

    def save(self, name, content):
        name = super(CachedS3BotoStorage, self).save(name, content)
        self.local_storage._save(name, content)
        return name

    def url(self, name):
        try:
            u = self.bucket.get_key(name).generate_url(3600, method='GET')
            if u.find('?') > 0:
                u = u[:u.find('?')]
            if u.find('#') > 0:
                u = u[:u.find('#')]

            return u
        except:
            return ""
