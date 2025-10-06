import cv2
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from picamera2 import Picamera2


class CameraWidget(Image):
    def __init__(self, **kwargs):
        super(CameraWidget, self).__init__(**kwargs)

        # Keep aspect ratio, stretch only if needed
        self.allow_stretch = True
        self.keep_ratio = True

        # Initialize camera
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration()
        self.picam2.configure(config)
        self.picam2.start()

        # Get resolution
        self.cam_width, self.cam_height = config["main"]["size"]

        # Set widget size to correct aspect ratio
        base_height = 600  # Base height for scaling
        self.size_hint = (None, None)  # No size hints
        self.width = (
            self.cam_width / self.cam_height
        ) * base_height  # Calculate width based on aspect ratio
        self.width = 800
        self.height = base_height

        Clock.schedule_interval(self.update, 1.0 / 30)

    def update(self, dt):
        frame = self.picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame, 0)

        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="rgb")
        texture.blit_buffer(frame.tobytes(), colorfmt="rgb", bufferfmt="ubyte")
        self.texture = texture


class CameraApp(App):
    def build(self):
        layout = BoxLayout(orientation="horizontal")

        # Left button area
        left_buttons = BoxLayout(orientation="vertical", size_hint=(None, 1), width=150)
        left_buttons.add_widget(Button(text="Button 1"))
        left_buttons.add_widget(Button(text="Button 2"))

        # Camera in center
        camera = CameraWidget()

        # Right button area
        right_buttons = BoxLayout(
            orientation="vertical", size_hint=(None, 1), width=150
        )
        right_buttons.add_widget(Button(text="Button 3"))
        right_buttons.add_widget(Button(text="Button 4"))

        layout.add_widget(left_buttons)
        layout.add_widget(camera)
        layout.add_widget(right_buttons)

        return layout


if __name__ == "__main__":
    CameraApp().run()
