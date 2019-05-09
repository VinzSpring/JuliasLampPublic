import machine, neopixel
import time
import urequests as requests
import ujson as json


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

print("loaded everything")
NUM_LEDS = 52
LED_PIN = machine.Pin(13)

pixels = neopixel.NeoPixel(LED_PIN, NUM_LEDS)
# bot = TelegramBot(bot_token)
#
# lamp = LedGlass(bot, pixels)
# lamp.start()
#
# while True:
#     lamp.update()
#     time.sleep(.1)
# print("bye")


