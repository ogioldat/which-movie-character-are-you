import dataclasses
import os
from typing import Any, Dict, List
import networkx as nx
import json


@dataclasses.dataclass
class Trait:
    alignment: int
    moralFlexibility: int
    loyalty: int
    riskTaking: int
    emotionalStability: int
    courage: int
    motivation: int
    charisma: int
    guilt: int
    logic_vs_emotion: int


@dataclasses.dataclass
class Character:
    character_name: str
    movie: str
    traits: Trait


def _parse_character(data_dict: Dict[str, Any]) -> Character:
    parsed_trait = Trait(**data_dict["traits"])

    return Character(
        character_name=data_dict["character_name"],
        movie=data_dict["movie"],
        traits=parsed_trait,
    )


def load_characters(json_chars) -> List[Character]:
    character_list: List[Character] = [_parse_character(d) for d in json_chars]

    return character_list


def build_chars_graph(data_path: str) -> nx.Graph:
    G = nx.Graph()
    
    file = open(data_path)
    data = json.loads(file.read())
    file.close()
    chars = load_characters(data)

    for char in chars:
        G.add_node(char.character_name, group="Character", color="#333333")
        for trait, weight in dataclasses.asdict(char.traits).items():
            G.add_node(trait, group="Trait", color="#ff5733")
            # G.add_edge(
            #     char.character_name, trait, weight=weight, title=f"Weight: {weight}"
            # )
            
    return G
