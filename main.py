import machine, neopixel
import time
import urequests as requests
import ujson as json
import sys


class TelegramBot(object):
    def __init__(self, token):
        self.token = token
        self.offset = 0
        self._url = 'https://api.telegram.org/bot' + token

    def _quote(self, t):
        return '%'.join('{:02x}'.format(c) for c in t)

    def send(self, chat_id, text):
        url = self._url + '/sendMessage?chat_id=' + str(chat_id) + \
              '&text=%' + self._quote(text.encode('utf-8'))

        try:
            requests.get(url)
            return True
        except:
            return False

    def get(self):
        url = self._url + '/getUpdates?timeout=30&limit=1&offset=' + \
              str(self.offset)

        try:
            r = requests.get(url)
            jo = json.loads(r.text)
        except:
            return None

        if len(jo['result']) > 0:
            self.offset = jo['result'][0]['update_id'] + 1
            if 'message' in jo['result'][0]:
                msg = jo['result'][0]['message']
                if 'text' in msg:
                    return (msg['chat']['id'],
                            str(msg['from']['first_name']),
                            str(msg['text']),
                            msg['date'])

        return None

    def update(self, handler):
        message = self.get()
        if message:
            handler(message)


def hsv_to_rgb(h, s, v):
    if s == 0.0: v *= 255; return (int(v), int(v), int(v))
    i = int(h * 6.)  # XXX assume int() truncates!
    f = (h * 6.) - i
    p, q, t = int(255 * (v * (1. - s))), int(255 * (v * (1. - s * f))), int(255 * (v * (1. - s * (1. - f))))
    v *= 255
    i %= 6
    if i == 0: return (int(v), int(t), int(p))
    if i == 1: return (int(q), int(v), int(p))
    if i == 2: return (int(p), int(v), int(t))
    if i == 3: return (int(p), int(q), int(v))
    if i == 4: return (int(t), int(p), int(v))
    if i == 5: return (int(v), int(p), int(q))


class Button:
    def __init__(self, gpio, callback):
        self.gpio = gpio
        self.callback = callback
        self.threshold = .5

    def check(self):
        if self.gpio.read() < self.threshold:
            self.callback()

    def calibrate(self):
        temp = []
        for i in range(10):
            temp.append(self.gpio.read())
            time.sleep(.1)
        self.threshold = sum(temp) / 10.0


colors = {
    "alice blue": (240, 248, 255),
    "antique white": (250, 235, 215),
    "aqua": (0, 255, 255),
    "aqua marine": (127, 255, 212),
    "azure": (240, 255, 255),
    "beige": (245, 245, 220),
    "bisque": (255, 228, 196),
    "black": (0, 0, 0),
    "blanched almond": (255, 235, 205),
    "blue": (0, 0, 255),
    "blue violet": (138, 43, 226),
    "brown": (165, 42, 42),
    "burly wood": (222, 184, 135),
    "cadet blue": (95, 158, 160),
    "chart reuse": (127, 255, 0),
    "chocolate": (210, 105, 30),
    "coral": (255, 127, 80),
    "corn flower blue": (100, 149, 237),
    "corn silk": (255, 248, 220),
    "crimson": (220, 20, 60),
    "cyan": (0, 255, 255),
    "dark blue": (0, 0, 139),
    "dark cyan": (0, 139, 139),
    "dark golden rod": (184, 134, 11),
    "dark gray / dark grey": (169, 169, 169),
    "dark green": (0, 100, 0),
    "dark khaki": (189, 183, 107),
    "dark magenta": (139, 0, 139),
    "dark olive green": (85, 107, 47),
    "dark orange": (255, 140, 0),
    "dark orchid": (153, 50, 204),
    "dark red": (139, 0, 0),
    "dark salmon": (233, 150, 122),
    "dark sea green": (143, 188, 143),
    "dark slate blue": (72, 61, 139),
    "dark slate gray": (47, 79, 79),
    "dark turquoise": (0, 206, 209),
    "dark violet": (148, 0, 211),
    "deep pink": (255, 20, 147),
    "deep sky blue": (0, 191, 255),
    "dim gray / dim grey": (105, 105, 105),
    "dodger blue": (30, 144, 255),
    "firebrick": (178, 34, 34),
    "floral white": (255, 250, 240),
    "forest green": (34, 139, 34),
    "gainsboro": (220, 220, 220),
    "ghost white": (248, 248, 255),
    "gold": (255, 215, 0),
    "golden rod": (218, 165, 32),
    "gray / grey": (128, 128, 128),
    "green": (0, 128, 0),
    "green yellow": (173, 255, 47),
    "honeydew": (240, 255, 240),
    "hot pink": (255, 105, 180),
    "indian red": (205, 92, 92),
    "indigo": (75, 0, 130),
    "ivory": (255, 255, 240),
    "khaki": (240, 230, 140),
    "lavender": (230, 230, 250),
    "lavender blush": (255, 240, 245),
    "lawn green": (124, 252, 0),
    "lemon chiffon": (255, 250, 205),
    "light blue": (173, 216, 230),
    "light coral": (240, 128, 128),
    "light cyan": (224, 255, 255),
    "light golden rod yellow": (250, 250, 210),
    "light gray / light grey": (211, 211, 211),
    "light green": (144, 238, 144),
    "light pink": (255, 182, 193),
    "light salmon": (255, 160, 122),
    "light sea green": (32, 178, 170),
    "light sky blue": (135, 206, 250),
    "light slate gray": (119, 136, 153),
    "light steel blue": (176, 196, 222),
    "light yellow": (255, 255, 224),
    "lime": (0, 255, 0),
    "lime green": (50, 205, 50),
    "linen": (250, 240, 230),
    "magenta / fuchsia": (255, 0, 255),
    "maroon": (128, 0, 0),
    "medium aqua marine": (102, 205, 170),
    "medium blue": (0, 0, 205),
    "medium orchid": (186, 85, 211),
    "medium purple": (147, 112, 219),
    "medium sea green": (60, 179, 113),
    "medium slate blue": (123, 104, 238),
    "medium spring green": (0, 250, 154),
    "medium turquoise": (72, 209, 204),
    "medium violet red": (199, 21, 133),
    "midnight blue": (25, 25, 112),
    "mint cream": (245, 255, 250),
    "misty rose": (255, 228, 225),
    "moccasin": (255, 228, 181),
    "navajo white": (255, 222, 173),
    "navy": (0, 0, 128),
    "old lace": (253, 245, 230),
    "olive": (128, 128, 0),
    "olive drab": (107, 142, 35),
    "orange": (255, 165, 0),
    "orange red": (255, 69, 0),
    "orchid": (218, 112, 214),
    "pale golden rod": (238, 232, 170),
    "pale green": (152, 251, 152),
    "pale turquoise": (175, 238, 238),
    "pale violet red": (219, 112, 147),
    "papaya whip": (255, 239, 213),
    "peach puff": (255, 218, 185),
    "peru": (205, 133, 63),
    "pink": (255, 192, 203),
    "plum": (221, 160, 221),
    "powder blue": (176, 224, 230),
    "purple": (128, 0, 128),
    "red": (255, 0, 0),
    "rosy brown": (188, 143, 143),
    "royal blue": (65, 105, 225),
    "saddle brown": (139, 69, 19),
    "salmon": (250, 128, 114),
    "sandy brown": (244, 164, 96),
    "sea green": (46, 139, 87),
    "sea shell": (255, 245, 238),
    "sienna": (160, 82, 45),
    "silver": (192, 192, 192),
    "sky blue": (135, 206, 235),
    "slate blue": (106, 90, 205),
    "slate gray": (112, 128, 144),
    "snow": (255, 250, 250),
    "spring green": (0, 255, 127),
    "steel blue": (70, 130, 180),
    "tan": (210, 180, 140),
    "teal": (0, 128, 128),
    "thistle": (216, 191, 216),
    "tomato": (255, 99, 71),
    "turquoise": (64, 224, 208),
    "violet": (238, 130, 238),
    "wheat": (245, 222, 179),
    "white": (255, 255, 255),
    "white smoke": (245, 245, 245),
    "yellow": (255, 255, 0),
    "yellow green": (154, 205, 50),
}


class LedGlass:
    def __init__(self, bot, leds):
        self.bot = bot
        self.leds = leds
        self.users = [
            "284196744",
            "V1n2",
            "313661515"
        ]

        self.last_color = (150, 100, 100)

        # self.buttons = [
        #    Button(machine.TouchPad(machine.Pin(12)), self.handle_touch)
        # ]

    def start(self):
        # for button in self.buttons:
        #    button.calibrate()
        pass

    def update(self):
        self.bot.update(self.on_msg_recv)
        # for button in self.buttons:
        #    button.check()

    def on_msg_recv(self, msg):
        chat_id, first_name, text, date = msg

        if str(chat_id) not in self.users:
            self.bot.send(chat_id, "unauthorized access!")
            return

        if text == "/on":
            self.turn_on()
            self.bot.send(chat_id, "you turn me on")
        elif text == "/off":
            self.turn_off()
            self.bot.send(chat_id, "turning off...")
        elif text == "/rainbow":
            self.rainbow()
            self.bot.send(chat_id, "gay mode...")
        elif ',' in text:
            rgb = text.split(',')
            try:
                r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
                self.set_color((r, g, b))
                self.bot.send(chat_id, "color set.")
            except Exception:
                self.bot.send(chat_id, "unknown color")
        elif text.lower() in colors.keys():
            self.set_color(colors[text.lower()])
            self.bot.send(chat_id, "color set.")
        else:
            self.bot.send(chat_id, "unknown command!")

    def handle_touch(self):
        print("touchhhh")

    def set_color(self, clr, save_state=True):
        for i in range(self.leds.n):
            self.leds[i] = clr
        self.leds.write()
        if save_state:
            self.last_color = clr

    def turn_on(self):
        self.set_color(self.last_color)

    def turn_off(self):
        self.set_color((0, 0, 0), False)

    def rainbow(self):
        jump = 360.0 / self.leds.n
        for i in range(self.leds.n):
            self.leds[i] = hsv_to_rgb(jump * i, .1, .1)
        self.leds.write()


NUM_LEDS = 52
LED_PIN = machine.Pin(13)

pixels = neopixel.NeoPixel(LED_PIN, NUM_LEDS)
bot = TelegramBot(bot_token)

lamp = LedGlass(bot, pixels)
lamp.start()

while True:
    lamp.update()
    time.sleep(.1)
