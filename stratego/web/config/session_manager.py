"""Session state management for Streamlit"""

import streamlit as st
from typing import Any, Optional


class SessionManager:
    """Manage Streamlit session state across reruns"""

    @staticmethod
    def init():
        """Initialize default session state values"""
        if "current_screen" not in st.session_state:
            st.session_state.current_screen = 0  # Welcome screen

        if "game_controller" not in st.session_state:
            st.session_state.game_controller = None

        if "game_mode" not in st.session_state:
            st.session_state.game_mode = "Standard (10x10)"

        if "ai_agent" not in st.session_state:
            st.session_state.ai_agent = None

        if "ai_config" not in st.session_state:
            st.session_state.ai_config = {
                "backend": "huggingface",
                "model": "mistral:7b",
                "prompt": "base"
            }

        if "game_active" not in st.session_state:
            st.session_state.game_active = False

        if "game_log" not in st.session_state:
            st.session_state.game_log = []

        if "last_error" not in st.session_state:
            st.session_state.last_error = None

        if "last_move" not in st.session_state:
            st.session_state.last_move = None

        if "current_observation" not in st.session_state:
            st.session_state.current_observation = ""

    @staticmethod
    def set_game_controller(controller: Any) -> None:
        """Set the game controller in session state"""
        st.session_state.game_controller = controller

    @staticmethod
    def get_game_controller() -> Optional[Any]:
        """Get game controller from session state"""
        return st.session_state.get("game_controller")

    @staticmethod
    def set_screen(screen_number: int) -> None:
        """Set current screen"""
        st.session_state.current_screen = screen_number

    @staticmethod
    def get_screen() -> int:
        """Get current screen"""
        return st.session_state.get("current_screen", 0)

    @staticmethod
    def set_ai_config(backend: str, model: str, prompt: str) -> None:
        """Set AI configuration"""
        st.session_state.ai_config = {
            "backend": backend,
            "model": model,
            "prompt": prompt
        }

    @staticmethod
    def get_ai_config() -> dict:
        """Get AI configuration"""
        return st.session_state.get("ai_config", {})

    @staticmethod
    def set_error(error_message: str) -> None:
        """Set the last error message"""
        st.session_state.last_error = error_message

    @staticmethod
    def get_error() -> Optional[str]:
        """Get the last error message"""
        return st.session_state.get("last_error")

    @staticmethod
    def clear_error() -> None:
        """Clear error message"""
        st.session_state.last_error = None

    @staticmethod
    def set_game_mode(mode: str) -> None:
        """Set selected game mode"""
        st.session_state.game_mode = mode

    @staticmethod
    def get_game_mode() -> str:
        """Get selected game mode"""
        return st.session_state.get("game_mode", "Standard (10x10)")

    @staticmethod
    def reset_all() -> None:
        """Reset all session state to defaults (for new game)"""
        st.session_state.game_controller = None
        st.session_state.game_active = False
        st.session_state.game_log = []
        st.session_state.last_error = None
        st.session_state.last_move = None
        st.session_state.current_observation = ""
        st.session_state.current_screen = 0
