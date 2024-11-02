# For relative imports to work in Python 3.6
import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import json
import threading
import customtkinter as ctk
import websocket


class ChatClient(ctk.CTk):
    def __init__(self, manager, user_id) -> None:
        super().__init__()
        self.manager = manager
        self.user_id= user_id

        self.title("Meooow")
        self.geometry("400x300")
        self.grid_columnconfigure((0,1), weight=1)

        # layout
        self.chat_display = ctk.CTkTextbox(self, width=380, height=200)
        self.chat_display.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        self.input_field = ctk.CTkEntry(self, width=280)
        self.input_field.grid(row=0, column=0, padx=(10,0), pady=10)

        self.send_button = ctk.CTkButton(self, text="Send", command=self.send_message)
        self.send_button.grid(row=0, column=1, padx=(0,10), pady=10)

        # events
        self.input_field.bind("<Return>", lambda event: self.send_message())
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        ## connexion
        self.websocket = None
        self.connect_server()

        # start thread to receive msg
        self.receive_thread = threading.Thread(target=self.receive_message, daemon=True)
        self.receive_thread.start()


    # @sio.event
    def connect_server(self):
        self.websocket = websocket.create_connection(f"ws://127.0.0.1:8000/ws/chat/{self.user_id}")

    def receive_message(self) -> None:
        while self.websocket is not None:
            # self.chat_display.insert("end", "Connected to server\n")
            try:
                message = self.websocket.recv()
                if message:
                    self.display_message(message)
            except Exception as e:
                print(f"Disconnected: {e}")
                # if self.websocket is not None:
                # self.websocket.close()
                self.websocket = None

    def open_login_window(self) -> None:
        self.manager.show_login()

    def display_message(self, message: dict["msg":str, "from":int|None] | str) -> None:
        l_message = ""
        if type(json.loads(message)) is str:
            l_message = json.loads(message)
            self.chat_display.insert("end", f"{l_message}")
        else:
            l_message, from_id = [json.loads(message)['msg'], json.loads(message)['from']]
            if from_id is None:
                self.chat_display.insert("end", f"{l_message}")
            else:
                self.chat_display.insert("end", f"User{from_id}: {l_message}")
        self.chat_display.yview("end") # scroll down

    def send_message(self):
        message = self.input_field.get()
        if message:
            self.websocket.send(message)
            self.chat_display.insert("end", f"You: {message}\n")
            self.chat_display.yview("end")
            self.input_field.delete(0, "end")

    def on_close(self):
        self.websocket.close()
        self.destroy()
        self.open_login_window()
