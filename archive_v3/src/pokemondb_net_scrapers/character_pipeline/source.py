from typing import Protocol, runtime_checkable

from pokemondb_net_scrapers.models.character import Character


@runtime_checkable
class CharacterSource(Protocol):
    """Where CharacterBuilder gets its data from. Implement this once per
    site/data-source; CharacterBuilder itself never talks HTML.
    """

    def list_seed_characters(self) -> list[Character]:
        """Scrape a listing page and return one seed Character per species,
        populated with whatever that page provides (e.g. name, nameId,
        thumbnail, types, generation). Detail fields are left at their
        model defaults - build_character_variants() fills those in.
        """
        ...

    def build_character_variants(self, seed: Character) -> list[Character]:
        """Scrape the seed's detail page and return one fully-populated
        Character per variant found there. Normally this is a single
        Character, but a species with alternate forms (Mega evolutions,
        regional forms, etc.) yields one Character per form.

        Implementations must give every returned Character a nameId that is
        unique across the whole run - callers cache by nameId, so alternate
        forms need a nameId distinct from their base form's (and from each
        other's).
        """
        ...
