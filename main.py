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
    "/alice_blue": (240, 248, 255),
    "/antique_white": (250, 235, 215),
    "/aqua": (0, 255, 255),
    "/aqua_marine": (127, 255, 212),
    "/azure": (240, 255, 255),
    "/beige": (245, 245, 220),
    "/bisque": (255, 228, 196),
    "/black": (0, 0, 0),
    "/blanched_almond": (255, 235, 205),
    "/blue": (0, 0, 255),
    "/blue_violet": (138, 43, 226),
    "/brown": (165, 42, 42),
    "/burly_wood": (222, 184, 135),
    "/cadet_blue": (95, 158, 160),
    "/chart_reuse": (127, 255, 0),
    "/chocolate": (210, 105, 30),
    "/coral": (255, 127, 80),
    "/corn_flower_blue": (100, 149, 237),
    "/corn_silk": (255, 248, 220),
    "/crimson": (220, 20, 60),
    "/cyan": (0, 255, 255),
    "/dark_blue": (0, 0, 139),
    "/dark_cyan": (0, 139, 139),
    "/dark_golden_rod": (184, 134, 11),
    "/dark_gray_or_dark_grey": (169, 169, 169),
    "/dark_green": (0, 100, 0),
    "/dark_khaki": (189, 183, 107),
    "/dark_magenta": (139, 0, 139),
    "/dark_olive_green": (85, 107, 47),
    "/dark_orange": (255, 140, 0),
    "/dark_orchid": (153, 50, 204),
    "/dark_red": (139, 0, 0),
    "/dark_salmon": (233, 150, 122),
    "/dark_sea_green": (143, 188, 143),
    "/dark_slate_blue": (72, 61, 139),
    "/dark_slate_gray": (47, 79, 79),
    "/dark_turquoise": (0, 206, 209),
    "/dark_violet": (148, 0, 211),
    "/deep_pink": (255, 20, 147),
    "/deep_sky_blue": (0, 191, 255),
    "/dim_gray_or_dim_grey": (105, 105, 105),
    "/dodger_blue": (30, 144, 255),
    "/firebrick": (178, 34, 34),
    "/floral_white": (255, 250, 240),
    "/forest_green": (34, 139, 34),
    "/gainsboro": (220, 220, 220),
    "/ghost_white": (248, 248, 255),
    "/gold": (255, 215, 0),
    "/golden_rod": (218, 165, 32),
    "/gray_or_grey": (128, 128, 128),
    "/green": (0, 128, 0),
    "/green_yellow": (173, 255, 47),
    "/honeydew": (240, 255, 240),
    "/hot_pink": (255, 105, 180),
    "/indian_red": (205, 92, 92),
    "/indigo": (75, 0, 130),
    "/ivory": (255, 255, 240),
    "/khaki": (240, 230, 140),
    "/lavender": (230, 230, 250),
    "/lavender_blush": (255, 240, 245),
    "/lawn_green": (124, 252, 0),
    "/lemon_chiffon": (255, 250, 205),
    "/light_blue": (173, 216, 230),
    "/light_coral": (240, 128, 128),
    "/light_cyan": (224, 255, 255),
    "/light_golden_rod_yellow": (250, 250, 210),
    "/light_gray_or_light_grey": (211, 211, 211),
    "/light_green": (144, 238, 144),
    "/light_pink": (255, 182, 193),
    "/light_salmon": (255, 160, 122),
    "/light_sea_green": (32, 178, 170),
    "/light_sky_blue": (135, 206, 250),
    "/light_slate_gray": (119, 136, 153),
    "/light_steel_blue": (176, 196, 222),
    "/light_yellow": (255, 255, 224),
    "/lime": (0, 255, 0),
    "/lime_green": (50, 205, 50),
    "/linen": (250, 240, 230),
    "/magenta_or_fuchsia": (255, 0, 255),
    "/maroon": (128, 0, 0),
    "/medium_aqua_marine": (102, 205, 170),
    "/medium_blue": (0, 0, 205),
    "/medium_orchid": (186, 85, 211),
    "/medium_purple": (147, 112, 219),
    "/medium_sea_green": (60, 179, 113),
    "/medium_slate_blue": (123, 104, 238),
    "/medium_spring_green": (0, 250, 154),
    "/medium_turquoise": (72, 209, 204),
    "/medium_violet_red": (199, 21, 133),
    "/midnight_blue": (25, 25, 112),
    "/mint_cream": (245, 255, 250),
    "/misty_rose": (255, 228, 225),
    "/moccasin": (255, 228, 181),
    "/navajo_white": (255, 222, 173),
    "/navy": (0, 0, 128),
    "/old_lace": (253, 245, 230),
    "/olive": (128, 128, 0),
    "/olive_drab": (107, 142, 35),
    "/orange": (255, 165, 0),
    "/orange_red": (255, 69, 0),
    "/orchid": (218, 112, 214),
    "/pale_golden_rod": (238, 232, 170),
    "/pale_green": (152, 251, 152),
    "/pale_turquoise": (175, 238, 238),
    "/pale_violet_red": (219, 112, 147),
    "/papaya_whip": (255, 239, 213),
    "/peach_puff": (255, 218, 185),
    "/peru": (205, 133, 63),
    "/pink": (255, 192, 203),
    "/plum": (221, 160, 221),
    "/powder_blue": (176, 224, 230),
    "/purple": (128, 0, 128),
    "/red": (255, 0, 0),
    "/rosy_brown": (188, 143, 143),
    "/royal_blue": (65, 105, 225),
    "/saddle_brown": (139, 69, 19),
    "/salmon": (250, 128, 114),
    "/sandy_brown": (244, 164, 96),
    "/sea_green": (46, 139, 87),
    "/sea_shell": (255, 245, 238),
    "/sienna": (160, 82, 45),
    "/silver": (192, 192, 192),
    "/sky_blue": (135, 206, 235),
    "/slate_blue": (106, 90, 205),
    "/slate_gray": (112, 128, 144),
    "/snow": (255, 250, 250),
    "/spring_green": (0, 255, 127),
    "/steel_blue": (70, 130, 180),
    "/tan": (210, 180, 140),
    "/teal": (0, 128, 128),
    "/thistle": (216, 191, 216),
    "/tomato": (255, 99, 71),
    "/turquoise": (64, 224, 208),
    "/violet": (238, 130, 238),
    "/wheat": (245, 222, 179),
    "/white": (255, 255, 255),
    "/white_smoke": (245, 245, 245),
    "/yellow": (255, 255, 0),
    "/yellow_green": (154, 205, 50),
}


class LedGlass:
    def __init__(self, bot, leds):
        self.bot = bot
        self.leds = leds
        self.users = [
            "284196744",            
            "313661515"
        ]

        self.last_color = (150, 100, 100)

        self.bot.send(self.users[0], "boot complete")

    def start(self):
        pass

    def update(self):
        self.bot.update(self.on_msg_recv)

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
        elif "/msg" in text:
          text = text.replace("/msg", "")
          for user in reversed(self.users):
            self.bot.send(user, text)
            time.sleep(1)
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

