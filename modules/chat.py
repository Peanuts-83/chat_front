# For relative imports to work in Python 3.6
import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import json
import threading
import customtkinter as ctk
import websocket
from PIL import Image

class ChatClient(ctk.CTkToplevel):
    def __init__(self, manager, master, user_id) -> None:
        super().__init__(master)
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
        #  leftFrame
        self.leftFrame = ctk.CTkFrame(self, width=80, fg_color="transparent")
        self.leftFrame.grid(row=0, column=0, sticky="enws", padx=0, pady=0)
        self.leftFrame.rowconfigure(0, weight=1)
        self.leftFrame.rowconfigure(1, weight=10)
        self.leftFrame.columnconfigure(0, weight=1)
        self.leftFrame.columnconfigure(1, weight=1)
        # settings
        self.settings_btn = ctk.CTkButton(self.leftFrame, text="Settings", command=self.open_settings)
        self.settings_btn.grid(row=1, column=0, sticky="nw", padx=(10,5), pady=0)
        self.mode_btn = ctk.CTkSwitch(self.leftFrame, text="Mode", command=self.switch_mode)
        self.mode_btn.grid(row=1, column=1, sticky="ne", padx=(5,10), pady=0)
        # users
        self.users = ['General','titi','tata','tutu','pipo']
        self.userTabFrame = ctk.CTkScrollableFrame(self.leftFrame, width=80)
        self.userTabFrame.grid(row=0, column=0, columnspan=2, sticky="esw", padx=0, pady=10)
        self.user_btns = {}
        for user in self.users:
            btn = ctk.CTkButton(self.userTabFrame, text=user, command=lambda u=user: self.select_user(u) )
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

        # all layout elements
        self.layout_elements = [self.leftFrame, self.settings_btn, self.mode_btn, self.userTabFrame, list(self.user_btns.values()), self.chat_display, self.input_field, self.send_button]

        # events
        self.input_field.bind("<Return>", lambda event: self.send_message()) # Return KEY
        self.protocol("WM_DELETE_WINDOW", self.on_close) # close window
        self.bind("<Configure>", self.on_resize) # resize et calcul des rows/cols

        ## connexion
        self.websocket = None
        self.connect_server()

        # start thread to receive msg
        self.receive_thread = threading.Thread(target=self.receive_message, daemon=True)
        self.receive_thread.start()

    # USER interraction #
    def select_user(self, user):
        self.current_user = user

    def open_settings(self):
        print('open settings')

    # def switch_mode(self):
    #     """
    #     toggle light/dark modes - wip
    #     """
    #     dark = self.mode_btn.get()
    #     if dark == 1:
    #         self._set_appearance_mode("dark")
    #     else:
    #         self._set_appearance_mode("light")
    #     self.update_widgets(self)

    # def update_widgets(self, widget):
    #     """
    #     update each UI item
    #     """
    #     for el in widget.winfo_children():
    #         if isinstance(el, ctk.CTkBaseClass):
    #             try:
    #                 el.configure(**el.configure())
    #             except:
    #                 el.configure()
    #             finally:
    #                 el.update()
    #         self.update_widgets(el)
    #         for subel in el.winfo_children():
    #             try:
    #                 subel.configure(**subel.configure())
    #             except:
    #                 subel.configure()
    #             finally:
    #                 subel.update()

    def on_resize(self, event):
        new_height = int(self.winfo_height())
        self.chat_display.configure(height=new_height - 60)

    # CHAT communication #
    def connect_server(self):
        self.websocket = websocket.create_connection(f"ws://127.0.0.1:8000/ws/chat/{self.user_id}")

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
