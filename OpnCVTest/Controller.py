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

class Controller:
    
    def __init__(self):
        self.static_templates = {
            'play': './images/play602.png',
            'balance': './images/balance.png',
            'reconnect' : './images/reconnect.png',
            'symbol10' : './images/symbol10.png',
            'symbol101' : './images/symbol101.png'
        }
        self.templates = {k: cv2.imread(v,0) for (k,v) in self.static_templates.items() }
        self.frame = None
        #represents entire monitor
        self.monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
        self.mouse = MouseController()
        self.sct = mss.mss()
        pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


    #take screenshot of monitor
    def take_screenshot(self):
        i = np.asarray(self.sct.grab(self.monitor))
        ig = cv2.cvtColor(i,cv2.COLOR_BGR2GRAY)

        return ig

    #takes new screenshot of monitor and updates frame to new screenshot
    def refresh_frame(self):
        self.frame = self.take_screenshot()

    #checks if a button image is on the screen
    def match_template(self,img_grayscale, template, threshold=0.8):
        res = cv2.matchTemplate(img_grayscale,template,cv2.TM_CCOEFF_NORMED,None,mask=template)
        matches = np.where(res >= threshold)

        return matches

    def scaled_find_template(self,name, image=None, threshold=0.8, scales=[0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,4.0]):
        if image is None:
            if self.frame is None:
                self.refresh_frame()

            image = self.frame

        initial_template = self.templates[name]
        for scale in scales:
            scaled_template = cv2.resize(initial_template, (0,0), fx=scale, fy=scale)
            matches = self.match_template(
                image,
                scaled_template,
                threshold
            )
            if np.shape(matches)[1] >= 1:
                print(scale)
                return matches
        return matches

    

    