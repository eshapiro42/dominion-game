import requests
import time


class Administrator:
    def __init__(self, host: str = "http://localhost", port: int = 5000):
        self.host = host
        self.port = port
        self.admin_base_url = f"{self.host}:{self.port}/admin"

    # BASIC ADMIN APIS
    def num_active_games(self):
        r = requests.get(f"{self.admin_base_url}/num_active_games")
        return r.json()
    
    def list_active_games(self):
        r = requests.get(f"{self.admin_base_url}/list_active_games")
        return r.json()

    def kill_game(self, room: str):
        r = requests.get(f"{self.admin_base_url}/kill_game/{room}")
        return r.text
    
    def forbid_new_games(self):
        r = requests.get(f"{self.admin_base_url}/forbid_new_games")
        return r.text
    
    def allow_new_games(self):
        r = requests.get(f"{self.admin_base_url}/allow_new_games")
        return r.text
    
    def broadcast_message(self, message: str):
        r = requests.get(f"{self.admin_base_url}/broadcast_message/{message}")
        return r.text
    
    def kill_server(self):
        r = requests.get(f"{self.admin_base_url}/kill_server")
        return r.text

    # COMPOSITE APIS
    def initiate_pending_shutdown(self, timeout: int, warning_interval: int):
        """
        Forbids the creation of new games and shuts down the server
        after the specified timeout (in minutes) or when there are no
        active games, whichever comes first. Periodic warnings are
        displayed to active users leading up to the shutdown at the
        specified interval (in minutes).

        This method is blocking and unexpected results may occur if the
        interpreter that ran it is killed preemptively or if multiple
        administrators attempt to run this method during an overlapping
        window. Similarly, other administrators running  APIs such as
        `allow_new_games` or `kill_server` may also interfere.

        If you cancel this method while it is running, it is advisable
        to call the `allow_new_games` method after as this is not done
        automatically.
        """
        self.forbid_new_games()
        time_remaining = timeout * 60
        start_time = time.time()
        while self.num_active_games() != 0 and time_remaining > 0:
            self.broadcast_message(f"An administrator has initiated a pending shutdown of the server. The creation of new games is no longer allowed and all ongoing games have {time_remaining / 60:.1f} minutes remaining before they are forcibly killed.")
            time.sleep(min(time_remaining, warning_interval * 60))
            time_remaining = max(0, timeout * 60 - (time.time() - start_time))
        self.kill_server()

    def kill_all_games(self):
        """
        Kills all games currently running on the server.
        """
        self.broadcast_message("An administrator has forcibly killed all ongoing games.")
        active_rooms = self.list_active_games().keys()
        for room in active_rooms:
            self.kill_game(room)