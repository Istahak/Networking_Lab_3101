from operator import index
import socket
import threading
import struct 

import tkinter as tk
from tkinter import Button, simpledialog, messagebox
from tkinter import scrolledtext

# Define the host IP address and port
host = "127.0.0.1"
port = 12369

host1 = "127.0.0.1"
port1 = 12358


IP = '127.0.0.1'
PORT = 5426
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"


root = tk.Tk()
buttons = []
buttons_frame = None
info_bar_frame = None
chat_frame = None
chat_box = None
input_frame = None
message_entry = None
send_button = None
clear_button = None
info_label = None
clicked_button_index = None
clientfortext = None
root.title("Tic Tac Toe The Network Showdown")

def decode_msg(msg):
    header = struct.unpack("6H", msg[:12])
    ms = msg[12:].decode('utf-8')

    # print('\n Before Decoding')
    # print(msg)
    
    # print('\n After Decoding')
    print({header},{ms})
 
    return ms

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

def send_message():
    message = message_entry.get()
    if message:
        clientfortext.send(message.encode())
        chat_box.insert(tk.END, "You: " + message + "\n")
        message_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Warning", "Please enter a message!")

def clear_chat():
    chat_box.delete(1.0, tk.END)


def button_click(index):
    global clicked_button_index
    clicked_button_index = index
    print(f"Button {index+1} clicked")
   

             

# Function to receive messages from the server
def receive_msg():
    while True: 
        # Receive message from the server
        message = clientfortext.recv(1024).decode()
        if message:
            # Insert the received message to the chat box
            chat_box.insert(tk.END,"Opponent: " + message + "\n")
        # Print the received message
        print(f"Received: {message}")
def connect_dns(domain_name):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message = domain_name
    client.sendto(message.encode(FORMAT), ADDR)
    msg,addr=client.recvfrom(SIZE)
    msg1=decode_msg(msg)
    data=msg1.split()
    while data[2]=="NS":
        new_adr=(IP,int(data[1]))
        print('Connecting to port', data[1])
        client.sendto(message.encode(FORMAT),new_adr)
        msg,addr=client.recvfrom(SIZE)
        msg1=decode_msg(msg)
        data=msg1.split()
    return int(data[1])
# Function for game play logic
def game_play(client):
    # Receive initial game state from the server
    inital_game_state = client.recv(1024).decode() # receive initial game state You are player 1. Your mark is X.
    # set the info label
    info_label.config(text=inital_game_state)
    player_mark = inital_game_state[-2]
    print(inital_game_state)
    while True:
        # Send signal to server to indicate it's ready to receive board
        client.send("1".encode()) # before taking board 
        # Receive initial game board from the server
        inital_game_board = client.recv(1024).decode() # receive initial game board [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
        for i in range(9):
           cc = inital_game_board[2 + 5 * i]
           if cc == 'X':
               buttons[i].config(text='X')
           elif cc == 'O':
               buttons[i].config(text='O')
           else:
               buttons[i].config(text=' ')        
        
        print(inital_game_board)
        # # Send signal to server to indicate it has received the board
        client.send("2".encode()) # after taking board
        # # Receive game status from the server
        status = client.recv(1024).decode() # receive status 1, 2, 3
        # print(status)
        if status == "3":
            # Send signal to server to indicate it's ready to receive game status
            client.send("3".encode()) # after taking status
            # Receive current game status from the server
            take_game_current_status = client.recv(1024).decode()
            info_label.config(text=take_game_current_status)
            if take_game_current_status == "You win!":
                print("You win!")
                break
            elif take_game_current_status == "You lose!":
                print("You lose!")
                break
            elif take_game_current_status == "It's a draw!":
                print("It's a draw!")
                break
            print(take_game_current_status)
        elif status == "2":
            pass
        else:
            # Send signal to server to indicate it's ready to receive game status
            client.send("3".encode()) # after taking status
            # Receive current game status from the server
            take_game_current_status = client.recv(1024).decode()
            info_label.config(text=take_game_current_status)
            print(take_game_current_status)
            while True:
                global clicked_button_index
                while clicked_button_index is None:
                    pass
                
                
                move = clicked_button_index
                clicked_button_index = None
                # print(f"Move: {move}",f"Move type: {type(move)}")
                
                for i in range(9):
                    print(inital_game_board[2 + 5 * i], end = " ")
    
                    if i % 3 == 2:
                        print()
                if move >= 0 and move <= 8 and inital_game_board[2 + 5 * move] == ' ':
                    print("size of buttons",len(buttons))
                    
                    buttons[move].config(text=player_mark)
                    client.send(str(move).encode())
                    break
                else:
                    info_label.config(text="Invalid move. Try again.")
                    print("Invalid move. Try again.")

# Main function
def main():
    port = connect_dns('www.tictactoe.com')
    port1 = connect_dns('www.msgttt.com')
    # Info bar
    global info_bar_frame
    info_bar_frame = tk.Frame(root, bg="lightgray", padx=10, pady=10)
    info_bar_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

    
    global info_label
    info_label = tk.Label(info_bar_frame, text="Please wait for your game patner", font=('Arial', 14), bg="lightgray")
    info_label.pack(expand=True, fill=tk.BOTH)
    
    global buttons_frame
   # Buttons
    buttons_frame = tk.Frame(root, padx=10, pady=10)
    buttons_frame.grid(row=1, column=0, sticky="nsew")
    global buttons
    for i in range(3):
        for j in range(3):
            index = i * 3 + j
            button = tk.Button(buttons_frame, text=" ", font=('Arial', 12), width=3, height=1,command=lambda idx=index: button_click(idx))
            button.grid(row=i, column=j, padx=5, pady=5)
            buttons.append(button)
    
    #Buttons creation end
    
        # Chat window
    global chat_frame    
    chat_frame = tk.Frame(root, bg="white", padx=10, pady=10)
    chat_frame.grid(row=1, column=1, sticky="nsew")

    global chat_box
    chat_box = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD)
    chat_box.pack(expand=True, fill=tk.BOTH)

    
    # Input message
    global input_frame
    input_frame = tk.Frame(root, padx=10, pady=10)
    input_frame.grid(row=2, column=1, sticky="ew")

    global message_entry
    message_entry = tk.Entry(input_frame, font=('Arial', 12))
    message_entry.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    global send_button
    send_button = Button(input_frame, text="Send", font=('Arial', 12), command=send_message)
    send_button.pack(side=tk.LEFT)

    global clear_button
    clear_button = Button(input_frame, text="Clear Chat", font=('Arial', 12), command=clear_chat)
    clear_button.pack(side=tk.RIGHT)
        
    
   
    # Create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to the server
    client.connect((host, port))
    # Print server connection message
    print(f"Connected to server.")
    global clientfortext
    clientfortext = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    clientfortext.connect((host1,port1))
    
    game_thread = threading.Thread(target=game_play, args=(client,))
    game_thread.start() 
    send_message_thread = threading.Thread(target=send_message, args=())
    send_message_thread.start()
    receive_message_thread = threading.Thread(target=receive_msg, args=())
    receive_message_thread.start()
    root.protocol("WM_DELETE_WINDOW", on_closing) 
    root.update_idletasks()  # Calculate window size
    root.mainloop()
# Entry point of the script
if __name__ == "__main__":
    main()