"""Game configuration constants for web UI"""

from dataclasses import dataclass
from typing import Dict, Tuple

# Game mode definitions (MVP: Standard only, Duel/Custom in Phase 2)
GAME_MODES = {
    "Standard (10x10)": {
        "env_id": "Stratego-v0",
        "size": 10,
        "display_name": "Standard"
    }
}

# Default AI models (Ollama only for MVP)
DEFAULT_MODELS = {
    "Ollama": {
        "mistral:7b": "mistral:7b",
        "gemma3:1b": "gemma3:1b",
        "phi3:3.8b": "phi3:3.8b",
    }
}

# Prompt presets
PROMPT_PRESETS = ["base", "concise", "adaptive"]

# Default prompt
DEFAULT_PROMPT = "base"

# Default agent backend (Ollama for MVP)
DEFAULT_AGENT_BACKEND = "ollama"

# Default model for new games
DEFAULT_MODEL = "mistral:7b"

# Game UI settings
BOARD_REFRESH_INTERVAL = 0.1  # seconds
DEFAULT_GAME_TIMEOUT = 300  # 5 minutes per move
MAX_MOVE_HISTORY_DISPLAY = 10  # Show last N moves

# Piece representations in board (ASCII only for compatibility)
PIECE_DISPLAY = {
    "fl": "F",  # Flag
    "bm": "B",  # Bomb
    "ms": "M",  # Marshal
    "gn": "G",  # General
    "mn": "N",  # Miner
    "sc": "S",  # Scout
    "sp": "P",  # Spy
    "sr": "R",  # Sergeant
    "lt": "L",  # Lieutenant
    "cp": "C",  # Captain
    "mx": "X",  # Unknown enemy
    ".": ".",   # Empty
    "~": "~",   # Lake
}


def get_game_config(mode_name: str) -> Dict:
    """Get game configuration by mode name"""
    return GAME_MODES.get(mode_name, GAME_MODES["Standard (10x10)"])


def get_env_id(mode_name: str) -> str:
    """Get environment ID from mode name"""
    config = get_game_config(mode_name)
    return config["env_id"]


def get_board_size(mode_name: str) -> int:
    """Get board size from mode name"""
    config = get_game_config(mode_name)
    return config["size"]


def get_available_models(backend: str = DEFAULT_AGENT_BACKEND) -> list:
    """Get available models for selected backend (Ollama only for MVP)"""
    if backend == "ollama":
        return list(DEFAULT_MODELS["Ollama"].keys())
    return []


def format_piece_for_display(piece_code: str) -> str:
    """Convert piece code to display emoji"""
    return PIECE_DISPLAY.get(piece_code, piece_code)
