# For relative imports to work in Python 3.6
from cProfile import label
import os, sys
from turtle import width
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
        self.geometry("400x310")
        self.minsize(400,310)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # layout
        # users
        self.users = ['toto','titi','tata','tutu','pipo']
        self.tabFrame = ctk.CTkScrollableFrame(self, width=80)
        self.tabFrame.grid(row=0, column=0, sticky="enws", padx=0, pady=10)
        self.user_btns = {}
        for user in self.users:
            btn = ctk.CTkButton(self.tabFrame, text=user, command=lambda u=user: self.select_user(u) )
            btn.pack(fill='x', padx=0, pady=1)
            self.user_btns[user] = btn
        # chat > readonly = {state: "disabled"} / readwrite = {state: "normal"}
        self.chat_display = ctk.CTkTextbox(self, width=300, height=250, state="disabled")
        self.chat_display.grid(row=0, column=1, columnspan=2, sticky="enw", padx=10, pady=10)
        # saisie
        self.input_field = ctk.CTkEntry(self, width=300)
        self.input_field.grid(row=1, column=0, columnspan=2, sticky='esw', padx=(10,5), pady=(0,10))
        # btn envoi
        self.send_button = ctk.CTkButton(self, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=2, sticky='esw', padx=(5,10), pady=(0,10))

        # events
        self.input_field.bind("<Return>", lambda event: self.send_message())
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Configure>", self.on_resize) # resize et calcul des rows/cols

        ## connexion
        self.websocket = None
        self.connect_server()

        # start thread to receive msg
        self.receive_thread = threading.Thread(target=self.receive_message, daemon=True)
        self.receive_thread.start()


    # @sio.event
    def connect_server(self):
        self.websocket = websocket.create_connection(f"ws://127.0.0.1:8000/ws/chat/{self.user_id}")

    def select_user(self, user):
        self.current_user = user

    def on_resize(self, event):
        new_height = int(self.winfo_height())
        self.chat_display.configure(height=new_height - 60)

    def receive_message(self) -> None:
        while self.websocket is not None:
            try:
                message = self.websocket.recv()
                if message:
                    self.display_message(message)
            except Exception as e:
                print(f"Disconnected: {e}")
                self.websocket = None

    def open_login_window(self) -> None:
        self.manager.show_login()

    def display_message(self, message: dict["msg":str, "from":int|None] | str) -> None:
        l_message = ""
        if type(json.loads(message)) is str:
            l_message = json.loads(message)
            self.chat_display.configure(state="normal")
            self.chat_display.insert("end", f"{l_message}")
        else:
            l_message, from_id = [json.loads(message)['msg'], json.loads(message)['from']]
            if from_id is None:
                self.chat_display.configure(state="normal")
                self.chat_display.insert("end", f"{l_message}")
            else:
                self.chat_display.configure(state="normal")
                self.chat_display.insert("end", f"User{from_id}: {l_message}")
        self.chat_display.yview("end") # scroll down
        self.chat_display.configure(state="disabled")

    def send_message(self):
        message = self.input_field.get()
        if message:
            self.websocket.send(message)
            self.chat_display.configure(state="normal")
            self.chat_display.insert("end", f"You: {message}\n")
            self.chat_display.yview("end")
            self.input_field.delete(0, "end")
            self.chat_display.configure(state="disabled")

    def on_close(self):
        self.websocket.close()
        self.destroy()
        self.open_login_window()
