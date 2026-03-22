"""Human move input widget - Beautifully styled move buttons"""
import streamlit as st
from stratego.web.utils.validators import is_valid_move_string


def render_move_input(game_controller):
    """Render beautiful clickable move buttons for human player"""
    if not game_controller:
        st.error("Game not initialized")
        return None

    if not game_controller.is_human_turn():
        return None

    legal_moves = game_controller.get_legal_moves()

    if not legal_moves:
        st.error("No legal moves available!")
        return None

    # Beautiful header with styling
    st.markdown("""
    <style>
        .move-section {
            background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%);
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(46, 204, 113, 0.3);
        }
        .move-title {
            color: white;
            font-size: 20px;
            font-weight: bold;
            margin: 0;
        }
        .move-buttons-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 15px;
            justify-content: flex-start;
        }
    </style>
    <div class="move-section">
        <p class="move-title">🎯 YOUR TURN - Click a Move Below</p>
    </div>
    """, unsafe_allow_html=True)

    # Display moves as styled buttons
    cols_per_row = 6
    cols = st.columns(cols_per_row)

    for idx, move in enumerate(legal_moves):
        col_idx = idx % cols_per_row
        with cols[col_idx]:
            if st.button(
                f"🎲 {move}",
                use_container_width=True,
                key=f"move_btn_{move}_{idx}",
                help=f"Move from {move.split()[0]} to {move.split()[1]}"
            ):
                return move.strip().upper()

    return None
