"""Agent factory for web UI"""

from typing import Optional, Tuple
import streamlit as st


class AgentBuilderError(Exception):
    """Custom error for agent building"""
    pass


def build_agent(backend: str, model: str, prompt: str = "base") -> Tuple[Optional[object], Optional[str]]:
    """
    Build an AI agent for the web UI. Currently supports Ollama.

    Args:
        backend: "ollama" (for MVP)
        model: Model name (e.g., "mistral:7b")
        prompt: Prompt preset (e.g., "base", "concise", "adaptive")

    Returns:
        (agent, error_message) - agent is None if error, error_message is None if success
    """
    try:
        if backend == "ollama":
            from stratego.models.ollama_model import OllamaAgent
            agent = OllamaAgent(model_name=model, prompt_name=prompt)
            return agent, None

        else:
            return None, f"Unknown backend: {backend}. Currently only 'ollama' is supported."

    except ImportError as e:
        error_msg = f"Backend '{backend}' not installed: {str(e)}"
        return None, error_msg
    except Exception as e:
        error_msg = f"Failed to build agent: {str(e)}"
        return None, error_msg


def build_mock_agent() -> object:
    """
    Build a mock agent for testing (always returns first legal move).
    Useful for testing UI without real LLM.
    """
    class MockAgent:
        def __init__(self):
            self.model_name = "mock"
        
        def __call__(self, observation: str) -> str:
            """Extract and return first legal move from observation"""
            from stratego.utils.parsing import extract_legal_moves
            
            legal_moves = extract_legal_moves(observation)
            if legal_moves:
                return legal_moves[0]
            return "[A0 B0]"  # Fallback
    
    return MockAgent()


def validate_agent_config(backend: str, model: str, prompt: str) -> Optional[str]:
    """
    Validate agent configuration without building the full agent.
    Returns error message if invalid, None if valid.
    """
    if not backend:
        return "Backend is required"
    if not model:
        return "Model name is required"
    if not prompt:
        return "Prompt preset is required"

    if backend != "ollama":
        return f"Only 'ollama' backend is currently supported. Got: {backend}"

    if prompt not in ["base", "concise", "adaptive"]:
        return f"Unknown prompt: {prompt}"

    return None
