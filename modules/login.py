# For relative imports to work in Python 3.6
import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import json
import customtkinter as ctk
import requests

from constants.constants import BASE_API, BASE_HTTP

class LoginClient(ctk.CTk):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager

        self.title("Meoow connection")
        self.geometry("400x300")

        self.label_username = ctk.CTkLabel(self, text="User")
        self.label_username.pack(pady=5)

        self.entry_username = ctk.CTkEntry(self)
        self.entry_username.pack(pady=5)
        self.entry_username.pack(pady=5)
        self.entry_username.focus_set() # focus sur champ Login au startup

        self.label_password = ctk.CTkLabel(self, text="Password")
        self.label_password.pack(pady=5)
        self.label_password.bind("<Return>", self.login)

        self.entry_password = ctk.CTkEntry(self, show="*")
        self.entry_password.pack(pady=5)
        self.entry_password.bind("<Return>", self.login) # touche RETURN (renvoie: self,event)

        self.login_button = ctk.CTkButton(self, text="Connexion", command=self.login)
        self.login_button.pack(pady=10)

        self.label_error = ctk.CTkLabel(self, text="", text_color="red")
        self.label_error.pack(pady=5)

        # event
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.protocol("WM_KEYDOWN")

        self.initFields()


    def initFields(self):
        self.entry_username.delete(0, "end")
        self.entry_password.delete(0, "end")
        self.label_error.configure(text="")
        self.entry_username.focus_set() # focus sur champ Login au startup

    def login(self, event=None):
        self.username = self.entry_username.get()
        self.password = self.entry_password.get()
        if self.username and self.password:
            request = self.authenticate(self.username, self.password)
            if request["status_code"]==200:
                self.open_chat_window(request["user_id"])
            else:
                self.label_error.configure(text=request["msg"])

    def authenticate(self, username: str, password: str) -> int|bool:
        try:
            response = requests.post(BASE_HTTP + BASE_API + "/login", json={"username":username, "password": password})
            return json.loads(response.content)
        except Exception as e:
            print(f"Connexion error: {e}")
        return False

    def open_chat_window(self, user_id: int):
        self.manager.show_chat(user_id)

    def on_close(self):
        self.destroy()
        sys.exit()