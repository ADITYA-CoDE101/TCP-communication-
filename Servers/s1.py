import socket
import threading
import sys
import sqlite3

IP = "127.0.0.1"
PORT = 9898
UACL = [] #  Unauthenticated Client List
ACL = [] #   Authenticated Client List
CLIENTS = [] # All Clients List
CLIENTS_LOCK = threading.Lock()

def broadcast(message, sender_sock):
    with CLIENTS_LOCK:
        for A_client in ACL:  # Aclient --> Authenticated client
            if A_client != sender_sock:
                try:
                    A_client.send(message)
                except Exception as e:                      # except (BrokenPipeError, ConnectionResetError) as e:
                    print(f"Connection Closed due to an Exeption: {e}")
                    terminator(A_client, "will add sql to client address mapping.")                                      # Termination
                



def handle_client(client_sock, client_address):
    authentication(client_sock, client_address)                     # We have remove the context manger (with) since we do not want redundent termination
    while True:                                         # and context manger closes automaticlly at the end of the block
        try:
            data = client_sock.recv(1024)
            if not data:
                break
            terminate_msg = data.strip()
            if  terminate_msg == "RQST-> DISCONNECT":
                terminator(client_sock, client_address, cmd=False)
                break
            
            print(f"Received from {client_address}: {data.decode()}")
            broadcast(data, client_sock)
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
            break

    try:
        terminator(client_sock, client_address)      
    except Exception as e:
        print(f"thread is still alive! , even the client is closed.")                                       # Termination
    print(f"Connection closed: {client_address}")

    # ------------------------------

def terminator(client_sock, client_sock_addrs, cmd=True):
    
    if cmd:
        try:
            client_sock.send(b"DISCONNECTED")  # if socket is closed, this can raise an error
        except (BrokenPipeError, ConnectionResetError) as e:
            print(f"Error sending DISCONNECTED message to {client_sock}: {e}")
            
    with CLIENTS_LOCK:        
        if client_sock in ACL:                  # Since client will not be in the ACL and CLIENTS list befor Authentication
            ACL.remove(client_sock)                 # So we need condition, if client exist in these list then remove otherwise just close the client as is.
        if client_sock in CLIENTS:
            CLIENTS.remove(client_sock)

    if cmd:
        try:
            client_sock.shutdown(socket.SHUT_RDWR)  # Gracefully shutdown the socket
        except Exception as e:
            print(f"Error shutting down socket {client_sock_addrs}: {e}")
        
        try:
            client_sock.close()  # Ensure the socket is properly closed
        except Exception as e:
            print(f"Error closing socket {client_sock_addrs}: {e}")
    print(f"Connection closed: {client_sock_addrs}")


def authentication(client_sock, client_address):
    client_sock.send(b"\t\tWelcome! To the Chat`!`\nDo SignUp/SingIn")
    client_sock.send(b"Type [ 1 ] for signUp or [ 2 ] for SignIn")
    opt = client_sock.recv(1024).decode()
    if opt == "1":
        signup(client_sock)
        if not signin(client_sock):             # Exit              [ if statment works if the  given condition is TRUE or NOT FALSE ]
            terminator(client_sock, client_address)              # Termination
            
        else:
            with CLIENTS_LOCK:
                ACL.append(client_sock)             # Authenticated
                CLIENTS.append(client_sock)
                UACL.remove(client_sock)
        
    elif opt == "2":
        if not signin(client_sock):             # if signin -> Trur then the if body will not execut .  # Exit
            print("invalid credential")
            terminator(client_sock, client_address)              # Termination
            
        else:
            with CLIENTS_LOCK:
                ACL.append(client_sock)             # Authenticated
                CLIENTS.append(client_sock)
                UACL.remove(client_sock)
    else:
        client_sock.send(b"Invalid option. Connection closed.\n")
        terminator(client_sock, client_address)                  # Termination
        


def signup(client_sock):
    client_sock.send(b"Enter Username: ")
    username = client_sock.recv(1024).decode().strip()
    client_sock.send(b"Enter Password: ")
    password = client_sock.recv(1024).decode().strip()
    # Here you would normally save the username and password securely be will do this later
    client_sock.send(b"Signup successful!\n")
    client_sock.send(f"Hello {username}".encode())      # ???
    with open("users.txt", "a") as f:                          # >[1]
        f.write(f"{username}:{password}\n")
    print("*"*50)
    print("New user signed up:", username)

    

def signin(client_sock):
    """
    Handles user sign-in by prompting for username and password, checking credentials against 'users.txt'.
    Allows up to 3 authentication attempts; returns True if successful, otherwise False.
    Sends appropriate messages to the client socket for success or failure.
    """
    client_sock.send(b"Enter Username: ")
    username = client_sock.recv(1024).decode().strip()
    client_sock.send(b"Enter Password: ")
    password = client_sock.recv(1024).decode().strip()
    
    attempts = 3
    while attempts > 0:
        with open("users.txt", "r") as f:
            users = f.readlines()
    
            for user in users:
                u, p = user.strip().split(":")
                if u == username and p == password:
                    client_sock.send(b"Login successful!\n")
                    return True
                else:
                    pass

        client_sock.send(b"Invalid credentials!\n")
        attempts -= 1
        if attempts > 0:
            client_sock.send(b"Try again.\nEnter Username: ")
            username = client_sock.recv(1024).decode().strip()
            client_sock.send(b"Enter Password: ")
            password = client_sock.recv(1024).decode().strip()
        elif attempts == 0:
            client_sock.send(b"Too mant failded attemps.\n ---EXITING---")
            print(f"Too many failed attempts. Connection closed with {client_sock}")
            return False
                    
    # -------------------------------


"""def signin(client_sock):
    client_sock.send(b"Enter Username: ")
    username = client_sock.recv(1024).decode().strip()
    client_sock.send(b"Enter Password: ")
    password = client_sock.recv(1024).decode().strip()
    
    attempts = 3
    while attempts > 0:
        try:
            # Use SQLite to verify credentials
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            
            if user:
                client_sock.send(b"Login successful!\n")
                conn.close()
                return True
            else:
                client_sock.send(b"Invalid credentials!\n")
                attempts -= 1
                if attempts > 0:
                    client_sock.send(b"Try again.\nEnter Username: ")
                    username = client_sock.recv(1024).decode().strip()
                    client_sock.send(b"Enter Password: ")
                    password = client_sock.recv(1024).decode().strip()
                elif attempts == 0:
                    client_sock.send(b"Too many failed attempts.\n ---EXITING---")
                    print(f"Too many failed attempts. Connection closed with {client_sock}")
                    conn.close()
                    return False
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            client_sock"""
    # -------------------------------


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen()
    print("[*] Server listening...")

    while True:
        try:
            client, address = server.accept()
            with CLIENTS_LOCK:
                UACL.append(client)    # add to unauthenticated clients list
            print(f"[+] Accepted connection from {address}")
            threading.Thread(target=handle_client, args=(client, address)).start()

            """ remove [ handler_thread.join() ] since it let only one thread at time ,
                This means the server will only handle one client at a time, 
                waiting for each to disconnect before accepting a new one.
                But we want to handle clients concurrently or parallaly, 
                :. we remove [ handler_thread.join() ] so the server an accept multiple client in parallel """
            
        except Exception as e:
            print(e)
            break
            
    server.close()
    
if __name__ == '__main__':
    main()


#######<------SFH------->####### --> start form here agian 
# ??? --> need to test and recheck

# >[number]   --> we do next or later.

""" /-------------------------------------------------------------------------------------------------/ """
# 1. will use the sql instead of the file handling to access and minupulate the credential data