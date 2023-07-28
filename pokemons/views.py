from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

import json


class PokemomView(APIView):
    """
    Pokemon view.
    """

    queryset = json.loads(
        open('pokemons_data.json', 'r').read()
    )

    def get(self, request: Request, number: str = None) -> Response:
        if number is None:
            return Response(self.queryset)
        if not number.isdigit():
            return Response(None)
        number = int(number) - 1
        if number >= 1010 or number < 0:
            return Response(None)
        return Response(self.queryset[number])
