import socket
import threading
import sys

DESTINATION = "127.0.0.1"
PORT = 9898

def send(client):
    while not stop_event.is_set():
        try:
            mesg = str(input(""))
            if mesg.lower() == "--exit":
                print("----EXIT----")
                # -----------------------------------
                    # actually close the connection properly
                try:
                    client.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                # -----------------------------------
                client.close()
                stop_event.set()
                break
            client.send(mesg.encode())
        except OSError:
            print("[1] Connection Lost ...")
            stop_event.set()
            break

def receive(client):
    while not stop_event.is_set():
        try:
            response = client.recv(4092).decode()
            if not response:
                print("[2] Connection Lost...")
                # -----------------------------------
                    # actually close the connection properly
                try:
                    client.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                # -----------------------------------
                stop_event.set()
                break
            if response == "INVALID_CREDENTIALS":
                print("Invalid credentials. Closing connection.")
                # -----------------------------------
                    # actually close the connection properly
                try:
                    client.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                # -----------------------------------
                client.close()
                stop_event.set()
                break
            print(f"\n\t\t\t{response}")
        except OSError:
            print("[3] Connection Lost ...")
            stop_event.set()
            break
    
def main():
    global stop_event
    stop_event = threading.Event()
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((DESTINATION, PORT))

        sender_thread = threading.Thread(target=send, args=(client,))
        receiver_thread = threading.Thread(target=receive, args=(client,))

        sender_thread.start()
        receiver_thread.start()

        while not stop_event.is_set():
            sender_thread.join(timeout=0.1)
            receiver_thread.join(timeout=0.1)
            if not sender_thread.is_alive() and not receiver_thread.is_alive(): # Here it stats that both threads needs to be alive for both of them to run.
                break
    except KeyboardInterrupt:
        print("Interrupted. Closing client.")
        stop_event.set()
        client.close()
        client.close()


if __name__ == "__main__":
    main()
