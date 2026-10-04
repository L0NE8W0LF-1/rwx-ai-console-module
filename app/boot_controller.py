from typing import Optional
import time


class BootMode:
    IDLE = "idle"
    LOADING = "loading"
    BOOTING = "booting"
    ACTIVE = "active"
    ERROR = "error"
    CANCELLED = "cancelled"


class BootController:
    def __init__(self, progress_callback=None, status_callback=None):
        self.current_mode = BootMode.IDLE
        self.current_image = None
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.is_running = False

    def load_image(self, image_path: str) -> bool:
        self.current_image = image_path
        if self.status_callback:
            self.status_callback(f"Loading image: {image_path}")
        return True

    def start_boot(self) -> bool:
        if not self.current_image:
            if self.status_callback:
                self.status_callback("No image loaded. Load an image first.")
            return False

        self.is_running = True
        self.current_mode = BootMode.BOOTING
        stages = [
            (10, "Initializing bootloader"),
            (25, "Loading recovery image"),
            (50, "Validating image signature"),
            (75, "Preparing boot environment"),
            (90, "Handing off to recovery"),
            (100, "Recovery environment active"),
        ]
        for progress, message in stages:
            if not self.is_running:
                self.current_mode = BootMode.CANCELLED
                if self.status_callback:
                    self.status_callback("Boot cancelled.")
                return False
            if self.progress_callback:
                self.progress_callback(progress)
            if self.status_callback:
                self.status_callback(message)
            time.sleep(0.3)
        self.current_mode = BootMode.ACTIVE
        return True

    def cancel_boot(self):
        self.is_running = False
        self.current_mode = BootMode.CANCELLED
        if self.status_callback:
            self.status_callback("Boot operation cancelled.")

    def get_current_mode(self):
        return self.current_mode
