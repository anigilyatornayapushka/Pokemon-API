from django.core.management.base import BaseCommand

import typing as t
import requests as req
import json
import re

import bs4


Bs4Tag = bs4.element.Tag
Bs4Data = bs4.BeautifulSoup


class Command(BaseCommand):
    """
    Find data about pokemons.
    """

    URL: str = 'https://www.pokemon.com/ru/pokedex/%s'
    ROOT: str = 'http://127.0.0.1:8000/'

    def handle(self, *args: t.Any, **kwargs: t.Any):
        """Generate data."""
        all_pokemons: list = []
        for idx in range(1, 1011):
            pokemon: dict = {}

            response: req.Response = req.get(self.URL % idx)
            if response.status_code != 200:
                all_pokemons.append(None)
                continue

            data: Bs4Data = bs4.BeautifulSoup(response.text, 'lxml')
            result: Bs4Tag

            # Search number and name of pokemon
            result = data.find(
                class_='pokedex-pokemon-pagination-title'
            ).find('div')
            res               = re.findall(r'\s*([^\s]*)', result.text)
            pokemon['name']   = res[0]
            pokemon['number'] = idx

            # Search source of pokemon image
            result = data.find(class_='profile-images').find('img')
            pokemon['img'] = result.get('src')

            # Search types of pokemon
            result = data.find(
                class_='dtm-type'
            ).find('ul').findAll('li')
            pokemon['type'] = []
            for pokemon_type in result:
                pokemon['type'].append(
                    pokemon_type.find('a').text
                )

            # Search weakness types of pokemon
            result = data.find(
                class_='dtm-weaknesses'
            ).find('ul').findAll('li')
            pokemon['type_weaknesses'] = []
            for pokemon_type in result:
                type_weakness = pokemon_type.find('span').text
                pokemon['type_weaknesses'].append(
                    re.match(r'[^\s]*', type_weakness)[0]
                )

            # Search evolutions
            result = data.find(class_='section pokedex-pokemon-evolution').find(
                'ul'
            ).findAll('li')
            pokemon['evolutions'] = []
            for evol in result:
                number = evol.find(class_='pokemon-number')
                if not number:
                    continue
                pokemon_number = re.findall(r'\d+', number.text)[0]
                pokemon['evolutions'].append(
                    self.ROOT + 'api/v1/pokemons/' + pokemon_number
                )

            # Search stats information
            result = data.findAll('li', class_='meter')
            pokemon['stats'] = {
                'HP': int(result[0].get('data-value')),
                'Atack': int(result[1].get('data-value')),
                'Defense': int(result[2].get('data-value')),
                'Special Atack': int(result[3].get('data-value')),
                'Special Defense': int(result[4].get('data-value')),
                'Speed': int(result[5].get('data-value'))
            }

            # Search other information
            pokemon['information'] = {}

            result = data.find(
                class_='version-descriptions active'
            ).find(class_='version-x active').text
            description = re.findall(r'\s*([^\n]*)', result)[0]

            result = data.find(class_='column-7').findAll('li')
            for i in range(2):
                title = result[i].find(class_='attribute-title').text
                value = result[i].find(class_='attribute-value').text
                pokemon['information'][title] = value
            pokemon['information']['description'] = description

            all_pokemons.append(pokemon)

        with open('pokemon_data.json', 'w') as file:
            file.write(
                json.dumps(all_pokemons)
            )
