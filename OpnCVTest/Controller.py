import cv2  #image modification
import mss.tools  #screenshots
import numpy as np
from PIL import Image
import time
from numpy.core.numeric import tensordot
from pynput.mouse import Button, Controller as MouseController
import pytesseract #image to text https://towardsdatascience.com/read-text-from-image-with-one-line-of-python-code-c22ede074cac
from re import sub
from decimal import Decimal

from OpnCVTest import scaled_find_template

#guide: https://www.tautvidas.com/blog/2018/02/automating-basic-tasks-in-games-with-opencv-and-python/

class Controller:
    
    def __init__(self):
        self.static_templates = {
            'play': './images/play602.png',
            'balance': './images/balance.png',
            'reconnect' : './images/reconnect.png',
            'rules' : './images/rules.png',
            'show_pay' : './images/show_pay_button.png',
            'symbol10' : './images/symbol10.png',
            'symbol10Win' : './images/symbol10Win.png',
            'symbolA' : './images/symbolA.png',
            'symbolAWin' : './images/symbolA-win.png'
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

    def get_coords(self, template, threshold=0.8, scales=[0.8,0.9,1.0,1.1,1.2,1.3]):
        self.refresh_frame()
        coords = []
        s = np.arange(0.8,1.2,0.01)
        
        #image to check for template in
        screen = np.asarray(self.sct.grab(self.monitor))

        #template to search for
        filepath = self.static_templates[template]
        template_img = cv2.imread(filepath,cv2.IMREAD_UNCHANGED)

        #search for template in variety of scales
        for scale in s:
            print(f"testing {scale}")
            #resize the template to the scale
            template_img = cv2.resize(template_img, (0,0), fx=scale, fy=scale)

            #find matches
            matches = cv2.matchTemplate(screen,template_img,cv2.TM_CCORR_NORMED)
            
            #filter matches to only matches that are stronger than threshold
            loc = np.where(matches >= threshold)

            #found a match with good enough threshold
            if np.shape(loc)[1] >= 1:
                print("found results")
                print(f"threshold = {np.shape(loc)[1]}")
                #max_loc stores coord of best matching
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(matches)
                return max_loc
            else:
                return [[0,0]]


    def find_click_object(self, template):
        
        coords = self.get_coords(template)

        if(coords[0] > 0 and coords[1] > 0):

            self.mouse.position = coords
            self.mouse.press(Button.left)
            self.mouse.release(Button.left)

    def is_object_displayed(self,template):
        coords = self.get_coords(template)

        return coords[0] > 0 and coords[1] > 0
        

    #takes new screenshot of monitor and updates frame to new screenshot
    def refresh_frame(self):
        self.frame = self.take_screenshot()

    #checks if a button image is on the screen
    def match_template(self,img_grayscale, template, threshold=0.8):
        res = cv2.matchTemplate(img_grayscale,template,cv2.TM_CCOEFF_NORMED)
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

    def match(self,img_grayscale, template, threshold=0.8):
        res = cv2.matchTemplate(img_grayscale,template,cv2.TM_CCOEFF_NORMED)
        matches = np.where(res >= threshold)

        return matches

    

    