from utils import logger, MAX_BUFFER_SIZE
import socket_server
import shared_data
import socket

class Client:
    def __init__(self, address, client_socket, client_id, client_name):
        self.address = address
        self.socket = client_socket
        self.client_id = client_id
        self.client_name = client_name
        self.room_id = None
        self.message_queue = []

    def listen(self):
        try:
            while True:
                data = self.socket.recv(MAX_BUFFER_SIZE).decode("utf-8")
                if data:
                    logger.info(f"Received message from {self.address}: {data}")
                    self.message_queue.append(data)
                else:
                    logger.info(f"Client {self.address} disconnected.")
                    self.disconnect_client("Client disconnected.")
                    break
        except Exception as e:
            logger.error(f"Error receiving message from {self.address}: {e}")
            self.disconnect_client("Error receiving message.")

    def disconnect_client(self, reason: str = ""):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass  # already closed / not connected
        try:
            self.socket.close()
        except OSError:
            pass
        try:
            shared_data.clients.remove(self)
        except ValueError:
            pass
        logger.info(f"Client {getattr(self, 'address', '?')} disconnected. {reason}")
        self.socket = None
        for chat in shared_data.chat_rooms:
            if chat.chat_id == self.room_id:
                chat.remove_client(self)
                break

    def __repr__(self):
        return f"Client({self.client_name}, {self.address}, ID: {self.client_id}, Room: {self.room_id})"

if __name__ == "__main__":
    pass