import cv2
import mss.tools
import numpy as np
from PIL import Image
import time
from pynput.mouse import Button, Controller as MouseController
import pytesseract
from re import sub
from decimal import Decimal

static_templates = {
    'play': 'play602.png',
    'balance': 'balance.png'
}
templates = {k: cv2.imread(v,0) for (k,v) in static_templates.items() }

monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
sct = mss.mss()
frame = None
mouse = MouseController();
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def convert_rgb_to_bgr(img):
    return img[:, :, ::-1]

def take_screenshot():

    i = np.asarray(sct.grab(monitor))
    ig = cv2.cvtColor(i,cv2.COLOR_BGR2GRAY)

    return ig

def refresh_frame():
    global frame 
    frame = take_screenshot()


def match_template(img_grayscale, template, threshold=0.9):
    res = cv2.matchTemplate(img_grayscale,template,cv2.TM_CCOEFF_NORMED)
    matches = np.where(res >= threshold)

    return matches

def find_template(name, image=None,threshold=0.9):

    global frame
    global templates

    if image is None:
        if frame is None:
            refresh_frame()
        image = frame

    return match_template(image,templates['play'],threshold)

def scaled_find_template(name, image=None, threshold=0.8, scales=[0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1,1.0, 0.9, 1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0]):
        global frame
        global templates
        if image is None:
            if frame is None:
                refresh_frame()

            image = frame

        initial_template = templates[name]
        for scale in scales:
            scaled_template = cv2.resize(initial_template, (0,0), fx=scale, fy=scale)
            matches = match_template(
                image,
                scaled_template,
                threshold
            )
            if np.shape(matches)[1] >= 1:
                return matches
        return matches

def click_object(template,offset=(0,0)):
    global frame
    global templates
    global mouse

    matches = scaled_find_template(template,frame)
    if np.shape(matches)[1] < 1:
        return
    x = matches[1][0] + offset[0]
    y = matches[0][0] + offset[1]

    mouse.position = (x,y)
    mouse.press(Button.left)
    mouse.release(Button.left)

def get_balance():
    click_object('balance')
    
    pos = mouse.position
    x = pos[0]
    y = pos[1] + 30
    print('x = {0}'.format(pos[0]))
    print('y = {0}'.format(pos[1]))

    rect = {"top": y, "left": x, "width": 200, "height": 50}
    im = np.asarray(sct.grab(rect))
    text = pytesseract.image_to_string(im)
    
    return text

refresh_frame()
balance_text_before = get_balance()
balance_before = Decimal(sub(r'[^\d.]', '', balance_text_before))
print(balance_before)

refresh_frame()
click_object('play')

balance_text_after = get_balance()
balance_after = Decimal(sub(r'[^\d.]', '', balance_text_after))
print(balance_after)

assert balance_after < balance_before
