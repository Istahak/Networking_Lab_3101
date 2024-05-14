import socket
import threading
import time
HOST = '127.0.0.1'
PORT = 12369

host = '127.0.0.1'
port = 12358
connected_users = []
user_map = {}
player_map = {}
user_connected_event = threading.Event()
lock = threading.Lock()

def check_win(board, mark):
    # Check rows
    for i in range(0, 9, 3):
        if board[i] == board[i+1] == board[i+2] == mark:
            return True

    # Check columns
    for i in range(3):
        if board[i] == board[i+3] == board[i+6] == mark:
            return True

    # Check diagonals
    if board[0] == board[4] == board[8] == mark:
        return True
    if board[2] == board[4] == board[6] == mark:
        return True

    return False

def is_board_full(board):
    for cell in board:
        if cell == ' ':
            return False  # If any cell is empty, the board is not full
    return True

def play_game(player1_conn, player2_conn):
    player1_mark = 'X'
    player2_mark = 'O'

    # Initialize the game board
    board = [' ' for _ in range(9)]

    # Send initial game state to players
    player1_conn.send("You are player 1. Your mark is X.".encode())
    player2_conn.send("You are player 2. Your mark is O.".encode())

    # Game loop
    current_turn = player1_conn
    while True:
        # Send current board state to both players
        player1_conn.recv(1024).decode()
        player2_conn.recv(1024).decode()
        print(str(board))
        player1_conn.send(str(board).encode())
        player2_conn.send(str(board).encode())
        
        current_turn.recv(1024).decode()
        # Check for a win or draw
        if check_win(board, player1_mark):
            player1_conn.send("3".encode())
            player2_conn.send("3".encode())
            current_turn.recv(1024).decode()
            player1_conn.send("You win!".encode())
            player2_conn.send("You lose!".encode())
            break
        elif check_win(board, player2_mark):
            player1_conn.send("3".encode())
            player2_conn.send("3".encode())
            current_turn.recv(1024).decode()
            player1_conn.send("You lose!".encode())
            player2_conn.send("You win!".encode())
            break
        elif is_board_full(board):
            player1_conn.send("3".encode())
            player2_conn.send("3".encode())
            current_turn.recv(1024).decode()
            player1_conn.send("It's a draw!".encode())
            player2_conn.send("It's a draw!".encode())
            break
        if current_turn == player1_conn:
            player1_conn.send("1".encode())
            player2_conn.send("2".encode())
        else:
            player1_conn.send("2".encode())
            player2_conn.send("1".encode())
        current_turn.recv(1024).decode()
        # Get current player's move
        current_player = "Player 1" if current_turn == player1_conn else "Player 2"
        current_mark = player1_mark if current_turn == player1_conn else player2_mark
        current_turn.send(f"Your turn, {current_player}. Make your move (0-8): ".encode())
        move = int(current_turn.recv(1024).decode())
        board[move] = current_mark
        current_turn = player1_conn if current_turn == player2_conn else player2_conn

        # Add a short delay to allow the other client to process the move
        time.sleep(0.1)  # Adjust as needed



# def handle_client(player1, player2):
#     # print(user_map[another_user['socket']].getpeername()[0])
#     # print('break\n')
#     # print(user_map[user['socket']].getpeername()[0])
#     # game_thread = threading.Thread(target=play_game, args=(user_map[another_user['socket']], user_map[user['socket']]))
#     # game_thread.start()
#     while True:
#         data = player1.recv(1024)
#         # print(f"Received data from {client_address}: {data.decode()}")
#         player2.send(data.encode())

def main():
    """Main function."""
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        while True:
            client_socket, client_address = server_socket.accept()
            connected_users.append(client_socket)
            if len(connected_users) == 2:
                client_thread = threading.Thread(target=play_game, args=(connected_users[0], connected_users[1]))
                client_thread.start()
                # msg_thread1 = threading.Thread(target=handle_client, args=(connected_users[0], connected_users[1]))
                # msg_thread1.start()
                # msg_thread2 = threading.Thread(target=handle_client, args=(connected_users[1], connected_users[0]))
                # msg_thread2.start()
                connected_users.clear()

if __name__ == "__main__":
    main()