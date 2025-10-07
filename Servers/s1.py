import socket
import threading
import sys

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
                except Exception as e:
                    print(f"Connection Closed due to an Exeption: {e}")
                    # ACL.remove(A_client)                                    ???
                    # CLIENTS.remove(A_client)                                ???
                    # A_client.close()                                        ???
                    terminator(A_client)                                      # Termination



def handle_client(client_sock, client_address):
    with client_sock:       
        authentication(client_sock)

        while True:
            try:
                data = client_sock.recv(1024)
                if not data:
                    break
                print(f"Received from {client_address}: {data.decode()}")
                broadcast(data, client_sock)
            except:
                break
    # -----------------------------

    with CLIENTS_LOCK:
        if client_sock in CLIENTS and client_sock in ACL:          
            terminator(client_sock)                                             # Termination
    print(f"Connection closed: {client_address}")

    # ------------------------------

def terminator(client_sock):
    with CLIENTS_LOCK:
        client_sock.send(b" DISCONNECTED")
        ACL.remove(client_sock)
        CLIENTS.remove(client_sock)
        client_sock.shutdown(socket.SHUT_RDWR)
        client_sock.close()



def authentication(client_sock):
    client_sock.send(b"\t\tWelcome! To the Chat`!`\nDo SignUp/SingIn")
    client_sock.send(b"Type [ 1 ] for signUp or [ 2 ] for SignIn")
    opt = client_sock.recv(1024).decode()

    if opt == "1":
        signup(client_sock)
        if not signin(client_sock):             # Exit              [ if statment works if the  given condition is TRUE or NOT FALSE ]
            terminator(client_sock)             # Termination
            
        else:
            ACL.append(client_sock)             # Authenticated
            UACL.remove(client_sock)
        
    elif opt == "2":
        if not signin(client_sock):             # if signin -> Trur then the if body will not execut .  # Exit
            terminator(client_sock)             # Termination
            
        else:
            ACL.append(client_sock)             # Authenticated
            UACL.remove(client_sock)
    else:
        client_sock.send(b"Invalid option. Connection closed.\n")
        terminator(client_sock)                 # Termination
        


def signup(client_sock):
    client_sock.send(b"Enter Username: ")
    username = client_sock.recv(1024).decode().strip()
    client_sock.send(b"Enter Password: ")
    password = client_sock.recv(1024).decode().strip()
    # Here you would normally save the username and password securely be will do this later
    client_sock.send(b"Signup successful!\n")
    client_sock.send(f"Hello {username}".encode("utf-8"))      # ???
    with open("users.txt", "a") as f:
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
        elif attempts < 3:
            client_sock.send(b"Too mant failded attemps.\n ---EXITING---")
            print(f"Too many failed attempts. Connection closed with {client_sock}")
            return False
                    
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
                CLIENTS.append(client) # Add to all clients list
                UACL.append(client)    # add to unauthenticated clients list
            print(f"[+] Accepted connection from {address} : {client}")
            threading.Thread(target=handle_client, args=(client, address), daemon=True).start()
        except KeyboardInterrupt:
            break
    server.close()

if __name__ == '__main__':
    main()


#######<------SFH------->####### --> start form here agian 
# ??? --> need to test and recheck