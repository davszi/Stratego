"""Move history display component"""
import streamlit as st


def render_game_history(game_controller, limit=None):
    """Display all game move history (or last N moves if limit specified)

    Args:
        game_controller: GameController instance
        limit: Max moves to show. None = show all moves
    """
    if not game_controller:
        return

    moves = game_controller.get_move_history_display(limit)

    if not moves:
        st.info("No moves yet")
        return

    # Show in expandable container if many moves
    if len(moves) > 20:
        with st.expander(f"Move History ({len(moves)} total moves)", expanded=False):
            # Show in columns for better layout with many moves
            col1, col2 = st.columns(2)
            for i, move in enumerate(moves):
                if i % 2 == 0:
                    with col1:
                        st.caption(f"**{i+1}.** {move}")
                else:
                    with col2:
                        st.caption(f"**{i+1}.** {move}")
    else:
        st.subheader(f"Move History ({len(moves)} moves)")
        cols = st.columns(2)
        for i, move in enumerate(moves):
            col_idx = i % 2
            with cols[col_idx]:
                st.caption(f"**{i+1}.** {move}")


def render_game_summary(game_controller):
    """Display game summary info"""
    if not game_controller:
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Turn", game_controller.get_turn_count())
    
    with col2:
        player = "Your turn" if game_controller.is_human_turn() else "AI thinking"
        st.metric("Current", player)
    
    with col3:
        st.metric("Status", "Active" if not game_controller.game_done else "Ended")
