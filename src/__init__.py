"""
Pacote MiniProjetoCRP.

Este módulo inicial (package initializer) expõe a API pública do pacote:
Pacman, PacmanGame, e as classes de Ghost.

Uso:
    from src import Pacman, PacmanGame, HunterGhost
"""
# Exportar classes públicas do pacote
from .pacman import Pacman
from .ghost import BaseGhost, HunterGhost, AmbusherGhost, StrategicGhost
from .pacman_game import PacmanGame

__all__ = [
    "Pacman", 
    "PacmanGame", 
    "BaseGhost", 
    "HunterGhost", 
    "AmbusherGhost", 
    "StrategicGhost"
]
__version__ = "0.1.0"
