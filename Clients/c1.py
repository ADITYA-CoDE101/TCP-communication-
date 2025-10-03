import socket
import threading
import sys

DESTINATION = "127.0.0.1"
PORT = 9898

def send(client):
    while True:
        try:
            mesg = str(input(""))
            if mesg.lower() == "exit":
                print("----EXIT----")
                client.close()
                break
                # exit()
            client.send(mesg.encode())
        except OSError:
            print("[1] Connection Lost ...")
            break
    exit()

def receive(client):
    while True:
        try:
            response = client.recv(4092).decode()
            if not response:
                print("[2] Connection Lost...")
                break
            if response == "INVALID_CREDENTIALS":
                print("Invalid credentials. Closing connection.")
                client.close()
                sys.exit(1)
            print(f"\n\t\t\t{response}")
        except OSError:
            print("[3] Connection Lost ...")
            break
    sys.exit()
    
def main():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((DESTINATION, PORT))

        sender_thread = threading.Thread(target=send , args=((client,)))
        receiver_thread = threading.Thread(target=receive, args=((client,)))

        sender_thread.start()
        receiver_thread.start()

        sender_thread.join()
        receiver_thread.join()
    except KeyboardInterrupt:
        client.close()
        exit()
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        client.close()


if __name__ == "__main__":
    main()
