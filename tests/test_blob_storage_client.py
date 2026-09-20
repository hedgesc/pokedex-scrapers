import fsspec

from pokemondb_net_scrapers.storage import BlobStorageClient


def test_upload_file_copies_local_file_to_remote_uri(tmp_path):
    local_path = tmp_path / "characters.csv"
    local_path.write_text("character_id,name\n1,Bulbasaur\n", encoding="utf-8", newline="")

    # memory:// ships with fsspec's core install - no cloud credentials or
    # backend package (s3fs/gcsfs/adlfs) needed to exercise the real
    # fsspec.core.url_to_fs()/fs.put() path this class actually uses.
    remote_path = "memory://test-bucket/exports/characters.csv"

    client = BlobStorageClient()
    result = client.upload_file(str(local_path), remote_path)

    assert result == remote_path

    fs = fsspec.filesystem("memory")
    assert fs.exists("/test-bucket/exports/characters.csv")
    assert fs.cat("/test-bucket/exports/characters.csv").decode("utf-8") == "character_id,name\n1,Bulbasaur\n"

    fs.rm("/test-bucket/exports/characters.csv")


def test_upload_file_returns_the_given_remote_path(tmp_path):
    local_path = tmp_path / "moves.csv"
    local_path.write_text("move_id,name\n1,Tackle\n", encoding="utf-8")
    remote_path = "memory://another-bucket/moves.csv"

    result = BlobStorageClient().upload_file(str(local_path), remote_path)

    assert result == remote_path

    fsspec.filesystem("memory").rm("/another-bucket/moves.csv")
