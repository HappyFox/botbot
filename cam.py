import board
import cv2
from adafruit_servokit import ServoKit
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from picamera2 import Picamera2

Config.set(
    "input", "gamepad0", "joystick,/dev/input/js0,provider=hidinput"
)  # Adjust the path if necessary


JOY_MAX = 32768  # That seems wrong, how many bits is this?
JOY_MIN = -32768
JOY_RANGE = JOY_MAX - JOY_MIN
SERVO_MAX = 180
SERVO_MIN = 0
SERVO_RANGE = SERVO_MAX - SERVO_MIN


def map_joy_to_servo(x):
    return int(SERVO_MIN + ((x - JOY_MIN) / JOY_RANGE) * SERVO_RANGE)


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.servo_kit = ServoKit(channels=16)
        self.servos = self.servo_kit.servo

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

        # Bind joystick events
        Window.bind(on_joy_button_down=self.on_joy_button_down)
        Window.bind(on_joy_axis=self.on_joy_axis)
        Window.bind(on_joy_hat=self.on_joy_hat)

        return layout

    def on_joy_button_down(self, window, stickid, buttonid):
        print(f"Button {buttonid} pressed")
        # Add your logic here to handle button presses

    def on_joy_axis(self, window, stickid, axisid, value):
        if axisid in [0, 1]:
            print(f"mapping from {value} to {map_joy_to_servo(value)}")
            self.servos[axisid].angle = map_joy_to_servo(value)

        # Add your logic here to handle axis movements

    def on_joy_hat(self, window, stickid, hatid, value):
        print(f"Hat: {id}, Value: {value}")


if __name__ == "__main__":
    CameraApp().run()
