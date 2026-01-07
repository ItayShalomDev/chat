import threading
import os
import utils
from utils import logger, MAX_CONNECTIONS, MAX_BUFFER_SIZE
import chat
import shared_data
import connection
import client_handler

def admin_commands(msg):
    """
    Handle admin commands.
    args:
        msg (str): The admin command message.
    returns:
        None
    """
    msg = msg.strip().lower()
    match msg:
        case "status":
            logger.info("Server is running and accepting connections.")
            show_connected_clients()
        case "broadcast":
            message = input("Enter message to broadcast: ")
            broadcast_message(message)
        case _:
            print("Available commands: status, broadcast")

def show_connected_clients() :
    """
    Prints all connected clients.
    """
    print(f"Connected clients: {len(shared_data.clients)}")
    for client in shared_data.clients:
        print(f"Client: {client}")

def broadcast_message(message: str, exclude_busy_users: bool=False) -> bool:
    """
    Broadcast a message to all connected clients.
    args:
        message (str): The message to broadcast.
        exclude_busy_users (bool): If True, exclude clients in chat rooms.
    returns:
        bool: True if broadcast was successful, False otherwise.
    """
    payload = f"[Broadcast] {message}\n"
    for client in shared_data.clients:
        if exclude_busy_users and client.room_id is not None:
            continue
        print("Sending to", client.client_name)
        try:
            client.socket.sendall(payload.encode("utf-8"))
        except Exception as e:
            logger.error(f"Failed to send message to {client.address}: {e}")
            return False
    print("Broadcast complete.")
    return True

if __name__ == "__main__":
    server_socket = connection.ConnectionHandler.start_server()
    threading.Thread(target=connection.ConnectionHandler.handle_new_client_connections, args=(server_socket,)).start()
    logger.debug("Admin command interface started.")

    while True:
        if os.getenv("ENABLE_ADMIN_COMMANDS", "true").lower() == "true":
            command = input("Enter admin command (type 'exit' to quit): ")
            if command.lower() == "exit":
                logger.info("Shutting down server...")
                server_socket.close()
                break
            else:
                admin_commands(command)
