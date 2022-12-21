import cv2  #image modification
import mss.tools  #screenshots
import numpy as np
from PIL import Image
import time
from pynput.mouse import Button, Controller as MouseController
import pytesseract #image to text https://towardsdatascience.com/read-text-from-image-with-one-line-of-python-code-c22ede074cac
from re import sub
from decimal import Decimal

#guide: https://www.tautvidas.com/blog/2018/02/automating-basic-tasks-in-games-with-opencv-and-python/

#buttons
static_templates = {
    'play': './images/play602.png',
    'balance': './images/balance.png',
    'reconnect' : './images/reconnect.png'
}

#convert button to greyscale
templates = {k: cv2.imread(v,0) for (k,v) in static_templates.items() }
balance_width, balance_height = templates['balance'].shape[::-1]

#represents entire monitor
monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
sct = mss.mss()

#the screenshot of the current screen. Can refresh with refresh_frame()
frame = None

mouse = MouseController();
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


#take screenshot of monitor
def take_screenshot():

    i = np.asarray(sct.grab(monitor))
    ig = cv2.cvtColor(i,cv2.COLOR_BGR2GRAY)

    return ig

#takes new screenshot of monitor and updates frame to new screenshot
def refresh_frame():
    global frame 
    frame = take_screenshot()

#checks if a button image is on the screen
def match_template(img_grayscale, template, threshold=0.8):
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

def scaled_find_template(name, image=None, threshold=0.8, scales=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0]):
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

#clicks a template image on screen
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

#finds coordinates of balance meter then takes a screnshot
# and parses text from the screenshot
def get_balance():
    click_object('balance')
    
    pos = mouse.position
    x = pos[0]
    y = pos[1] + balance_height

    rect = {"top": y, "left": x, "width": 200, "height": 50}
    im = np.asarray(sct.grab(rect))
    text = pytesseract.image_to_string(im)

    return text

'''
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
'''