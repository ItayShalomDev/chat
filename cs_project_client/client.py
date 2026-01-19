import socket
import os
import threading
import dotenv
import utils
from utils import logger
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox
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
                utils.cprint(f"{message}", "green")
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

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Socket Client")
        self.root.geometry("700x600")
        self.root.minsize(600, 500)
        self.client_socket = None
        self.is_connected = False

        self.bg_color = "#2b2b2b"
        self.fg_color = "#ffffff"
        self.input_bg = "#3c3f41"
        self.button_bg = "#4a90e2"
        self.button_hover = "#357abd"
        self.disconnect_bg = "#e74c3c"
        self.disconnect_hover = "#c0392b"
        self.frame_bg = "#363636"

        self.root.configure(bg=self.bg_color)

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(
            self.root,
            text="Socket Client",
            font=("Segoe UI", 16, "bold"),
            bg=self.bg_color,
            fg=self.fg_color,
            pady=10
        )
        title_label.pack(fill=tk.X)

        connection_frame = tk.Frame(self.root, bg=self.frame_bg, padx=15, pady=15)
        connection_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        host_frame = tk.Frame(connection_frame, bg=self.frame_bg)
        host_frame.pack(side=tk.LEFT, padx=5)

        tk.Label(
            host_frame,
            text="Host:",
            font=("Segoe UI", 10),
            bg=self.frame_bg,
            fg=self.fg_color
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.host_entry = tk.Entry(
            host_frame,
            width=20,
            font=("Segoe UI", 10),
            bg=self.input_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            borderwidth=2
        )
        self.host_entry.insert(0, os.getenv("SERVER_HOST", "127.0.0.1"))
        self.host_entry.pack(side=tk.LEFT)

        port_frame = tk.Frame(connection_frame, bg=self.frame_bg)
        port_frame.pack(side=tk.LEFT, padx=5)

        tk.Label(
            port_frame,
            text="Port:",
            font=("Segoe UI", 10),
            bg=self.frame_bg,
            fg=self.fg_color
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.port_entry = tk.Entry(
            port_frame,
            width=10,
            font=("Segoe UI", 10),
            bg=self.input_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            borderwidth=2
        )
        self.port_entry.insert(0, os.getenv("SERVER_PORT", "10000"))
        self.port_entry.pack(side=tk.LEFT)

        self.connect_button = tk.Button(
            connection_frame,
            text="Connect",
            command=self.connect_to_server,
            font=("Segoe UI", 10, "bold"),
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.button_hover,
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=5
        )
        self.connect_button.pack(side=tk.LEFT, padx=5)
        self.connect_button.bind("<Enter>", lambda e: self.connect_button.config(bg=self.button_hover))
        self.connect_button.bind("<Leave>", lambda e: self.connect_button.config(bg=self.button_bg))

        self.disconnect_button = tk.Button(
            connection_frame,
            text="Disconnect",
            command=self.disconnect_from_server,
            state=tk.DISABLED,
            font=("Segoe UI", 10, "bold"),
            bg=self.disconnect_bg,
            fg=self.fg_color,
            activebackground=self.disconnect_hover,
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=5
        )
        self.disconnect_button.pack(side=tk.LEFT, padx=5)

        messages_frame = tk.Frame(self.root, bg=self.bg_color, padx=10, pady=5)
        messages_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            messages_frame,
            text="Messages",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_color,
            fg=self.fg_color,
            anchor=tk.W
        ).pack(anchor=tk.W, pady=(0, 5))

        text_border_frame = tk.Frame(messages_frame, bg="#1a1a1a", padx=1, pady=1)
        text_border_frame.pack(fill=tk.BOTH, expand=True)

        self.messages_text = scrolledtext.ScrolledText(
            text_border_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=20,
            font=("Consolas", 10),
            bg=self.input_bg,
            fg=self.fg_color,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            insertbackground=self.fg_color
        )
        self.messages_text.pack(fill=tk.BOTH, expand=True)

        self.messages_text.tag_config("received", foreground="#4ade80", font=("Consolas", 10))
        self.messages_text.tag_config("sent", foreground="#60a5fa", font=("Consolas", 10))
        self.messages_text.tag_config("error", foreground="#f87171", font=("Consolas", 10, "bold"))
        self.messages_text.tag_config("info", foreground="#a1a1aa", font=("Consolas", 10, "italic"))

        input_frame = tk.Frame(self.root, bg=self.bg_color, padx=10, pady=10)
        input_frame.pack(fill=tk.X)

        tk.Label(
            input_frame,
            text="Message",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_color,
            fg=self.fg_color,
            anchor=tk.W
        ).pack(anchor=tk.W, pady=(0, 5))

        input_control_frame = tk.Frame(input_frame, bg=self.bg_color)
        input_control_frame.pack(fill=tk.X)

        entry_border_frame = tk.Frame(input_control_frame, bg="#1a1a1a", padx=1, pady=1)
        entry_border_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.message_entry = tk.Entry(
            entry_border_frame,
            font=("Segoe UI", 11),
            bg=self.input_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.message_entry.pack(fill=tk.BOTH, padx=5, pady=5)
        self.message_entry.bind('<Return>', lambda event: self.send_message_gui())

        self.send_button = tk.Button(
            input_control_frame,
            text="Send",
            command=self.send_message_gui,
            state=tk.DISABLED,
            font=("Segoe UI", 10, "bold"),
            bg=self.button_bg,
            fg=self.fg_color,
            activebackground=self.button_hover,
            activeforeground=self.fg_color,
            relief=tk.FLAT,
            cursor="hand2",
            padx=30,
            pady=8
        )
        self.send_button.pack(side=tk.LEFT)
        self.send_button.bind("<Enter>", lambda e: self.send_button.config(bg=self.button_hover) if self.send_button['state'] == tk.NORMAL else None)
        self.send_button.bind("<Leave>", lambda e: self.send_button.config(bg=self.button_bg) if self.send_button['state'] == tk.NORMAL else None)

    def append_message(self, message, tag="info"):
        self.messages_text.config(state=tk.NORMAL)
        self.messages_text.insert(tk.END, message + "\n", tag)
        self.messages_text.see(tk.END)
        self.messages_text.config(state=tk.DISABLED)

    def connect_to_server(self):
        try:
            host = self.host_entry.get()
            port = int(self.port_entry.get())

            self.append_message(f"Connecting to {host}:{port}...", "info")
            self.client_socket = start_client(host, port)
            self.is_connected = True

            self.append_message("Connected to server", "info")

            welcome_msg = get_message(self.client_socket)
            self.append_message(f"{welcome_msg}", "received")

            threading.Thread(target=self.listen_for_messages_gui, daemon=True).start()

            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            self.disconnect_button.bind("<Enter>", lambda e: self.disconnect_button.config(bg=self.disconnect_hover))
            self.disconnect_button.bind("<Leave>", lambda e: self.disconnect_button.config(bg=self.disconnect_bg))
            self.send_button.config(state=tk.NORMAL)
            self.host_entry.config(state=tk.DISABLED)
            self.port_entry.config(state=tk.DISABLED)

        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.append_message(f"Error: {e}", "error")
            messagebox.showerror("Connection Error", str(e))

    def disconnect_from_server(self):
        if self.client_socket:
            self.is_connected = False
            self.client_socket.close()
            self.client_socket = None

            self.append_message("Disconnected from server", "info")

            self.connect_button.config(state=tk.NORMAL)
            self.disconnect_button.config(state=tk.DISABLED)
            self.disconnect_button.unbind("<Enter>")
            self.disconnect_button.unbind("<Leave>")
            self.send_button.config(state=tk.DISABLED)
            self.host_entry.config(state=tk.NORMAL)
            self.port_entry.config(state=tk.NORMAL)

    def listen_for_messages_gui(self):
        while self.is_connected:
            try:
                message = get_message(self.client_socket)
                if message:
                    self.append_message(f"{message}", "received")
                time.sleep(0.1)
            except Exception as e:
                if self.is_connected:
                    logger.error(f"Error receiving message: {e}")
                    self.append_message(f"Error: {e}", "error")
                    self.is_connected = False
                break

    def send_message_gui(self):
        message = self.message_entry.get()
        if message:
            try:
                send_message(self.client_socket, message)
                self.append_message(f"You: {message}", "sent")
                self.message_entry.delete(0, tk.END)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                self.append_message(f"Error: {e}", "error")
                messagebox.showerror("Send Error", str(e))

    def on_closing(self):
        if self.is_connected:
            self.disconnect_from_server()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
