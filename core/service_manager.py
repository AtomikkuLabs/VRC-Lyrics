import queue
import config
import logging
import threading
from core import lrc, ChatboxManager, ParamManager


class ServiceManager:
    def __init__(self):
        self.running = None
        self.lrc_thread = None
        self.osc_thread = None
        self.queue = queue.Queue()
        self.lock = threading.Lock()

    def start(self, handlers):
        with self.lock:
            if self.running and self.running.is_set():
                return

            handlers.reset()
            logging.info("Starting Services...")
            handlers.info("Starting App...")
            self.running = threading.Event()
            self.running.set()
            ip = config.get('ip')
            port = config.get('port')

            self.lrc_thread = threading.Thread(target=lambda: self._run_lrc(handlers, self.running), daemon=True)
            self.osc_thread = threading.Thread(target=lambda: self._create_osc_manager(ip, port).run(), daemon=True)

            self.lrc_thread.start()
            self.osc_thread.start()

    def stop(self, handlers):
        with self.lock:
            if not self.running or not self.running.is_set():
                return

            logging.info("Stopping Services...")
            handlers.dismiss()
            handlers.reset()
            self.running.clear()
            self.queue.put(None)

            self.lrc_thread, self.osc_thread = None, None

            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                except queue.Empty:
                    break

    def _run_lrc(self, handlers, running):
        try:
            lrc(self.queue, running, handlers)
        except Exception as e:
            logging.exception(f"Fatal error in LRC: {e}")
            if "Invalid client_id" in str(e):
                handlers.error("Invalid Spotify Client ID")
            else:
                handlers.error(f"Program error occurred: {e}")
        finally:
            if running.is_set():
                handlers.app.toggle_service()

    def _create_osc_manager(self, ip, port):
        if port == 9000:
            logging.info("Using ChatboxManager")
            return ChatboxManager(ip, port, self.queue, self.running)
        else:
            logging.info("Using ParamManager")
            return ParamManager(ip, port, self.queue, self.running)
