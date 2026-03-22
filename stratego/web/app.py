"""Main Streamlit application for Stratego Human vs AI"""

import streamlit as st
from stratego.web.config import session_manager, agent_builder, game_config
from stratego.web.game_controller import GameController
from stratego.web.components import game_history, status_panel
from stratego.web.components.interactive_board import render_interactive_board
from stratego.web.utils.validators import normalize_move


def screen_welcome():
    """Screen 0: Welcome and game mode selection"""
    st.title("⚔️ STRATEGO - Human vs AI")
    st.markdown("*Challenge an intelligent AI opponent in the classic strategy game!*")

    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🎮 How to Play")
        st.write("""
        **Objective:** Capture the enemy flag or eliminate all movable pieces

        **Your Setup:**
        - 🔵 Your army positioned at the **BOTTOM** of the board
        - Arrange your pieces strategically before the game starts
        - Each piece has a rank that determines its strength

        **Your Turn:**
        1. **Click on one of your pieces** (blue area at bottom)
        2. **Available destination squares will be highlighted** in green with a dot (●)
        3. **Click the destination** to move your piece there
        4. **Battles resolve automatically** when pieces meet

        **AI Opponent:**
        - 🔴 Enemy forces at the **TOP** of the board
        - Uses Mistral 7B LLM to make strategic decisions
        - Plays immediately after your move
        """)

        st.markdown("---")
        st.markdown("### ⚙️ Setup Requirements")
        with st.expander("📦 Ollama Installation", expanded=False):
            st.code(
                """# Make sure you have Ollama running locally:
ollama serve

# In a new terminal, pull Mistral:
ollama pull mistral:7b

# Verify it's installed:
ollama list""",
                language="bash"
            )
            st.caption(
                "💡 Ollama provides local LLM inference. "
                "Download: https://ollama.ai"
            )

    with col2:
        st.subheader("📊 Game Info")
        selected_config = game_config.get_game_config(
            "Standard (10x10)"
        )
        st.metric("Board Size", "10 × 10")
        st.metric("Players", "2 (You vs AI)")
        st.metric("AI Model", "Mistral 7B")
        st.metric("Time/Move", "~2-5 sec")

        st.divider()

        st.subheader("🎯 Piece Legend")
        legend_data = {
            "🚩": "Flag (0★) - Must protect!",
            "💣": "Bomb (0★) - Immovable",
            "👑": "Marshal (10★) - Strongest",
            "⭐": "General (9★) - Second strongest",
            "🏃": "Scout (2★) - Can move multi-square",
            "🕵️": "Spy (1★) - Defeats Marshal",
            "🪖": "Sergeant (3★)",
            "📍": "Lieutenant (4★)",
            "🎖️": "Captain (6★)",
        }
        for emoji, desc in legend_data.items():
            st.caption(f"{emoji} {desc}")

    st.divider()

    # Game mode selection
    st.markdown("### 🕹️ Start Your Battle")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(
            "**Standard 10×10 with lakes**\n"
            "Classic Stratego rules. Your pieces at bottom, AI at top."
        )

    with col2:
        if st.button("Start Game →", type="primary", use_container_width=True, key="start_game_btn"):
            session_manager.SessionManager.set_game_mode("Standard (10x10)")
            session_manager.SessionManager.set_screen(1)
            st.rerun()


def screen_ai_config():
    """Screen 1: AI agent configuration - Real Ollama setup"""
    st.title("⚙️ Configure AI Opponent")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🚀 Ollama AI Model")

        # Ollama configuration
        backend = "ollama"
        st.success("✅ Using Ollama Backend")

        available_models = game_config.get_available_models(backend)
        model = st.selectbox(
            "Select Model:",
            available_models,
            index=0,
            help="Choose from available Ollama models (make sure it's pulled: ollama pull mistral:7b)"
        )

        ollama_url = st.text_input(
            "🔗 Ollama Server URL:",
            value="http://localhost:11434",
            help="Local: http://localhost:11434 | Remote: your_server_ip:11434"
        )

        # Test connection button
        if st.button("🧪 Test Connection", help="Check if Ollama is running"):
            try:
                import requests
                response = requests.get(f"{ollama_url}/api/tags", timeout=3)
                if response.status_code == 200:
                    st.success("✅ Connected to Ollama!")
                    st.caption(f"(Available models: {len(response.json().get('models', []))})")
                else:
                    st.error(f"❌ Ollama responded with status {response.status_code}")
            except Exception as e:
                st.error(f"❌ Cannot connect to Ollama: {str(e)}")
                st.caption(f"Make sure Ollama is running at {ollama_url}")

    with col2:
        st.subheader("📖 Strategy & Settings")

        prompt = st.selectbox(
            "Prompt Style:",
            game_config.PROMPT_PRESETS,
            index=0,
            help="base=minimal | concise=focused on winning | adaptive=strategic analysis"
        )

        st.info("💡 Tip: Start with Mistral 7B for good balance of speed and quality")

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("< Back", use_container_width=True):
            session_manager.SessionManager.set_screen(0)
            st.rerun()

    with col3:
        if st.button("🎮 Start Game", type="primary", use_container_width=True):
            # Build real OllamaAgent
            try:
                from stratego.models.ollama_model import OllamaAgent

                st.session_state.ollama_url = ollama_url
                agent = OllamaAgent(
                    model_name=model,
                    prompt_pack=prompt,
                    host=ollama_url
                )

                # Initialize game
                mode = session_manager.SessionManager.get_game_mode()
                env_id = game_config.get_env_id(mode)
                size = game_config.get_board_size(mode)

                game_ctrl = GameController(env_id, size, agent, prompt)
                game_ctrl.reset()

                session_manager.SessionManager.set_game_controller(game_ctrl)
                session_manager.SessionManager.set_ai_config(backend, model, prompt)
                session_manager.SessionManager.set_screen(2)
                st.rerun()

            except Exception as e:
                st.error(f"❌ Failed to create AI: {str(e)}")
                st.code(f"Error details:\n{str(e)}")
                st.warning(
                    f"Make sure:\n"
                    f"1. Ollama is running: `ollama serve`\n"
                    f"2. Model is pulled: `ollama pull {model}`\n"
                    f"3. Server URL is correct: {ollama_url}"
                )


def screen_active_game():
    """Screen 2: Active game with interactive chess-like board"""
    game_ctrl = session_manager.SessionManager.get_game_controller()

    if not game_ctrl:
        st.error("Game not initialized!")
        return

    st.title("⚔️ STRATEGO - Battle Arena")

    # Top controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("🔄 Reset", help="Start a new game"):
            session_manager.SessionManager.reset_all()
            st.rerun()

    with col2:
        # Game stats in header
        col2a, col2b, col2c = st.columns(3)
        with col2a:
            st.metric("Moves", game_ctrl.get_turn_count())
        with col2b:
            current = "👤 You" if game_ctrl.is_human_turn() else "🤖 AI"
            st.metric("Current", current)
        with col2c:
            st.metric("Status", "🎮 Active" if not game_ctrl.game_done else "🏁 Ended")

    with col3:
        if st.button("📋 Menu", help="Return to main menu"):
            session_manager.SessionManager.reset_all()
            st.rerun()

    st.divider()

    # Main game area
    left, right = st.columns([2.5, 1.5])

    with left:
        # Interactive board
        player_move = render_interactive_board(game_ctrl)

        if player_move:
            # Execute human move
            done, info = game_ctrl.execute_move(player_move)

            if done:
                st.session_state.game_ended = True
                st.rerun()

            # Trigger AI turn
            player_id, obs = game_ctrl.get_current_player()
            st.rerun()

        # AI's turn
        if game_ctrl.is_ai_turn():
            st.divider()
            st.markdown("## 🤖 AI is thinking...")

            with st.spinner("AI calculating move..."):
                try:
                    move, error = game_ctrl.get_ai_move()

                    if error:
                        st.warning(f"⚠️ {error}")

                    done, info = game_ctrl.execute_move(move)
                    st.success(f"✅ AI played: {move}")

                    if done:
                        st.session_state.game_ended = True
                    else:
                        # Update to human turn
                        player_id, obs = game_ctrl.get_current_player()

                    st.rerun()

                except Exception as e:
                    st.error(f"❌ AI Error: {str(e)}")
                    st.code(str(e))

    with right:
        st.subheader("📊 Game Info")

        # Status panel with beautiful styling
        status_panel.render_status_panel(game_ctrl)

        st.divider()

        # Move history
        st.subheader("📜 Move History")
        game_history.render_game_history(game_ctrl)

        # Game end screen
        if game_ctrl.game_done:
            st.divider()
            st.error("🏁 GAME ENDED!")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Play Again", use_container_width=True):
                    session_manager.SessionManager.reset_all()
                    st.rerun()
            with col2:
                if st.button("🏠 Main Menu", use_container_width=True):
                    session_manager.SessionManager.reset_all()
                    st.rerun()


def main():
    """Main application entry point"""
    # Configure page
    st.set_page_config(
        page_title="Stratego - Human vs AI",
        page_icon="chess",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session
    session_manager.SessionManager.init()
    
    # Route to correct screen
    screen = session_manager.SessionManager.get_screen()
    
    if screen == 0:
        screen_welcome()
    elif screen == 1:
        screen_ai_config()
    elif screen == 2:
        screen_active_game()
    else:
        st.error(f"Unknown screen: {screen}")


if __name__ == "__main__":
    main()
