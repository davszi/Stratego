"""Game controller - wrapper around StrategoEnv and AI agents"""

from typing import Tuple, Optional, List, Dict, Any
from stratego.env.stratego_env import StrategoEnv
from stratego.utils.parsing import extract_legal_moves, extract_forbidden, extract_board_block_lines
from stratego.game_logger import GameLogger
import os


class GameController:
    """Thin wrapper around StrategoEnv for web UI."""
    
    def __init__(self, env_id: str, size: int, ai_agent: object, prompt_name: str = "base"):
        self.env = StrategoEnv(env_id=env_id, size=size)
        self.env_id = env_id
        self.ai_agent = ai_agent
        self.prompt_name = prompt_name
        self.size = size
        self.human_player_id = 0
        self.ai_player_id = 1
        self.move_history = {0: [], 1: []}
        self.game_done = False
        self.game_info = {}
        self.current_player_id = None
        self.current_observation = ""
        self.game_logger = None
        self.logs_dir = os.path.join(os.path.dirname(__file__),"..","..","logs","games")
        os.makedirs(self.logs_dir, exist_ok=True)
    
    def reset(self) -> Tuple[int, str]:
        self.env.reset(num_players=2)
        self.move_history = {0: [], 1: []}
        self.game_done = False
        self.game_info = {}
        self.game_logger = GameLogger(out_dir=os.path.join(self.logs_dir, ".."), game_type=self.env_id, board_size=self.size, prompt_name=self.prompt_name)
        return self.get_current_player()
    
    def get_current_player(self) -> Tuple[int, str]:
        self.current_player_id, self.current_observation = self.env.get_observation()
        return self.current_player_id, self.current_observation
    
    def get_legal_moves(self, observation: Optional[str] = None) -> List[str]:
        obs_to_use = observation or self.current_observation
        if not obs_to_use:
            return []
        legal = extract_legal_moves(obs_to_use)
        forbidden = set(extract_forbidden(obs_to_use))
        result = [m for m in legal if m not in forbidden]
        return result if result else legal
    
    def get_board_display(self, observation: Optional[str] = None) -> str:
        obs_to_use = observation or self.current_observation
        if not obs_to_use:
            return "No board state available"
        try:
            board_lines = extract_board_block_lines(obs_to_use, self.size)
            return "\n".join(board_lines)
        except Exception as e:
            return f"Error rendering board: {str(e)}"
    
    def execute_move(self, move_str: str) -> Tuple[bool, Dict[str, Any]]:
        if self.game_done:
            return True, {"error": "Game already finished"}
        try:
            done, info = self.env.step(action=move_str)
            move_info = {"player": self.current_player_id, "move": move_str, "done": done, "info": info}
            self.move_history[self.current_player_id].append(move_info)
            if self.game_logger:
                try:
                    self.game_logger.log_move(turn=sum(len(v) for v in self.move_history.values()), player=self.current_player_id, move=move_str, model_name=getattr(self.ai_agent,"model_name","human"), prompt_name=self.prompt_name, game_done=done, game_info=info)
                except:
                    pass
            if done:
                self.game_done = True
                self.game_info = info
            return done, info
        except Exception as e:
            return True, {"error": f"Move execution error: {str(e)}"}
    
    def get_ai_move(self, observation: Optional[str] = None) -> Tuple[str, Optional[str]]:
        obs_to_use = observation or self.current_observation
        if not obs_to_use:
            return "[A0 B0]", "No observation available"
        try:
            move = self.ai_agent(obs_to_use)
            if not move:
                legal_moves = self.get_legal_moves(obs_to_use)
                move = legal_moves[0] if legal_moves else "[A0 B0]"
            return str(move).strip(), None
        except Exception as e:
            legal_moves = self.get_legal_moves(obs_to_use)
            return (legal_moves[0] if legal_moves else "[A0 B0]"), f"AI error: {str(e)}"
    
    def close(self) -> Tuple[Dict, Dict]:
        try:
            rewards, info = self.env.close()
            if self.game_logger:
                try:
                    winner = info.get("winner") if info else None
                    result = info.get("result") if info else None
                    self.game_logger.finalize_game(winner=winner, result=result)
                except:
                    pass
            return rewards, info
        except Exception as e:
            return {}, {"error": str(e)}
    
    def is_human_turn(self) -> bool:
        return self.current_player_id == self.human_player_id
    
    def is_ai_turn(self) -> bool:
        return self.current_player_id == self.ai_player_id
    
    def get_turn_count(self) -> int:
        return sum(len(v) for v in self.move_history.values())
    
    def get_move_history_display(self, limit: int = None) -> List[str]:
        """Get move history in CHRONOLOGICAL order (alternating: You, AI, You, AI...)

        Args:
            limit: Max moves to return. None = return all moves
        """
        moves = []
        max_moves = max(len(self.move_history[0]), len(self.move_history[1]))

        # Interleave moves from both players chronologically
        for i in range(max_moves):
            # Your move (Player 0)
            if i < len(self.move_history[0]):
                m = self.move_history[0][i]
                moves.append(f"You: {m['move']}")

            # AI move (Player 1)
            if i < len(self.move_history[1]):
                m = self.move_history[1][i]
                moves.append(f"AI: {m['move']}")

        # Return all moves (or last 'limit' if specified)
        if limit:
            return moves[-limit:]
        return moves
