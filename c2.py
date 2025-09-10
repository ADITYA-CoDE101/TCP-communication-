import socket
import threading

DESTINATION = "127.0.0.1"
PORT = 9898

def send(client):
    while True:
        try:
            mesg = str(input("-->"))
            if mesg.lower() == "exit":
                print("----EXIT----")
                client.close()
                # break
                exit()
            client.send(mesg.encode())
        except:
            print("[1] ERROR !!!")
            break

def recevie(client):
    while True:
        try:
            response = client.recv(4092).decode()
            if not response:
                print("Connection Lost...")
                break
            print(f"\n\t\t{response}")
        except:
            print("[2] ERROR!!!")
            break

def main():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((DESTINATION, PORT))

        sender_Th = threading.Thread(target=send, args=(client,))
        recevie_th = threading.Thread(target=recevie, args=(client,))

        sender_Th.start()
        recevie_th.start()

        sender_Th.join()
        recevie_th.join()
    except KeyboardInterrupt:
        client.close()
        exit()
   
if __name__ == "__main__":
    main()

