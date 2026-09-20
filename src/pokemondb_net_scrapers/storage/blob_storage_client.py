import fsspec


class BlobStorageClient:
    """StorageClient backed by fsspec, so the concrete backend - S3, GCS,
    Azure Blob, local disk, even an in-memory filesystem for tests - is
    selected by remote_path's URI scheme at runtime (e.g. "s3://...",
    "gs://...", "az://...") rather than hardcoded to one cloud provider.

    fsspec's core package only ships the local and in-memory filesystems -
    install whichever backend package the URI scheme you actually use needs
    (s3fs for "s3://", gcsfs for "gs://", adlfs for "az://", ...) alongside
    this package; picking one isn't this class's concern.
    """

    def upload_file(self, local_path: str, remote_path: str) -> str:
        fs, path = fsspec.core.url_to_fs(remote_path)
        fs.put(local_path, path)
        return remote_path
