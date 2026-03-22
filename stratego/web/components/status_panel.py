"""Game status panel component - Beautiful stats display"""
import streamlit as st
import time


def render_status_panel(game_controller):
    """Display game status info with beautiful styling"""
    if not game_controller:
        return

    st.markdown("""
    <style>
        .status-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        .status-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .turn-info {
            background: rgba(255,255,255,0.1);
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .turn-number {
            font-size: 24px;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        # Turn indicator with emoji
        if game_controller.is_human_turn():
            st.success("🎯 YOUR TURN - Make a Move!")
            emoji = "👤"
            player_text = "You"
        elif game_controller.is_ai_turn():
            st.info("🤖 AI IS THINKING...")
            emoji = "🤖"
            player_text = "AI"
        else:
            st.warning("⚠️ Game state unclear")
            emoji = "❓"
            player_text = "Unknown"

        # Game statistics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "⚔️ Total Moves",
                game_controller.get_turn_count(),
                help="Total number of moves played by both players"
            )

        with col2:
            st.metric(
                "👤 Your Moves",
                len(game_controller.move_history[0]),
                help="Number of moves you have made"
            )

        with col3:
            st.metric(
                "🤖 AI Moves",
                len(game_controller.move_history[1]),
                help="Number of moves AI has made"
            )

        # Game status
        st.divider()

        if game_controller.game_done:
            st.error(f"🏁 GAME ENDED")
            st.write(f"**Result:** {game_controller.game_info.get('result', 'Unknown')}")
        else:
            st.success("✅ Game Active")
            st.caption(f"Current Player: {emoji} {player_text}")
