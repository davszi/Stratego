"""Beautiful board display component with emojis and proper styling"""
import streamlit as st
from stratego.utils.parsing import extract_board_block_lines, extract_legal_moves


# Piece emoji mapping - makes board much more visual
PIECE_EMOJI = {
    "fl": "🚩",  # Flag
    "bm": "💣",  # Bomb
    "ms": "👑",  # Marshal (Crown)
    "gn": "⭐",  # General (Star)
    "mn": "⛏️",  # Miner
    "sc": "🏃",  # Scout (Running person)
    "sp": "🕵️",  # Spy
    "sr": "🪖",  # Sergeant (Helmet)
    "lt": "📍",  # Lieutenant (Pin)
    "cp": "🎖️",  # Captain (Medal)
    "mx": "❓",  # Unknown enemy
    ".": " ",   # Empty
    "~": "💧",  # Lake
}


def render_board(game_controller, background_color="auto"):
    """Render a beautiful game board with emojis and great styling"""
    if not game_controller:
        st.error("Game not initialized")
        return

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

    # Create beautiful HTML board
    html_board = create_beautiful_board_html(board_data, size)

    st.markdown("## ⚔️ Stratego Battle Board", help="Blue = Your Army | Red = Enemy Army")
    st.markdown(html_board, unsafe_allow_html=True)

    # Legend
    legend_col1, legend_col2, legend_col3 = st.columns(3)
    with legend_col1:
        st.markdown("🔵 **Your Pieces** - Blue Background")
    with legend_col2:
        st.markdown("🔴 **Enemy Pieces** - Red with ❓")
    with legend_col3:
        st.markdown("💧 **Lakes** - Blocked Water")


def create_beautiful_board_html(board_data, size) -> str:
    """Create a beautiful, professional-looking board"""

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
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.2);
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
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.2);
        }

        .cell {
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 1px solid rgba(255,255,255,0.1);
        }

        .cell:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }

        .cell-empty {
            background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
            color: #555;
        }

        .cell-your-piece {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.4);
            font-weight: bold;
        }

        .cell-your-piece:hover {
            background: linear-gradient(135deg, #5dade2 0%, #3498db 100%);
        }

        .cell-enemy-piece {
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(231, 76, 60, 0.4);
            font-weight: bold;
        }

        .cell-enemy-piece:hover {
            background: linear-gradient(135deg, #ec7063 0%, #e74c3c 100%);
        }

        .cell-lake {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
            animation: wave 3s ease-in-out infinite;
        }

        @keyframes wave {
            0%, 100% { opacity: 0.7; }
            50% { opacity: 1; }
        }

        .turn-indicator {
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            margin: 15px 0;
            padding: 10px;
            background: linear-gradient(90deg, #f39c12 0%, #e67e22 100%);
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
    </style>

    <div class="board-wrapper">
        <div class="board-grid">
    """

    # Column headers
    html += '<div class="col-header"></div>'  # Corner placeholder
    for col in range(size):
        html += f'<div class="col-header">{col}</div>'

    # Rows with pieces
    rows = [chr(ord('A') + i) for i in range(size)]

    for row in rows:
        # Row header
        html += f'<div class="row-header">{row}</div>'

        # Cells
        for col in range(size):
            piece = board_data.get((row, col), ".")

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

            html += f'<div class="{cell_class}">{emoji}</div>'

    html += """
        </div>
    </div>
    """

    return html


def render_legal_moves(game_controller):
    """Display available legal moves"""
    if not game_controller:
        return []

    legal_moves = game_controller.get_legal_moves()
    if legal_moves:
        moves_str = " | ".join(legal_moves[:8])
        st.caption(f"Available moves: {moves_str}")
    return legal_moves
