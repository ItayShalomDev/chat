from utils import logger, MAX_CONNECTIONS, MAX_BUFFER_SIZE
import socket
import threading
import os
import time
import chat
import socket_server
import shared_data
from client_handler import Client

class ConnectionHandler:
    _client_id = 0

    @staticmethod
    def start_server(host=os.getenv("SERVER_HOST", "127.0.0.1"), port=int(os.getenv("SERVER_PORT", 10000))) -> socket.socket:
        """
        Start a socket server.
        args:
            host (str): The host IP address to bind the server to, defaults to env parameter.
            port (int): The port number to bind the server to, defaults to env parameter.
        returns:
            socket.socket: The server socket.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen()
        logger.info(f"Server listen on {host}:{port}")
        return server_socket

    @staticmethod
    def list_available_rooms() -> str:
        """
        List available chat rooms.
        returns:
            str: A string representation of available chat rooms.
        """

        available_rooms = [str(chat) + "\n" for chat in shared_data.chat_rooms if not chat.full]
        return ", ".join(available_rooms) if available_rooms else "No available rooms"

    @staticmethod
    def wait_room_for_client(client_socket, address):
        logger.info(f"Accepted connection from {address}")
        try:
            client_socket.sendall("Welcome! Please write your name: ".encode("utf-8"))
            client_name: str = client_socket.recv(MAX_BUFFER_SIZE).decode("utf-8").strip()
            logger.info(f"Client {address} set name to {client_name}")
            if shared_data.chat_rooms and any(not chat.full for chat in shared_data.chat_rooms):
                client_socket.sendall(f"Hello {client_name}, join Available chat rooms (type the id):\n{ConnectionHandler.list_available_rooms()}\nor create new chat (type 'new')".encode("utf-8"))
            else:
                client_socket.sendall(f"Hello {client_name}, currently there are no available rooms\nSend 'new' to create chat or wait for rooms (refresh by sending a message)".encode("utf-8"))
            client: Client = Client(address, client_socket, client_id=ConnectionHandler._client_id, client_name=client_name)
            shared_data.clients.append(client)
            while True:
                data = client_socket.recv(MAX_BUFFER_SIZE).decode("utf-8")
                if data == "new":
                    ConnectionHandler.create_new_chat(client)
                    break
                else:
                    try:
                        room_id = int(data)
                        if ConnectionHandler.assign_client_to_room_by_id(client, room_id):
                            client_socket.sendall(f"Joined chat room {room_id}.\n".encode("utf-8"))
                            break
                        else:
                            client_socket.sendall(f"Chat room {room_id} is full or does not exist.\nPlease select another room: {ConnectionHandler.list_available_rooms()} :\n".encode("utf-8"))
                    except ValueError:
                        client_socket.sendall(f"Please select a room to join:\n{ConnectionHandler.list_available_rooms()}\n".encode("utf-8"))

                logger.info(f"Received data from {client_name} {address}: {data}")
        except Exception as e:
            logger.error(f"Error handling client {address}: {e}")
            client_socket.close()

    @staticmethod
    def create_new_chat(client: Client) :
        """
        Handle creating a new chat room.
        args:
            client (Client): The client requesting a new chat room.
            client_socket (socket.socket): The client's socket.
        returns:
            None
        """
        new_chat = chat.Chat(client)
        shared_data.chat_rooms.append(new_chat)
        logger.info(f"Created new chat room {new_chat.chat_id} for client {client.address}")
        client.socket.sendall(f"New chat room {new_chat.chat_id} created.\n"
                              f"Waiting for another client to join...\n".encode("utf-8"))
        threading.Thread(target=client.listen).start()
        threading.Thread(target=new_chat.chatManager).start()
        socket_server.broadcast_message(f"A new chat room has been created by {client.client_name}. Room ID: {new_chat.chat_id}.\n", exclude_busy_users=True)

    @staticmethod
    def assign_client_to_room_by_id(client: Client, chat_room_id: int) -> bool:
        """
        Assign a client to an available chat room.
        args:
            client (Client): The client to assign.
            chat_room_id (int): The ID of the chat room to assign the client to.
        returns:
            bool: True if the client was assigned, False otherwise.
        """
        chat_room = next((chat for chat in shared_data.chat_rooms if chat.chat_id == chat_room_id), None)
        if chat_room and not chat_room.full:
            chat_room.send_message_to_all(f"{client.client_name} has joined the chat room.\n")
            chat_room.add_client(client)
            client.socket.sendall(f"Joined chat room {chat_room_id}. You can start chatting now!\n".encode("utf-8"))
            logger.info(f"Client {client.address} joined chat room {chat_room_id}")
            client.room_id = chat_room_id
            threading.Thread(target=client.listen()).start()
            return True
        return False

    @staticmethod
    def assign_client_to_room_by_users(client: Client) -> bool:
        """
        Assign a client to an chat room by the users inside.
        args:
            client (Client): The client to assign.
        returns:
            bool: True if the client was assigned, False otherwise.
        """
        pass

    @staticmethod
    def handle_new_client_connections(server_socket: socket.socket):
        """
        Handle new client connections.
        args:
            server_socket (socket.socket): The server socket to accept connections on.
        returns:
            None
        """
        logger.info("Server is running and waiting for connections...")
        while True:
            ConnectionHandler.remove_disconnected_clients()
            time.sleep(1)
            if len(shared_data.clients) >= MAX_CONNECTIONS:
                logger.warning("Max connections reached, refusing new connection.")
                continue

            client_socket, address = server_socket.accept()
            client_handler = threading.Thread(target=ConnectionHandler.wait_room_for_client, args=(client_socket, address))
            client_handler.start()
            ConnectionHandler._client_id += 1

    @staticmethod
    def remove_disconnected_clients():

        try:
            # clients = [client for client in shared_data.clients if client.socket.fileno() != -1]
            pass
        except Exception as e:
            logger.error(f"Error removing disconnected clients: {e}")


if __name__ == "__main__":
    pass
