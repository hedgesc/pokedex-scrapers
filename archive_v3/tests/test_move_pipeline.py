import pytest
from bs4 import BeautifulSoup

from pokemondb_net_scrapers.config import CacheConfig
from pokemondb_net_scrapers.interfaces import CacheClient
from pokemondb_net_scrapers.models.move import Move
from pokemondb_net_scrapers.move_pipeline import _pokemondb_html as html_module
from pokemondb_net_scrapers.move_pipeline.builder import MoveBuilder
from pokemondb_net_scrapers.move_pipeline.pokemondb_source import PokemonDbMoveSource
from pokemondb_net_scrapers.move_pipeline.source import MoveSource


def make_tag(html):
    return BeautifulSoup(html, "html.parser").find()


def make_move(name, nameId=None, **overrides):
    m = Move(name, nameId or name.lower(), "Normal", "Physical", "40", "100", "35", "Inflicts regular damage.", "—")

    for k, v in overrides.items():
        setattr(m, k, v)

    return m


# --- MoveBuilder ---------------------------------------------------------

class FakeMoveSource:
    def __init__(self, moves):
        self._moves = moves

    def list_moves(self):
        return self._moves


class RecordingCacheClient:
    def __init__(self, fail_for=frozenset()):
        self.calls = []
        self._fail_for = fail_for

    def set(self, key, value, ttl=None):
        if key in self._fail_for:
            raise RuntimeError("cache unavailable")

        self.calls.append((key, value, ttl))

    def get(self, key):
        for k, v, _ in self.calls:
            if k == key:
                return v

        return None


def make_builder(moves, cache=None, cache_config=None):
    source = FakeMoveSource(moves)
    cache = cache if cache is not None else RecordingCacheClient()
    return MoveBuilder(source, cache, cache_config), cache


def test_fake_move_source_satisfies_move_source_protocol():
    assert isinstance(FakeMoveSource([]), MoveSource)


def test_recording_cache_client_satisfies_cache_client_protocol():
    assert isinstance(RecordingCacheClient(), CacheClient)


def test_build_returns_list_of_moves():
    builder, _ = make_builder([make_move("Tackle")])

    result = builder.build()

    assert isinstance(result, list)
    assert all(isinstance(m, Move) for m in result)


def test_build_returns_empty_list_when_source_has_no_moves():
    builder, _ = make_builder([])
    assert builder.build() == []


def test_build_assigns_sequential_ids_in_source_order():
    tackle = make_move("Tackle")
    thunderbolt = make_move("Thunderbolt")

    builder, _ = make_builder([tackle, thunderbolt])
    result = builder.build()

    assert [m.moveId for m in result] == [1, 2]


def test_build_caches_name_id_to_move_id_with_default_prefix():
    builder, cache = make_builder([make_move("Tackle", nameId="tackle")])

    builder.build()

    assert cache.calls == [("moves:tackle", "1", None)]


def test_build_caches_every_move():
    tackle = make_move("Tackle", nameId="tackle")
    thunderbolt = make_move("Thunderbolt", nameId="thunderbolt")

    builder, cache = make_builder([tackle, thunderbolt])
    builder.build()

    assert cache.calls == [
        ("moves:tackle", "1", None),
        ("moves:thunderbolt", "2", None),
    ]


def test_build_uses_configured_cache_key_prefix():
    builder, cache = make_builder(
        [make_move("Tackle", nameId="tackle")],
        cache_config=CacheConfig(moves_key_prefix="m:"),
    )

    builder.build()

    assert cache.calls == [("m:tackle", "1", None)]


def test_build_passes_ttl_from_cache_config():
    builder, cache = make_builder(
        [make_move("Tackle")],
        cache_config=CacheConfig(ttl_seconds=3600),
    )

    builder.build()

    assert cache.calls[0][2] == 3600


def test_build_swallows_cache_errors_by_default():
    builder, _ = make_builder(
        [make_move("Tackle", nameId="tackle")],
        cache=RecordingCacheClient(fail_for={"moves:tackle"}),
    )

    result = builder.build()

    assert len(result) == 1


def test_build_raises_on_cache_error_when_configured():
    builder, _ = make_builder(
        [make_move("Tackle", nameId="tackle")],
        cache=RecordingCacheClient(fail_for={"moves:tackle"}),
        cache_config=CacheConfig(raise_on_cache_error=True),
    )

    with pytest.raises(RuntimeError):
        builder.build()


# --- _pokemondb_html: MoveRowTag / AllMovesPage --------------------------

ALL_MOVES_HTML = """
<table id="moves">
  <tbody>
    <tr>
      <td><a>Tackle</a></td>
      <td><a>Normal</a></td>
      <td><img title="Physical"></td>
      <td>40</td>
      <td>100</td>
      <td>35</td>
      <td></td>
      <td>Inflicts regular damage with no additional effect.</td>
      <td>—</td>
    </tr>
    <tr>
      <td><a>Growl</a></td>
      <td><a>Normal</a></td>
      <td><img title="Status"></td>
      <td>—</td>
      <td>100</td>
      <td>40</td>
      <td></td>
      <td>Lowers the target's Attack by one stage.</td>
      <td>100%</td>
    </tr>
  </tbody>
</table>
"""


def test_move_row_tag_selects_all_columns():
    row = make_tag(
        '<tr><td><a>Tackle</a></td><td><a>Normal</a></td><td><img title="Physical"></td>'
        "<td>40</td><td>100</td><td>35</td><td></td>"
        "<td>Inflicts regular damage.</td><td>—</td></tr>"
    )
    tag = html_module.MoveRowTag(row)

    assert tag.select_name() == "Tackle"
    assert tag.select_type() == "Normal"
    assert tag.select_category() == "Physical"
    assert tag.select_power() == "40"
    assert tag.select_accuracy() == "100"
    assert tag.select_pp() == "35"
    assert tag.select_effect() == "Inflicts regular damage."
    assert tag.select_probability() == "—"


def test_move_row_tag_missing_type_and_category_return_empty_string():
    row = make_tag(
        "<tr><td><a>Splash</a></td><td></td><td></td>"
        "<td>—</td><td>—</td><td>40</td><td></td>"
        "<td>Does nothing.</td><td>—</td></tr>"
    )
    tag = html_module.MoveRowTag(row)

    assert tag.select_type() == ""
    assert tag.select_category() == ""


def test_all_moves_page_selects_move_rows(monkeypatch):
    monkeypatch.setattr(html_module.web, "getHtml", lambda url: ALL_MOVES_HTML)

    page = html_module.AllMovesPage("https://example.com/move/all")
    rows = page.select_move_rows()

    assert [r.select_name() for r in rows] == ["Tackle", "Growl"]


# --- PokemonDbMoveSource --------------------------------------------------

def test_pokemondb_move_source_satisfies_move_source_protocol():
    assert isinstance(PokemonDbMoveSource(), MoveSource)


def test_pokemondb_move_source_list_moves(monkeypatch):
    monkeypatch.setattr(html_module.web, "getHtml", lambda url: ALL_MOVES_HTML)

    moves = PokemonDbMoveSource(all_moves_url="https://example.com/move/all").list_moves()

    assert [m.name for m in moves] == ["Tackle", "Growl"]
    assert moves[0].nameId == "tackle"
    assert moves[0].type == "Normal"
    assert moves[0].category == "Physical"
    assert moves[0].power == "40"
    assert moves[0].accuracy == "100"
    assert moves[0].pp == "35"
    assert moves[0].effect == "Inflicts regular damage with no additional effect."
    assert moves[0].probability == "—"
    assert moves[0].moveId == 0


def test_pokemondb_move_source_with_builder_end_to_end(monkeypatch):
    monkeypatch.setattr(html_module.web, "getHtml", lambda url: ALL_MOVES_HTML)

    builder, cache = make_builder(
        PokemonDbMoveSource(all_moves_url="https://example.com/move/all").list_moves()
    )
    moves = builder.build()

    assert [m.moveId for m in moves] == [1, 2]
    assert cache.calls == [
        ("moves:tackle", "1", None),
        ("moves:growl", "2", None),
    ]
