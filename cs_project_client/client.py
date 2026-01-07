import socket
import os
import threading
import dotenv
import utils
from utils import logger
import time
dotenv.load_dotenv()
MAX_PACKET_SIZE = int(os.getenv("MAX_PACKET_SIZE", 1024))

def start_client(host=os.getenv("SERVER_HOST", "127.0.0.1"), port=int(os.getenv("SERVER_PORT", 10000))):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket

def get_message(client_socket: socket.socket) -> str:
    data = client_socket.recv(MAX_PACKET_SIZE)
    return data.decode("utf-8")

def listen_for_messages(client_socket: socket.socket):
    while True:
        try:
            message = get_message(client_socket)
            if message:
                print(f"{message}")
            time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            raise e

def send_message(client_socket: socket.socket, message: str):
    client_socket.sendall(message.encode("utf-8"))

def send_messages_loop(client_socket: socket.socket):
    while True:
        message = input("")
        if message.lower() == 'exit':
            raise KeyboardInterrupt
        send_message(client_socket, message)

if __name__ == "__main__":
    client_socket = start_client()
    print("Connected to server")
    print(get_message(client_socket))
    try:
        threading.Thread(target=listen_for_messages, args=(client_socket,), daemon=True).start()
        # threading.Thread(target=send_messages_loop, args=(client_socket,), daemon=True).start()
        send_messages_loop(client_socket)
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        client_socket.close()
        print("Connection closed")