import tkinter as tk
from PIL import Image, ImageTk
import os
import math
import time

# Path to the directory containing images
path = os.path.join(os.path.dirname(__file__), "BlackCatimages")

# Original image names and animation configuration
pngs = {
    "up": ["1.png", "2.png"],
    "upright": ["3.png", "4.png"],
    "right": ["5.png", "6.png"],
    "downright": ["7.png", "8.png"],
    "down": ["9.png", "10.png"],
    "downleft": ["11.png", "12.png"],
    "left": ["13.png", "14.png"],
    "upleft": ["15.png", "16.png"],
    "sitting": "25.png",
    "yawning": "26.png",
    "scratching": ["27.png", "28.png"],
    "lickingpaw": "31.png",
    "sleeping": "29.png",
    "sleeping2": "30.png",
    "alert": "32.png",
}

class NekoApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "white")

        self.cat_x, self.cat_y = 100, 100
        self.window_offset = (-20, -30)
        self.mouse_x, self.mouse_y = 0, 0
        self.timer_start = None
        self.state = "active"

        self.images = self.load_images()
        self.current_image_index = 0
        self.image_label = tk.Label(root, bg="white")
        self.image_label.pack()

        # Bind left mouse click to exit the program
        self.image_label.bind("<Button-1>", self.exit_program)

        self.update_position()
        self.animate_cat()
        self.follow_mouse()

    def load_images(self):
        images = {}
        for key, value in pngs.items():
            if isinstance(value, list):
                images[key] = [self.load_image(os.path.join(path, filename)) for filename in value]
            else:
                images[key] = self.load_image(os.path.join(path, value))
        return images

    def load_image(self, filepath):
        image = Image.open(filepath).convert("RGBA")
        return ImageTk.PhotoImage(image)

    def exit_program(self, event):
        self.root.destroy()

    def set_image(self, key):
        if isinstance(self.images[key], list):
            self.current_image_index = (self.current_image_index + 1) % len(self.images[key])
            current_image = self.images[key][self.current_image_index]
        else:
            current_image = self.images[key]

        self.image_label.config(image=current_image)

        width = current_image.width()
        height = current_image.height()

        self.root.geometry(f"{width}x{height}+{self.cat_x + self.window_offset[0]}+{self.cat_y + self.window_offset[1]}")

    def update_position(self):
        self.root.geometry(
            f"+{self.cat_x + self.window_offset[0]}+{self.cat_y + self.window_offset[1]}"
        )

    def start_timer(self):
        if self.timer_start is None:
            self.timer_start = time.time()

    def reset_timer(self):
        self.timer_start = None

    def get_elapsed_time(self):
        if self.timer_start is None:
            return 0
        return time.time() - self.timer_start

    def animate_cat(self):
        if self.state == "active":
            dx, dy = self.mouse_x - self.cat_x, self.mouse_y - self.cat_y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 16:
                angle = math.atan2(-dy, dx)
                animation_key = self.get_movement_animation_key(angle)
                self.set_image(animation_key)
                self.cat_x += int(math.cos(angle) * 16)
                self.cat_y -= int(math.sin(angle) * 16)
                self.update_position()
                self.reset_timer()
            else:
                self.start_timer()
                elapsed = self.get_elapsed_time()
                if elapsed >= 45:
                    self.state = "sleeping"
                    self.sleep_toggle = True
                    self.sleep_last_toggle_time = time.time()
                    self.set_image("sleeping")
                elif 42 <= elapsed < 44:
                    self.set_image("yawning")
                    if elapsed >= 44:
                        self.set_image("yawning")
                elif 30 <= elapsed < 42:
                    self.set_image("lickingpaw")
                    if elapsed >= 35:
                        self.set_image("sitting")
                elif 20 <= elapsed < 30:
                    self.set_image("yawning")
                    if elapsed >= 23:
                        self.set_image("sitting")
                elif 10 <= elapsed < 20:
                    self.set_image("scratching")
                    if elapsed >= 15:
                        self.set_image("sitting")
                else:
                    self.set_image("sitting")
        elif self.state == "sleeping":
            current_time = time.time()
            if current_time - self.sleep_last_toggle_time >= 1:
                self.sleep_toggle = not self.sleep_toggle
                self.sleep_last_toggle_time = current_time
                self.set_image("sleeping2" if self.sleep_toggle else "sleeping")
            if (
                abs(self.mouse_x - self.cat_x) > 50
                or abs(self.mouse_y - self.cat_y) > 50
            ):
                self.state = "alert"
                self.set_image("alert")
                self.root.after(1000, lambda: setattr(self, "state", "active"))
        elif self.state == "alert":
            self.set_image("alert")
            self.root.after(1000, lambda: setattr(self, "state", "active"))

        self.root.after(200, self.animate_cat)

    def get_movement_animation_key(self, angle):
        if -math.pi / 8 <= angle < math.pi / 8:
            return "right"
        elif math.pi / 8 <= angle < 3 * math.pi / 8:
            return "upright"
        elif 3 * math.pi / 8 <= angle < 5 * math.pi / 8:
            return "up"
        elif 5 * math.pi / 8 <= angle < 7 * math.pi / 8:
            return "upleft"
        elif angle >= 7 * math.pi / 8 or angle <= -7 * math.pi / 8:
            return "left"
        elif -7 * math.pi / 8 <= angle < -5 * math.pi / 8:
            return "downleft"
        elif -5 * math.pi / 8 <= angle < -3 * math.pi / 8:
            return "down"
        elif -3 * math.pi / 8 <= angle < -math.pi / 8:
            return "downright"
        return "sitting"

    def follow_mouse(self):
        self.mouse_x, self.mouse_y = self.root.winfo_pointerxy()
        if self.state == "sleeping" and (
            abs(self.mouse_x - self.cat_x) > 50 or abs(self.mouse_y - self.cat_y) > 50
        ):
            self.state = "alert"
            self.set_image("alert")
            self.root.after(1000, lambda: setattr(self, "state", "active"))
        self.root.after(50, self.follow_mouse)

if __name__ == "__main__":
    root = tk.Tk()
    app = NekoApp(root)
    root.mainloop()
