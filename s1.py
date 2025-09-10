import socket
import threading

IP = "127.0.0.1"
PORT = 9898
CLIENTS = []
CLIENTS_LOCK = threading.Lock()

def broadcast(message, sender_sock):
    with CLIENTS_LOCK:
        for client in CLIENTS:
            if client != sender_sock:
                try:
                    client.send(message)
                except:
                    CLIENTS.remove(client)

def handle_client(client_sock, client_address):
    with client_sock:
        while True:
            try:
                data = client_sock.recv(1024)
                if not data:
                    break
                print(f"Received from {client_address}: {data.decode()}")
                broadcast(data, client_sock)
            except:
                break
    with CLIENTS_LOCK:
        if client_sock in CLIENTS:
            CLIENTS.remove(client_sock)
    print(f"Connection closed: {client_address}")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen()
    print("[*] Server listening...")

    while True:
        try:
            client, address = server.accept()
            with CLIENTS_LOCK:
                CLIENTS.append(client)
            print(f"[+] Accepted connection from {address}")
            threading.Thread(target=handle_client, args=(client, address), daemon=True).start()
        except KeyboardInterrupt:
            break
    server.close()

if __name__ == '__main__':
    main()