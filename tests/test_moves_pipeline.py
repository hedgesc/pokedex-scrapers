from pokemondb_net_scrapers.moves_pipeline import html as html_module
from pokemondb_net_scrapers.moves_pipeline.all_moves_scraper import AllMovesScraper


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
  </tbody>
</table>
"""


def test_all_moves_scraper_lists_moves(monkeypatch):
    monkeypatch.setattr(html_module.web, "getHtml", lambda url: ALL_MOVES_HTML)

    moves = AllMovesScraper("https://example.com/move/all").list_moves()

    assert len(moves) == 1
    assert moves[0].name == "Tackle"
    assert moves[0].nameId == "tackle"
    assert moves[0].type == "Normal"
    assert moves[0].category == "Physical"
    assert moves[0].power == "40"
    assert moves[0].moveId == 0
