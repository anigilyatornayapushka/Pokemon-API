from django.urls import path

from .views import PokemomView


urlpatterns = [
    path('', PokemomView.as_view()),
    path('<str:number>', PokemomView.as_view())
]
