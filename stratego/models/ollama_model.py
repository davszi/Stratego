import os
import random

import re
from typing import Optional, Tuple

from langchain_ollama import ChatOllama
import requests

from .base import AgentLike
from ..utils.parsing import (
    extract_legal_moves, slice_board_and_moves, strip_think, MOVE_RE, extract_forbidden
)


# I seperated Prompts from the code
from ..prompts import PromptPack, get_prompt_pack

# 🧩 Import strategies
from ..strategies.base import Strategy
from ..strategies.aggressive_strategy import AggressiveStrategy
from ..strategies.defensive_strategy import DefensiveStrategy
from ..strategies.random_move import RandomStrategy


class OllamaAgent(AgentLike):
    def __init__(
        self,
        model_name: str,
        system_prompt: Optional[str] = None,
        host: Optional[str] = None,
        prompt_pack: Optional[PromptPack | str] = None,
        strategy: Optional[Strategy] = None,
        **kwargs,
    ):
        self.model_name = model_name

        self.STRATEGIC_GUIDANCE = """
You are a skilled Stratego player.
You must choose the SINGLE best legal move from the given board, legal moves, forbidden moves, and move history.

GENERAL RULES:
1. Output EXACTLY ONE MOVE in the form [A0 B0].
2. NEVER output explanations, commentary, or reasoning.
3. Try to choose a move that would be legal in Stratego rules.
4. NEVER repeat a previous move unless it creates a tactical advantage (capture, reveal, escape).
5. AVOID back-and-forth oscillations (e.g., A5->A6 then A6->A5).
6. It would be considered a SERIOUS MISTAKE, which leads you to lose the game, to attempt illegal moves such as moving a Flag or Bomb, moving in an impossible way, moving upon its own pieces, or trying to move opponent's pieces.

STRATEGIC PRINCIPLES:
1. Avoid random or pointless shuffling of pieces.
2. Prefer moves that improve board position, uncover information, or apply pressure.
3. Avoid moving high-value officers (Marshal, General, Colonel) blindly into unknown pieces.
4. Prefer advancing Scouts for reconnaissance.
5. Avoid moving bombs unless revealed and forced.
6. Do NOT walk pieces next to the same unknown piece repeatedly without purpose.
7. Do NOT afraid to sacrifice low-rank pieces for information gain.

CAPTURE & SAFETY RULES:
1. If you can capture a known weaker enemy piece safely, prefer that move.
2. NEVER attack a higher-ranked or unknown piece with a valuable piece unless strategically justified.
3. If the enemy piece is revealed as weaker, press the advantage.
4. If your piece is threatened, retreat or reposition instead of repeating the last move.

USE OF HISTORY:
1. Avoid repeating cycles recognized in the history (e.g., A->B->A->B).
2. Track revealed enemy pieces from history and use rank knowledge:
   - If they moved, they are not Bombs or Flags.
   - If they captured, infer their rank and avoid attacking with weaker pieces.
3. If an enemy repeatedly retreats from your piece, continue safe pressure.

POSITIONING RULES:
1. Advance pieces that have strategic value while keeping your formation stable.
2. Keep bombs guarding high-value territory; avoid unnecessary bomb movement.
3. Push on flanks where the opponent retreats often.
4. Maintain escape squares for your high-ranking leaders.

ENDGAME LOGIC:
1. Prioritize discovering and attacking the opponent's flag location.
2. Secure safe paths for Miners to remove bombs.
3. In endgame, prioritize mobility and avoid blockades caused by your own pieces.

CHOOSE THE BEST MOVE:
Evaluate all legal moves and pick the one that:
- improves position, OR
- pressures an opponent safely, OR
- increases information, OR
- avoids known traps or loops, OR
- ensures safety of valuable pieces.

Output ONLY one legal move in the exact format [A0 B0]. Nothing else.
"""
#         self.VALIDATION_GUIDANCE = """
# You are validating a Stratego move. Decide if the move obeys Stratego rules given the board and history.
# Rules to enforce:
# - Pieces cannot move into lakes or off-board.
# - Immovable pieces (Bomb, Flag) cannot move.
# - A piece cannot capture its own piece.
# - Only Scouts can move more than one square in straight lines; others move exactly one square orthogonally.
# - No diagonal movement.
# - Respect revealed information from history (if it moved before, it is not a Bomb/Flag).
# - If an 'Available Moves:' list is present, moves not in that list are almost always invalid.
# - If a 'FORBIDDEN' list is present, those moves are invalid.
# - On small custom boards (size <= 5), there are NO lakes unless the board explicitly shows '~'. If you do not see '~', assume no lakes exist.

# Respond with either:
# - VALID
# - INVALID: <short reason>
# """
        if isinstance(prompt_pack, str) or prompt_pack is None:
            self.prompt_pack: PromptPack = get_prompt_pack(prompt_pack)
        else:
            self.prompt_pack = prompt_pack



        if system_prompt is not None:
            self.system_prompt = system_prompt
        else:
            # if there is already an existing updated prompt, we use that one
            prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "current_prompt.txt")
            if os.path.exists(prompt_path):
                with open(prompt_path, "r", encoding="utf-8") as f:
                    self.system_prompt = f.read()
            else:
                self.system_prompt = self.prompt_pack.system
                
                
        self.initial_prompt = self.system_prompt
        # Setup Ollama client
        base_url = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        model_kwargs = {
            "temperature": kwargs.pop("temperature", 0.1),
            "top_p": kwargs.pop("top_p", 0.9),
            "repeat_penalty": kwargs.pop("repeat_penalty", 1.05),
            "num_predict": kwargs.pop("num_predict", 24),
            **kwargs,
        }
        
        # Only print connection message if explicitly enabled (for CLI use, not web UI)
        # print("🚀 Connecting to Ollama at:", base_url)
        self.client = ChatOllama(model=model_name, base_url=base_url, model_kwargs=model_kwargs)
        
        # Simple move history tracking
        self.move_history = []
        self.player_id = None

    def set_move_history(self, history):
        """Set the recent move history for this agent."""
        self.move_history = history

    # def _validate_move(self, context: str, move: str) -> Tuple[bool, str]:
    #     """Ask the LLM to self-check legality based on board + history."""
    #     prompt = (
    #         self.VALIDATION_GUIDANCE
    #         + "\n\nBOARD + HISTORY CONTEXT:\n"
    #         + context
    #         + f"\n\nCANDIDATE MOVE: {move}\nRespond strictly with VALID or INVALID and a reason."
    #     )
    #     verdict = self._llm_once(prompt)
    #     if not verdict:
    #         return False, "empty validation response"
    #     verdict_upper = verdict.strip().upper()
    #     if verdict_upper.startswith("VALID"):
    #         return True, ""
    #     if verdict_upper.startswith("INVALID"):
    #         reason = verdict.split(":", 1)[1].strip() if ":" in verdict else "marked invalid"
    #         return False, reason
    #     return False, f"unrecognized verdict: {verdict[:60]}"

    # Run one LLM call
    def _llm_once(self, prompt: str) -> str:

        """Send request directly to Ollama REST API (fixes Windows LangChain bug)."""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=300
            )
            if response.status_code == 200:
                data = response.json()
                return (data.get("response") or "").strip()
            else:
                print(f"Ollama returned HTTP {response.status_code}: {response.text}")
                return ""
        except Exception as e:
            print(f"Ollama request failed: {e}")
            return ""

    def __call__(self, observation: str) -> str:
        # Build context
        slim = slice_board_and_moves(observation)
        available_moves = set(extract_legal_moves(observation))
        forbidden_moves = set(extract_forbidden(observation))

        prompt_history_lines = []
        for line in observation.splitlines():
            if line.startswith("Turn ") or "played[" in line:
                prompt_history_lines.append(line)
        history = "\n".join(prompt_history_lines)
        full_context = slim + ("\n\nMOVE HISTORY:\n" + history if history else "")

        def _detect_board_size(obs: str) -> Optional[int]:
            """Infer board size from numeric header (e.g., '0 1 2 3')."""
            header_re = re.compile(r"^\s*0(\s+\d+)+\s*$")
            lines = obs.splitlines()
            for i in range(len(lines) - 1, -1, -1):
                if header_re.match(lines[i].strip()):
                    nums = [int(n) for n in lines[i].split() if n.isdigit()]
                    if nums:
                        return max(nums) + 1
            return None

        def _build_board_map(obs: str) -> dict[str, str]:
            size_local = _detect_board_size(obs)
            if not size_local:
                return {}
            lines = obs.splitlines()
            header_idx = None
            header_re = re.compile(r"^\s*0(\s+\d+)+\s*$")
            for i in range(len(lines)):
                if header_re.match(lines[i].strip()):
                    header_idx = i
                    break
            if header_idx is None:
                return {}
            board_map: dict[str, str] = {}
            # Expect size_local lines after header
            for r in range(size_local):
                line_idx = header_idx + 1 + r
                if line_idx >= len(lines):
                    break
                parts = lines[line_idx].split()
                if not parts:
                    continue
                row_label = parts[0]
                cells = parts[1:]
                if len(cells) < size_local:
                    continue
                for c in range(size_local):
                    pos = f"{row_label.upper()}{c}"
                    board_map[pos] = cells[c]
            return board_map

        board_map = _build_board_map(observation)

        # >>> THE CRITICAL FIX <<<
        guidance = (
            self.STRATEGIC_GUIDANCE
            + "\n\n"
            + self.prompt_pack.guidance(full_context)
        )

        recent_moves = set()
        if len(self.move_history) >= 2:
            recent_moves = {m["move"] for m in self.move_history[-2:]}
        
        last_error = None
        last_raw: str = ""
        invalid_memory = []
        BARE_MOVE_RE = re.compile(r"\b([A-Z]\d+)\s+([A-Z]\d+)\b")

        def _extract_move(raw: str):
            m = MOVE_RE.search(raw or "")

            if m:
                return m.group(0)
            m2 = BARE_MOVE_RE.search(raw or "")
            if m2:
                return f"[{m2.group(1)} {m2.group(2)}]"
            return None

        # generation + self-validation loop (4 attempts max)
        for attempt in range(4):
            decorated_guidance = guidance
            if invalid_memory:
                decorated_guidance += "\n\nPreviously invalid moves (avoid these):\n" + "\n".join(invalid_memory)

            raw = self._llm_once(decorated_guidance)
            last_raw = raw or last_raw
            if not raw:
                last_error = "empty response (timeout or HTTP error)"
                continue

            mv = _extract_move(raw)
            if not mv:
                last_error = f"no move found in response: {raw[:80]!r}"
                continue

            # Geometric sanity check: block diagonals and multi-step moves from non-Scout pieces
            try:
                src, dst = mv.strip("[]").split()
                sr, sc = ord(src[0]) - 65, int(src[1:])
                dr, dc = ord(dst[0]) - 65, int(dst[1:])
                drow = abs(dr - sr)
                dcol = abs(dc - sc)
                src_token = board_map.get(src, "")
                # Block moving empty/unknown/lake squares
                if src_token in {"", ".", "?", "~"}:
                    invalid_memory.append(f"{mv} (source not movable)")
                    last_error = "source not movable"
                    continue
                # Diagonal
                if drow > 0 and dcol > 0:
                    invalid_memory.append(f"{mv} (diagonal not allowed)")
                    last_error = "diagonal"
                    continue
                # Multi-step non-Scout
                if drow + dcol > 1:
                    is_scout = src_token.upper() in {"SC", "SCOUT"}
                    if not is_scout:
                        invalid_memory.append(f"{mv} (non-Scout multi-step)")
                        last_error = "non-Scout multi-step"
                        continue
            except Exception:
                pass

            # quick deterministic veto using env-provided lists
            if available_moves and mv not in available_moves:
                invalid_memory.append(f"{mv} (not in Available Moves)")
                last_error = f"{mv} not in Available Moves"
                print(f"   LLM proposed move not in Available Moves: {mv}")
                continue
            if mv in forbidden_moves:
                invalid_memory.append(f"{mv} (in FORBIDDEN)")
                last_error = f"{mv} in FORBIDDEN"
                print(f"   LLM proposed forbidden move {mv}")
                continue

            if mv in recent_moves and len(recent_moves) > 0:
                last_error = f"repeated move {mv}"
                print(f"   LLM proposed recent move {mv}, trying alternatives...")
                continue

            if available_moves:
                return mv

        def _first_valid_from_list(candidates):
            for mv in candidates:
                if available_moves and mv not in available_moves:
                    # print(f"   Fallback move not in Available Moves: {mv}")
                    continue
                if mv in forbidden_moves:
                    # print(f"   Fallback forbidden move: {mv}")
                    continue
                if mv in recent_moves and len(recent_moves) > 0:
                    continue
                if available_moves:
                    return mv
                # is_valid, reason = self._validate_move(full_context, mv)
                # if is_valid:
                #     return mv
                # print(f"   Fallback invalid move {mv}: {reason}")
            return None

        if last_raw:
            candidates = MOVE_RE.findall(last_raw or "")
            if candidates:
                mv = _first_valid_from_list(candidates)
                if mv:
                    return mv
                    
        # Try to pick a random valid move from available moves
        obs_moves = MOVE_RE.findall(observation)
        if obs_moves:
            mv = _first_valid_from_list(obs_moves)
            if mv:
                return mv
            non_recent = [mv for mv in obs_moves if mv not in recent_moves]
            if non_recent:
                return random.choice(non_recent)
            return random.choice(obs_moves)

        print(f"[AGENT] {self.model_name} failed to produce valid move after retries.")
        if last_error:
            print(f"   Last error: {last_error}")

        return ""
