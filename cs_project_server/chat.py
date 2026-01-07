import threading
from utils import logger, MAX_BUFFER_SIZE
import socket_server
import shared_data
from client_handler import Client
import time
import os

class Chat:
    _chat_id = 1
    _max_chat_size = os.getenv("MAX_CHAT_SIZE", 2)
    def __init__(self, client1: Client = None):
        self.chat_id = Chat._chat_id
        Chat._chat_id += 1
        self.chat_clients = []
        self.full = False
        if client1:
            self.add_client(client1)
        threading.Thread(target=self.chatManager).start()

    def add_client(self, client: Client) -> bool:
        """
        Add a client to the chat.

        args:
            client (ClientConnection): The client to add.
        returns:
            bool: True if the client was added, False otherwise.
        """
        if len(self.chat_clients) < int(Chat._max_chat_size):
            self.chat_clients.append(client)
            client.room_id = self.chat_id
            if len(self.chat_clients) == int(Chat._max_chat_size):
                self.full = True
            return True
        return False

    def broadcast(self, message: str):
        for client in self.chat_clients:
            try:
                client.socket.sendall(message.encode("utf-8"))
            except Exception as e:
                logger.error(f"Failed to send message to {client.address}: {e}")

    def send_message(self,from_client: Client, to_client: Client, message: str):
        try:
            message = f"[{from_client.client_name}]: {message}"
            to_client.socket.sendall(message.encode("utf-8"))
        except Exception as e:
            logger.error(f"Failed to send message to {to_client.address}: {e}")
            self.remove_client(to_client)


    def send_message_to_all(self, message: str):
        for client in self.chat_clients:
            try:
                client.socket.sendall(message.encode("utf-8"))
            except Exception as e:
                logger.error(f"Failed to send message to {client.address}: {e}")

    def chatManager(self):
        logger.info(f"Starting chat {self.chat_id}")
        while True:
            for client in self.chat_clients:
                if client.socket is None:
                    logger.info(f"Client {client.address} disconnected from chat {self.chat_id}")
                    self.chat_clients.remove(client)
                    if len(self.chat_clients) == 0:
                        self.close_chat()
                        return

                if client.message_queue:
                    message = client.message_queue.pop(0)
                    for other_client in self.chat_clients:
                        if other_client != client:
                            self.send_message(client, other_client, message)
            time.sleep(0.1)  # Prevent busy waiting

    def close_chat(self):
        logger.info("Closing chat {self.chat_id}")
        for client in self.chat_clients:
            try:
                client.socket.close()
            except Exception as e:
                logger.error(f"Error closing connection for {client.address}: {e}")
        self.chat_clients.clear()
        if self in shared_data.chat_rooms:
            shared_data.chat_rooms.remove(self)

    def remove_client(self, client: Client):
        if client in self.chat_clients:
            self.chat_clients.remove(client)
            client.room_id = None
            self.full = False
            self.send_message_to_all(f"{client.client_name} has left the chat.\n")
            logger.info(f"Client {client.address} removed from chat {self.chat_id}")
            if len(self.chat_clients) == 0:
                self.close_chat()


    def __repr__(self):
        return f"Chat Room: {self.chat_id} | Users: {(",".join([client.client_name for client in self.chat_clients]))}"

if __name__ == "__main__":
    pass