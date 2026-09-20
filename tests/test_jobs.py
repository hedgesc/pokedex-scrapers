import pytest

from pokemondb_net_scrapers import jobs
from pokemondb_net_scrapers.config import settings
from pokemondb_net_scrapers.models.move import Move


class FakeBuilder:
    def __init__(self, items):
        self._items = items

    def build(self):
        return self._items


class FakeStorageClient:
    def __init__(self):
        self.calls = []

    def upload_file(self, local_path, remote_path):
        self.calls.append((local_path, remote_path))
        return "uploaded://" + remote_path


def make_move(moveId, name):
    m = Move(name, name.lower(), "Normal", "Physical", "40", "100", "35", "", "")
    m.moveId = moveId
    return m


def test_export_pipeline_to_csv_raises_for_unknown_pipeline():
    with pytest.raises(KeyError):
        jobs.export_pipeline_to_csv("not_a_real_pipeline")


def test_export_pipeline_to_csv_scrapes_exports_and_uploads(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "csv_output_folder", str(tmp_path))
    monkeypatch.setattr(settings, "moves_csv_file", "moves.csv")
    monkeypatch.setattr(settings, "storage_bucket", "s3://my-bucket")
    monkeypatch.setattr(settings, "storage_prefix", "pokedex/exports/")

    moves = [make_move(1, "Tackle"), make_move(2, "Growl")]
    monkeypatch.setitem(jobs._BUILDERS, "moves", lambda: FakeBuilder(moves))

    fake_storage = FakeStorageClient()
    monkeypatch.setattr(jobs, "get_storage_client", lambda: fake_storage)

    result = jobs.export_pipeline_to_csv("moves")

    assert result == "uploaded://s3://my-bucket/pokedex/exports/moves.csv"
    assert len(fake_storage.calls) == 1

    local_path, remote_path = fake_storage.calls[0]
    assert local_path.endswith("moves.csv")
    assert remote_path == "s3://my-bucket/pokedex/exports/moves.csv"

    with open(local_path, encoding="utf-8") as f:
        lines = f.readlines()

    assert len(lines) == 3  # header + 2 moves


def test_export_pipeline_to_csv_raises_on_empty_builder_output(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "csv_output_folder", str(tmp_path))
    monkeypatch.setitem(jobs._BUILDERS, "moves", lambda: FakeBuilder([]))

    with pytest.raises(ValueError):
        jobs.export_pipeline_to_csv("moves")


def test_remote_path_joins_bucket_prefix_and_filename(monkeypatch):
    monkeypatch.setattr(settings, "storage_bucket", "gs://my-bucket/")
    monkeypatch.setattr(settings, "storage_prefix", "pokedex/exports/")

    assert jobs._remote_path("/tmp/whatever/moves.csv") == "gs://my-bucket/pokedex/exports/moves.csv"


def test_all_registered_pipelines_are_constructible():
    # Every factory should build a Builder without hitting the network -
    # PokemonDb*Source/StaticYaml*Source construction is itself side-effect
    # free, and get_cache_client()/RedisCacheClient's connection is lazy.
    for name, factory in jobs._BUILDERS.items():
        builder = factory()
        assert hasattr(builder, "build"), "pipeline '{0}' factory didn't return a Builder".format(name)
