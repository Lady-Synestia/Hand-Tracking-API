import threading
from queue import Queue
from app.utils.Sockets.SocketSend import WebSocketThread


class WebSocketManager:
    _instance = None
    _thread_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._thread_lock:
                if cls._instance is None:  # Double-check locking
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.ws_thread = WebSocketThread()
            self.message_queue = Queue()
            self._initialized = True

    def start(self):
        # start the WebSocket thread
        if not self.ws_thread.thread.is_alive():
            self.ws_thread.start()

    def send_message(self, message: str):
        # send a message to the WebSocket server
        self.ws_thread.send_message(message)

    def stop(self):
        # stop the WebSocket thread
        self.ws_thread.stop()


# its a global singleton
websocket_manager = WebSocketManager()
