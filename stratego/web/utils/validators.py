"""Validators for move input and game state"""

import re
from typing import Tuple, Optional


# Move format: [A0 B0] where A-J are rows and 0-9 are columns
MOVE_PATTERN = r'^\s*\[\s*([A-J])(\d+)\s+([A-J])(\d+)\s*\]\s*$'


def validate_move_format(move_str: str, board_size: int = 10) -> Tuple[bool, Optional[str]]:
    """
    Validate move format and board boundaries.
    
    Args:
        move_str: Move string (e.g., "[A0 B0]")
        board_size: Board size (4-10)
    
    Returns:
        (is_valid, error_message) - error_message is None if valid
    """
    if not move_str or not isinstance(move_str, str):
        return False, "Move must be a non-empty string"
    
    move_str = move_str.strip().upper()
    
    match = re.match(MOVE_PATTERN, move_str)
    if not match:
        return False, "Invalid format. Use [A0 B0] where A-J are rows and 0-9 are columns"
    
    src_row, src_col, dst_row, dst_col = match.groups()
    src_col = int(src_col)
    dst_col = int(dst_col)
    
    # Check row bounds
    src_row_idx = ord(src_row) - ord('A')
    dst_row_idx = ord(dst_row) - ord('A')
    
    if src_row_idx >= board_size or dst_row_idx >= board_size:
        return False, f"Row out of bounds (board size: {board_size}x{board_size})"
    
    # Check column bounds
    if src_col >= board_size or dst_col >= board_size or src_col < 0 or dst_col < 0:
        return False, f"Column out of bounds (board size: {board_size}x{board_size})"
    
    # Source and destination must be different
    if src_row == dst_row and src_col == dst_col:
        return False, "Source and destination must be different"
    
    return True, None


def normalize_move(move_str: str) -> str:
    """
    Normalize move string to standard format: [A0 B0]
    
    Args:
        move_str: Raw move string from user
    
    Returns:
        Normalized move string in uppercase
    """
    if not move_str:
        return ""
    
    move_str = move_str.strip().upper()
    
    # Try to parse and reformat
    match = re.match(MOVE_PATTERN, move_str)
    if match:
        src_row, src_col, dst_row, dst_col = match.groups()
        return f"[{src_row}{src_col} {dst_row}{dst_col}]"
    
    return move_str


def extract_move_coordinates(move_str: str) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """
    Extract coordinates from move string.
    
    Args:
        move_str: Move string (e.g., "[A0 B0]")
    
    Returns:
        ((src_row, src_col), (dst_row, dst_col)) or None if invalid
    """
    move_str = move_str.strip().upper()
    match = re.match(MOVE_PATTERN, move_str)
    
    if not match:
        return None
    
    src_row, src_col, dst_row, dst_col = match.groups()
    src_col = int(src_col)
    dst_col = int(dst_col)
    
    src_row_idx = ord(src_row) - ord('A')
    dst_row_idx = ord(dst_row) - ord('A')
    
    return ((src_row_idx, src_col), (dst_row_idx, dst_col))


def is_valid_move_string(move_str: str, legal_moves: list, board_size: int = 10) -> Tuple[bool, Optional[str]]:
    """
    Complete validation: format + legal moves list.
    
    Args:
        move_str: Move string from user
        legal_moves: List of legal moves from observation
        board_size: Board size
    
    Returns:
        (is_valid, error_message)
    """
    # First check format
    is_valid_format, format_error = validate_move_format(move_str, board_size)
    if not is_valid_format:
        return False, format_error
    
    # Normalize and check against legal moves
    normalized_move = normalize_move(move_str)
    
    if legal_moves and normalized_move not in legal_moves:
        return False, f"Move {normalized_move} is not in legal moves"
    
    return True, None
