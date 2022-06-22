from ..classes.character_dex_move import CharacterDexMove
from .pages.character import *

def scrapeAllCharacterMoves(character):
  result = []
  parser = getCharacterParser(character)
  
  gens = scrapeMoveGenerations(parser)
  for g in gens:
    moves_parser = getCharacterMovesParser(character, g)
    
    dex_tabs = scrapeMovesTabs(moves_parser)
    for tab in dex_tabs:
      moves_panel = moves_parser.select_one(tab.panelId)
      
      # moves are sorted by power and learned by id descending
      index = 0
      moves = scrapePanelForMoves(moves_panel)
      for m in moves:
        dcm = CharacterDexMove(character.characterId, tab.name, g, m)
        
        if index < 4:
          dcm.isSuggested = True

        result.append(dcm)
        index += 1

  return result