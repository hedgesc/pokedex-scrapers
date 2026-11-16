import pytest

from pokemondb_net_scrapers import jobs
from pokemondb_net_scrapers.config import settings
from pokemondb_net_scrapers.models.move import Move


class FakeBuilder:
    def __init__(self, items):
        self._items = items

    def build(self):
        return self._items


def make_move(moveId, name):
    m = Move(name, name.lower(), "Normal", "Physical", "40", "100", "35", "", "")
    m.moveId = moveId
    return m


def test_export_pipeline_to_csv_raises_for_unknown_pipeline():
    with pytest.raises(KeyError):
        jobs.export_pipeline_to_csv("not_a_real_pipeline")


def test_export_pipeline_to_csv_scrapes_and_exports(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "csv_output_folder", str(tmp_path))
    monkeypatch.setattr(settings, "moves_csv_file", "moves.csv")

    moves = [make_move(1, "Tackle"), make_move(2, "Growl")]
    monkeypatch.setitem(jobs._BUILDERS, "moves", lambda: FakeBuilder(moves))

    result = jobs.export_pipeline_to_csv("moves")

    assert result.endswith("moves.csv")

    with open(result, encoding="utf-8") as f:
        lines = f.readlines()

    assert len(lines) == 3  # header + 2 moves


def test_export_pipeline_to_csv_raises_on_empty_builder_output(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "csv_output_folder", str(tmp_path))
    monkeypatch.setitem(jobs._BUILDERS, "moves", lambda: FakeBuilder([]))

    with pytest.raises(ValueError):
        jobs.export_pipeline_to_csv("moves")


def test_all_registered_pipelines_are_constructible():
    # Every factory should build a Builder without hitting the network -
    # PokemonDb*Source/StaticYaml*Source construction is itself side-effect
    # free, and get_cache_client()/RedisCacheClient's connection is lazy.
    for name, factory in jobs._BUILDERS.items():
        builder = factory()
        assert hasattr(builder, "build"), "pipeline '{0}' factory didn't return a Builder".format(name)
