# game URL: https://primerlearning.org/CoinFlip/index.html
# Play on a mac screen of 2560 x 1600 resoution.

from PIL import ImageGrab, Image
import pytesseract
import re
import math
import subprocess
import numpy as np
import logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s")
logger = logging.getLogger(__name__)

import time
import threading
from pynput.mouse import Button, Controller

# pynput.keyboard is used to watch events of keyboard for start and stop of mouse
from pynput.keyboard import Listener, KeyCode


file_log_handler = logging.FileHandler(filename = 'PrimerLearning.log')

file_log_handler.setLevel(logging.INFO)
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s")
file_log_handler.setFormatter(log_formatter)
logger.addHandler(file_log_handler)

# four variables are created to control the auto-clicker
delay = 2.3
toss_delay= 3
render_toss_delay = 1.8
button = Button.left # Button.left
start_stop_key = KeyCode(char='s')
stop_key = KeyCode(char='q')

# The coordinates of these web elements are dependent on actual game setup.
heads_img_coords = [594, 732, 654, 777] 
# tails_img_coords = [570, 789, 630, 834]
toss_5_coin_button_coords = [576, 1260, 578, 1262]
score_img_coords = [266, 1210, 374, 1234]

toss_5_coin_button_loc = (338, 630)
fair_coin_button_loc = (170, 710)
biased_coin_button_loc = (338, 710)

# Some probability thresholds for the agent to make decisions on whether it's a fair or biased coin.
# A biased coin has 75% chance of landing on its head.
fair_coin_upper_threshold_1st_round = 0.8
fair_coin_lower_threshold_1st_round = 0.2

fair_coin_upper_threshold = 0.75
fair_coin_lower_threshold = 0.3

def get_result_image(bbox):
    img = ImageGrab.grab(bbox=bbox)
    return img


def extract_num_from_image(img):
    num_raw = pytesseract.image_to_string(img,
                                          lang='eng',
                                          config='--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789')
    num = int(re.search('^\d{1,2}', num_raw).group())

    return num


def calc_fair_coin_prob(num_heads,
                        num_tails,
                        biased_coin_heads=0.75):
    total_coin_toss = num_heads + num_tails
    
    # n_choose_k = math.factorial(total_coin_toss) // math.factorial(num_heads) // math.factorial(num_tails)    
    # Since we're calculating relative probabilities, omitting calculation of n_choose_k
    p_fair = 0.5 ** total_coin_toss
    
    p_biased = (biased_coin_heads ** num_heads) * ((1 - biased_coin_heads) ** num_tails)
    
    p = round(p_fair / (p_fair + p_biased), 2)
    
    return p


def get_coin_flips(total_tosses,
                   time_delay):

    heads_img = get_result_image(bbox=heads_img_coords)

    num_heads = extract_num_from_image(heads_img)

    return num_heads


# threading.Thread is used to control clicks
class ClickMouse(threading.Thread):
    
# delay and button is passed in class to check execution of auto-clicker
    def __init__(self, delay, button):
        super(ClickMouse, self).__init__()
        self.delay = delay
        self.button = button
        self.running = False
        self.program_running = True

    def start_clicking(self):
        self.running = True

    def stop_clicking(self):
        self.running = False

    def exit(self):
        self.stop_clicking()
        self.program_running = False

    def run(self):
        seq = 0
        new_run = True
        while self.program_running:
            while self.running:
                toss_5_coin_button_img = get_result_image(toss_5_coin_button_coords)
                toss_5_coin_button_brightness = np.average(np.array(toss_5_coin_button_img))
                if toss_5_coin_button_brightness < 200:
                    subprocess.call(["say", "Alert!", "Game", "over!"])
                    return

                coin_type = "unknown"

                if new_run:
                    total_toss = 0
                    logger.info(f'Start - Coin #: {seq}')
                    score_img = get_result_image(score_img_coords)
                    score_hash = hash(score_img.tobytes())

                new_run = False
                mouse.move(toss_5_coin_button_loc[0] - mouse.position[0], toss_5_coin_button_loc[1] -  mouse.position[1])
                time.sleep(0.03)
                mouse.click(self.button)
                total_toss += 5
                time.sleep(render_toss_delay) # Wait for UI to respond
                num_heads = get_coin_flips(total_tosses=total_toss,
                                           time_delay=self.delay)

                num_tails = total_toss - num_heads
                p_fair_coin = calc_fair_coin_prob(num_heads=num_heads,
                                                  num_tails=num_tails)

                # Since we gain only 15 points for a correct guess, we shouldn't toss too many times before making a fair/biased coin determination (set at 15 tosses).
                if total_toss <= 15:
                    if (p_fair_coin > fair_coin_upper_threshold and total_toss > 5) or (p_fair_coin > fair_coin_upper_threshold_1st_round and total_toss <= 5):
                        mouse.move(fair_coin_button_loc[0] - mouse.position[0], fair_coin_button_loc[1] - mouse.position[1])
                        time.sleep(0.1)
                        mouse.click(self.button)
                        coin_type = "fair"
                        new_run = True

                    if (p_fair_coin < fair_coin_lower_threshold and total_toss > 5) or (p_fair_coin < fair_coin_lower_threshold_1st_round and total_toss <= 5):
                        mouse.move(biased_coin_button_loc[0] - mouse.position[0], biased_coin_button_loc[1] - mouse.position[1])
                        time.sleep(0.1)
                        mouse.click(self.button)
                        coin_type = "biased"
                        new_run = True

                # If we've flipped the coin fewer than 15 times, w/ a smaller sample size, we should make catious decisions.
                else:
                    if p_fair_coin >= 0.5:
                        mouse.move(fair_coin_button_loc[0] - mouse.position[0], fair_coin_button_loc[1] - mouse.position[1])
                        time.sleep(0.1)
                        mouse.click(self.button)
                        coin_type = "fair"
                        new_run = True
                    
                    else:
                        mouse.move(biased_coin_button_loc[0] - mouse.position[0], biased_coin_button_loc[1] - mouse.position[1])
                        time.sleep(0.1)
                        mouse.click(self.button)
                        coin_type = "biased"
                        new_run = True
                
                if not new_run:
                    logger.info(f'Heads: {num_heads} | Tails: {num_tails} | Fair_coin_prob: {p_fair_coin} | coin_type: {coin_type} | unrevealed')

                time.sleep(render_toss_delay)
                if new_run:
                    seq += 1
                    new_score_img = get_result_image(score_img_coords)
                    new_score_hash = hash(new_score_img.tobytes())
                    if new_score_hash != score_hash:
                        logger.info(f'Heads: {num_heads} | Tails: {num_tails} | Fair_coin_prob: {p_fair_coin} | coin_type: {coin_type} | Right ')
                    else:
                        logger.info(f'Heads: {num_heads} | Tails: {num_tails} | Fair_coin_prob: {p_fair_coin} | coin_type: {coin_type} | Wrong ')



# instance of mouse controller is created
mouse = Controller()
click_thread = ClickMouse(delay, button)
click_thread.start()


def on_press(key):
    # start_stop_key will stop mouse control if running flag is set to true
    if key == start_stop_key:
        if click_thread.running:
            click_thread.stop_clicking()
        else:
            click_thread.start_clicking()
            
    # here exit method is called and when key is pressed it terminates the mouse control
    elif key == stop_key:
        click_thread.exit()
        listener.stop()


with Listener(on_press=on_press) as listener:
    listener.join()
