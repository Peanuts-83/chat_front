# For relative imports to work in Python 3.6
import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from modules.login import LoginClient
from modules.chat import ChatClient


class AppManager:
    user_id: int = None

    def __init__(self):
        self.login_client = LoginClient(self)
        self.chat_client = None
        self.show_login()

    def show_login(self):
        if self.login_client:
            self.login_client.deiconify()
            self.login_client.initFields()
        self.login_client.lift()
        self.login_client.mainloop()

    def show_chat(self, user_id: int):
        self.login_client.withdraw()
        self.user_id = user_id
        self.chat_client = ChatClient(self, self.login_client, self.user_id)
        self.chat_client.lift()
