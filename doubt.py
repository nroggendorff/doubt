import logging
import sys
import threading
from datetime import datetime
from functools import wraps
import requests

class DiscordLogger:
    def __init__(
        self, 
        webhook_url: str,
        app_name: str = "Application",
        level: int = logging.INFO,
        flush_interval: float = 1.0,
        max_message_length: int = 2000
    ):
        self.webhook_url = webhook_url
        self.app_name = app_name

        root = logging.getLogger()
        root.handlers.clear()

        self.handler = self._create_discord_handler(
            webhook_url, 
            app_name,
            flush_interval,
            max_message_length
        )

        self.logger = logging.getLogger()
        self.logger.handlers = [self.handler]
        self.logger.setLevel(level)

        self.progress_tracker = self.ProgressTracker(
            webhook_url,
            app_name=app_name
        )

    def _create_discord_handler(
        self, 
        webhook_url: str,
        app_name: str,
        flush_interval: float,
        max_message_length: int
    ) -> 'DiscordLogger.DiscordHandler':
        handler = self.DiscordHandler(
            webhook_url,
            app_name,
            flush_interval,
            max_message_length
        )
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        return handler

    class DiscordHandler(logging.Handler):
        def __init__(
            self,
            webhook_url: str,
            app_name: str,
            flush_interval: float,
            max_message_length: int
        ):
            super().__init__()
            self.webhook_url = webhook_url
            self.app_name = app_name
            self.flush_interval = flush_interval
            self.max_message_length = max_message_length
            
            self.buffer = []
            self.buffer_lock = threading.Lock()
            self.last_flush = datetime.now()

        def emit(self, record: logging.LogRecord) -> None:
            try:
                msg = self.format(record)
                with self.buffer_lock:
                    self.buffer.append(msg)

                if record.levelno >= logging.WARNING or len(self.buffer) >= 10:
                    self.flush()
                elif (datetime.now() - self.last_flush).total_seconds() >= self.flush_interval:
                    self.flush()
            except Exception:
                self.handleError(record)

        def flush(self) -> None:
            with self.buffer_lock:
                if not self.buffer:
                    return
                    
                message = "\n".join(self.buffer)
                if len(message) > self.max_message_length:
                    message = message[-(self.max_message_length-3):] + "..."

                payload = {
                    "content": f"```\n{message}\n```",
                    "username": self.app_name
                }

                try:
                    requests.post(self.webhook_url, json=payload)
                except Exception as e:
                    print(f"Failed to send to Discord: {e}", file=sys.__stderr__)

                self.buffer.clear()
                self.last_flush = datetime.now()

    class ProgressTracker:
        def __init__(
            self,
            webhook_url: str,
            desc: str = "Progress",
            num_intervals: int = 10,
            app_name: str = "Application"
        ):
            self.webhook_url = webhook_url
            self.desc = desc
            self.num_intervals = num_intervals
            self.last_percentage = None
            self.total = None
            self.current = 0
            self.has_started = False
            self.has_finished = False
            self.tqdm_desc = None
            self.app_name = app_name
            self.last_eta = None

        def write(self, message: str) -> None:
            if not message.strip():
                return

            try:
                if "%" in message and "|" in message:
                    parts = message.split("|")
                    
                    if self.tqdm_desc is None:
                        raw_desc = parts[0].strip()
                        self.tqdm_desc = ' '.join(word for word in raw_desc.split() 
                                                if not any(c.isdigit() for c in word)).rstrip(':')

                    progress_part = parts[2].strip()
                    count_total = progress_part.split()[0]
                    current, total = map(int, count_total.split('/'))

                    eta_part = parts[-1].strip()
                    
                    if self.total is None:
                        self.total = total
                        self.has_started = True
                        self._send_progress(0, eta_part)
                        return

                    self.current = current
                    current_percentage = (self.current * 100) // self.total

                    if (current_percentage >= 0 and 
                        current_percentage <= 100 and 
                        current_percentage % (100 // self.num_intervals) == 0 and 
                        current_percentage != self.last_percentage):
                        self._send_progress(current_percentage, eta_part)
                        self.last_percentage = current_percentage
                else:
                    clean_message = message.strip()
                    if clean_message:
                        payload = {
                            "content": f"```\n{clean_message}\n```",
                            "username": self.app_name
                        }
                        try:
                            requests.post(self.webhook_url, json=payload)
                        except Exception as e:
                            print(f"Failed to send to Discord: {e}", file=sys.__stderr__)

            except Exception:
                pass

        def _send_progress(self, percentage: int, eta: str) -> None:
            desc = self.tqdm_desc or self.desc
            current = (percentage * self.total) // 100 if self.total else 0

            bar_length = 20
            filled = int(bar_length * percentage / 100)
            bar = '=' * filled + '-' * (bar_length - filled)
            
            message = f"{desc}: [{bar}] [{current}/{self.total} | {eta}]"
            
            payload = {
                "content": f"```\n{message}\n```",
                "username": self.app_name
            }
            try:
                requests.post(self.webhook_url, json=payload)
            except Exception as e:
                print(f"Failed to send progress to Discord: {e}", file=sys.__stderr__)

def discord_logging(webhook_url: str, app_name: str = "Application"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            original_stdout = sys.stdout
            original_stderr = sys.stderr
            
            try:
                logger = DiscordLogger(webhook_url, app_name)

                sys.stdout = logger.progress_tracker
                sys.stderr = logger.progress_tracker
                
                result = func(*args, **kwargs)
                return result

            except Exception as e:
                print(f"Error in {func.__name__}: {str(e)}")
                raise
            finally:
                sys.stdout = original_stdout
                sys.stderr = original_stderr
                if 'logger' in locals():
                    logger.handler.flush()
        return wrapper
    return decorator
