import socket
import threading

DESTINATION = "127.0.0.1"
PORT = 9898

def send(client):
    while True:
        try:
            mesg = input("-->")
            if mesg.lower() == "exit":
                client.close()
                exit()
            client.send(mesg.encode())
        except:
            print("1")
            break

def receive(client):
    while True:
        try:
            response = client.recv(4092).decode()
            if not response:
                print("Connection lost.....")
                break
            print(f"\nReceived: {response}",
                  "\n-->")
        except:
            print("2")
            break
    
    
def main():

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((DESTINATION, PORT))

    sender_thread = threading.Thread(target=send , args=((client,)))
    receiver_thread = threading.Thread(target=receive, args=((client,)))

    sender_thread.start()
    receiver_thread.start()

    sender_thread.join()
    receiver_thread.join()
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        client.close()


if __name__ == "__main__":
    main()
