"""Interactive board component - Chess-like click-to-move interface"""
import streamlit as st
from stratego.utils.parsing import extract_legal_moves


# Piece emoji mapping
PIECE_EMOJI = {
    "fl": "🚩",  # Flag
    "bm": "💣",  # Bomb
    "ms": "👑",  # Marshal
    "gn": "⭐",  # General
    "mn": "⛏️",  # Miner
    "sc": "🏃",  # Scout
    "sp": "🕵️",  # Spy
    "sr": "🪖",  # Sergeant
    "lt": "📍",  # Lieutenant
    "cp": "🎖️",  # Captain
    "mx": "❓",  # Unknown enemy
    ".": " ",   # Empty
    "~": "💧",  # Lake
}


def render_interactive_board(game_controller):
    """
    Render an interactive chess-like board where:
    1. Click a piece to select it
    2. See available moves highlighted
    3. Click destination to move
    """
    if not game_controller:
        st.error("Game not initialized")
        return None

    board = game_controller.get_board_display()
    lines = board.split("\n")

    # Find where board starts
    board_start = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("0"):
            board_start = i + 1
            break

    board_lines = lines[board_start:]

    # Extract board data
    size = game_controller.size
    board_data = {}

    for line in board_lines:
        if not line.strip() or len(line) < 3:
            continue
        row_label = line[0] if line and line[0].isalpha() else None
        if not row_label:
            continue

        rest = line[2:].strip()
        pieces = rest.split()

        if len(pieces) >= size:
            for col, piece in enumerate(pieces[:size]):
                board_data[(row_label, col)] = piece

    # Initialize session state for piece selection
    if "selected_piece" not in st.session_state:
        st.session_state.selected_piece = None
    if "available_moves_for_piece" not in st.session_state:
        st.session_state.available_moves_for_piece = []

    st.markdown("## ⚔️ Stratego Battle Board")
    st.markdown(
        "*Click a piece to select it, then click a highlighted square to move*"
    )

    # Get all legal moves for reference
    all_legal_moves = game_controller.get_legal_moves()

    # Create board HTML
    html = create_interactive_board_html(
        board_data,
        size,
        game_controller,
        st.session_state.selected_piece,
        st.session_state.available_moves_for_piece,
        all_legal_moves
    )

    st.markdown(html, unsafe_allow_html=True)

    # Handle piece/move selection with buttons
    selected_move = handle_board_interaction(
        board_data, size, game_controller, all_legal_moves
    )

    return selected_move


def create_interactive_board_html(
    board_data, size, game_controller, selected_piece, available_moves, all_legal_moves
) -> str:
    """Create beautiful interactive board HTML"""

    html = """
    <style>
        .board-wrapper {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            display: inline-block;
            margin: 20px 0;
        }

        .board-grid {
            display: grid;
            grid-template-columns: 40px repeat(""" + str(size) + """, 50px);
            grid-template-rows: 40px repeat(""" + str(size) + """, 50px);
            gap: 2px;
            background-color: #1a1a2e;
            padding: 10px;
            border-radius: 10px;
        }

        .col-header {
            background: linear-gradient(180deg, #3d5a80 0%, #2a5298 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
            border-radius: 5px;
        }

        .row-header {
            background: linear-gradient(90deg, #3d5a80 0%, #2a5298 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
            border-radius: 5px;
        }

        .cell {
            width: 50px;
            height: 50px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 1px solid rgba(255,255,255,0.1);
            position: relative;
        }

        .cell-empty {
            background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
        }

        .cell-your-piece {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.4);
        }

        .cell-your-piece:hover {
            background: linear-gradient(135deg, #5dade2 0%, #3498db 100%);
            transform: scale(1.08);
        }

        .cell-selected {
            background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%) !important;
            box-shadow: 0 0 20px rgba(243, 156, 18, 0.8) !important;
            border: 2px solid #fff !important;
        }

        .cell-available-move {
            background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%) !important;
            box-shadow: 0 0 15px rgba(46, 204, 113, 0.6) !important;
            border: 2px dashed #fff !important;
        }

        .cell-available-move::after {
            content: "●";
            font-size: 30px;
            color: rgba(255,255,255,0.6);
            position: absolute;
        }

        .cell-enemy-piece {
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            box-shadow: 0 4px 15px rgba(231, 76, 60, 0.4);
        }

        .cell-enemy-piece:hover {
            background: linear-gradient(135deg, #ec7063 0%, #e74c3c 100%);
            transform: scale(1.08);
        }

        .cell-lake {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            animation: wave 3s ease-in-out infinite;
        }

        @keyframes wave {
            0%, 100% { opacity: 0.7; }
            50% { opacity: 1; }
        }

        .coordinate-label {
            position: absolute;
            bottom: 2px;
            right: 4px;
            font-size: 8px;
            color: rgba(255,255,255,0.3);
            font-weight: bold;
        }
    </style>

    <div class="board-wrapper">
        <div class="board-grid">
    """

    # Column headers (0-9)
    html += '<div class="col-header"></div>'  # Corner
    for col in range(size):
        html += f'<div class="col-header">{col}</div>'

    # Rows - REVERSED for proper orientation (J at bottom, A at top visually)
    # But we need to think about this - human should be at bottom
    # In standard game: Player 0 (human) is at rows A-D (top)
    # But for chess-like play, human should be at bottom
    # So we display rows in reverse order (J down to A) so human setup is at bottom
    rows = [chr(ord('A') + i) for i in range(size)]

    for row_idx, row in enumerate(reversed(rows)):  # Reverse to show A at bottom
        # Row header
        html += f'<div class="row-header">{row}</div>'

        # Cells
        for col in range(size):
            piece = board_data.get((row, col), ".")
            cell_key = f"{row}-{col}"

            # Determine cell class and emoji
            if piece == "~":
                cell_class = "cell cell-lake"
                emoji = PIECE_EMOJI.get(piece, "💧")
            elif piece == ".":
                cell_class = "cell cell-empty"
                emoji = ""
            elif piece == "?":
                cell_class = "cell cell-enemy-piece"
                emoji = PIECE_EMOJI.get(piece, "❓")
            else:
                cell_class = "cell cell-your-piece"
                emoji = PIECE_EMOJI.get(piece, "🎖️")

            # Check if this is selected or available move
            if cell_key == selected_piece:
                cell_class += " cell-selected"
            elif cell_key in available_moves:
                cell_class += " cell-available-move"

            html += f'<div class="{cell_class}" data-cell="{cell_key}">{emoji}<span class="coordinate-label">{row}{col}</span></div>'

    html += """
        </div>
    </div>
    """

    return html


def handle_board_interaction(board_data, size, game_controller, all_legal_moves):
    """Handle click-based board interaction"""

    if not game_controller.is_human_turn():
        return None

    st.markdown("---")
    st.markdown("### 🎮 Make Your Move")

    # Get legal moves with their source and destination
    legal_move_dict = {}  # Maps destination to source
    for move in all_legal_moves:
        # Move format: "[A0 B0]"
        parts = move.replace("[", "").replace("]", "").split()
        if len(parts) == 2:
            src, dst = parts
            dst_key = f"{dst[0]}-{int(dst[1])}"
            legal_move_dict[dst_key] = move

    # Show instructions
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"📍 Legal moves: {len(all_legal_moves)}")
    with col2:
        st.caption("Step 1: Click a piece")
    with col3:
        st.caption("Step 2: Click destination")

    # Create columns for move buttons
    st.markdown("**Or click a move directly:**")
    cols_per_row = 6
    cols = st.columns(cols_per_row)

    for idx, move in enumerate(all_legal_moves):
        col_idx = idx % cols_per_row
        with cols[col_idx]:
            if st.button(
                f"🎲 {move}",
                use_container_width=True,
                key=f"move_btn_{move}_{idx}",
            ):
                return move.strip().upper()

    return None
