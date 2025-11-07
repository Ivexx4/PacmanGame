"""
Pacote MiniProjetoCRP.

Este módulo inicial (package initializer) expõe a API pública do pacote:
Map, Pacman, Ghost e PacmanGame.

Uso:
    from src import Map, Pacman, Ghost, PacmanGame
"""
# Exportar classes públicas do pacote
from .pacman import Pacman
from .ghost import Ghost
from .pacman_game import PacmanGame

__all__ = [ "Pacman", "Ghost", "PacmanGame"]
__version__ = "0.1.0"

