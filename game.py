import streamlit as st
import random

st.title("🎲 Game Hub")

# Sidebar for game selection
game = st.sidebar.selectbox("Choose a game:", ["Rock-Paper-Scissors", "Tic-Tac-Toe", "Number Guessing", "Memory Game"])

# 1. Rock-Paper-Scissors
if game == "Rock-Paper-Scissors":
    st.header("✊ Rock-Paper-Scissors")
    user_choice = st.selectbox("Choose your move:", ["Rock", "Paper", "Scissors"])
    if st.button("Play"):
        computer_choice = random.choice(["Rock", "Paper", "Scissors"])
        st.write(f"Computer chose: **{computer_choice}**")
        if user_choice == computer_choice:
            st.info("It's a tie!")
        elif (user_choice == "Rock" and computer_choice == "Scissors") or \
             (user_choice == "Paper" and computer_choice == "Rock") or \
             (user_choice == "Scissors" and computer_choice == "Paper"):
            st.success("You win!")
        else:
            st.error("You lose!")

# 2. Tic-Tac-Toe
elif game == "Tic-Tac-Toe":
    st.header("⭕ Tic-Tac-Toe")

    # Initialize the board
    if 'board' not in st.session_state:
        st.session_state.board = [''] * 9
        st.session_state.current_player = 'X'
        st.session_state.game_over = False

    # Display the current player
    st.write(f"Current Player: **{st.session_state.current_player}**")

    # Draw the board
    cols = st.columns(3)
    for i in range(9):
        with cols[i % 3]:
            if st.button(st.session_state.board[i] if st.session_state.board[i] != '' else ' ', key=f'cell{i}'):
                if st.session_state.board[i] == '' and not st.session_state.game_over:
                    st.session_state.board[i] = st.session_state.current_player
                    # Check for win
                    board = st.session_state.board
                    win_conditions = [
                        (0,1,2), (3,4,5), (6,7,8),  # Rows
                        (0,3,6), (1,4,7), (2,5,8),  # Columns
                        (0,4,8), (2,4,6)            # Diagonals
                    ]
                    winner = None
                    for a, b, c in win_conditions:
                        if board[a] == board[b] == board[c] != '':
                            winner = board[a]
                            break
                    if winner:
                        st.success(f"Player **{winner}** wins!")
                        st.session_state.game_over = True
                    elif '' not in st.session_state.board:
                        st.info("It's a tie!")
                        st.session_state.game_over = True
                    else:
                        # Switch player
                        st.session_state.current_player = 'O' if st.session_state.current_player == 'X' else 'X'
                st.experimental_rerun()

    # Reset the game
    if st.session_state.game_over:
        if st.button("Restart Game"):
            st.session_state.board = [''] * 9
            st.session_state.current_player = 'X'
            st.session_state.game_over = False
            st.experimental_rerun()

# 3. Number Guessing Game
elif game == "Number Guessing":
    st.header("🔢 Number Guessing Game")
    if 'number' not in st.session_state:
        st.session_state.number = random.randint(1, 100)
        st.session_state.attempts = 0

    guess = st.number_input("Guess a number between 1 and 100:", min_value=1, max_value=100, step=1)
    if st.button("Guess"):
        st.session_state.attempts += 1
        if guess < st.session_state.number:
            st.info("Too low!")
        elif guess > st.session_state.number:
            st.info("Too high!")
        else:
            st.success(f"Correct! You guessed the number in {st.session_state.attempts} attempts.")
            # Reset the game
            st.session_state.number = random.randint(1, 100)
            st.session_state.attempts = 0

# 4. Memory Game
elif game == "Memory Game":
    st.header("🧠 Memory Game")
    grid_size = 4
    total_tiles = grid_size * grid_size
    total_pairs = total_tiles // 2

    if 'memory_grid' not in st.session_state:
        # Initialize the grid with pairs of numbers
        numbers = list(range(1, total_pairs + 1)) * 2
        random.shuffle(numbers)
        st.session_state.memory_grid = numbers
        st.session_state.flipped = [False] * total_tiles
        st.session_state.first_choice = None
        st.session_state.second_choice = None
        st.session_state.matches_found = 0
        st.session_state.pending_flip = []

    # Handle pending flips (tiles to flip back)
    if st.session_state.pending_flip:
        idx1, idx2 = st.session_state.pending_flip
        st.session_state.flipped[idx1] = False
        st.session_state.flipped[idx2] = False
        st.session_state.pending_flip = []

    # Draw the grid
    cols = st.columns(grid_size)
    for i in range(total_tiles):
        with cols[i % grid_size]:
            if st.button("🟦" if not st.session_state.flipped[i] else f"{st.session_state.memory_grid[i]}", key=f'memory{i}'):
                if not st.session_state.flipped[i]:
                    st.session_state.flipped[i] = True
                    if st.session_state.first_choice is None:
                        st.session_state.first_choice = i
                    elif st.session_state.second_choice is None:
                        st.session_state.second_choice = i
                        idx1 = st.session_state.first_choice
                        idx2 = st.session_state.second_choice
                        val1 = st.session_state.memory_grid[idx1]
                        val2 = st.session_state.memory_grid[idx2]

                        if val1 == val2:
                            st.success("Match found!")
                            st.session_state.matches_found += 1
                            if st.session_state.matches_found == total_pairs:
                                st.balloons()
                                st.success("You've found all matches!")
                                # Reset the game
                                del st.session_state.memory_grid
                                st.experimental_rerun()
                        else:
                            st.warning("No match! Tiles will flip back on next click.")
                            st.session_state.pending_flip = [idx1, idx2]
                        # Reset choices
                        st.session_state.first_choice = None
                        st.session_state.second_choice = None
                    st.experimental_rerun()
