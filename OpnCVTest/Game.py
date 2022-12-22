from numpy.matrixlib.defmatrix import mat
from Controller import Controller
import numpy as np
from pynput.mouse import Button, Controller as MouseController
import pytesseract
import cv2
import time
import random
from PIL import Image

from OpnCVTest import scaled_find_template

class Game:

    def __init__(self,controller):
        self.controller = controller
        pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

    def click_object(self, template,offset=(0,0)):
        scales = np.arange(0.8,1.4,0.01)
        matches = self.controller.scaled_find_template(template,scales=scales)
        if np.shape(matches)[1] < 1:
            return

        x = matches[1][0] + offset[0]
        y = matches[0][0] + offset[1]

        self.controller.mouse.position = (x,y)
        self.controller.mouse.press(Button.left)
        self.controller.mouse.release(Button.left)

    def click_rules(self):
        self.controller.find_click_object('play')

    def is_rules_open(self):
        scales = np.arange(0.8,1.4,0.01)
        matches = self.controller.scaled_find_template('show_pay')

        return np.shape(matches)[1] >= 1

    #finds coordinates of balance meter then takes a screnshot
    # and parses text from the screenshot
    def get_balance(self):
        self.click_object('balance')
        
        balance_width, balance_height = self.controller.templates['balance'].shape[::-1]

        pos = self.controller.mouse.position
        x = pos[0]
        y = pos[1] + balance_height

        rect = {"top": y, "left": x, "width": 200, "height": 50}

        im = np.asarray(self.controller.sct.grab(rect))
        text = pytesseract.image_to_string(im)

        return text


    def matching_symbol_count(self, template):
        time.sleep(5)

        threshold = 0.8
        matches = []
        method = cv2.TM_CCORR_NORMED
        sizes = np.arange(0.8,1.2,0.01)

        #screenshot of entire monitor to search for templates in
        screenshot = np.asarray(self.controller.sct.grab(self.controller.monitor))

        #template image of symbol in non-winning state (no animation)
        filepath_orig = self.controller.static_templates['symbolA']
        template_orig = cv2.imread(filepath_orig,cv2.IMREAD_UNCHANGED)
        template_orig = cv2.resize(template_orig, (0,0), fx=0.92, fy=0.92)

        #template of image in winning state with animation
        template_win = cv2.imread(self.controller.static_templates['symbolAWin'],cv2.IMREAD_UNCHANGED)
        #cv2.resize(template_win, (0,0), fx=0.92, fy=0.92)

        h,w,c = template_orig.shape
 
        # Apply template Matching
        result_orig = cv2.matchTemplate(screenshot,template_orig,method)
        for size in sizes:
            template_win = cv2.resize(template_win, (0,0), fx=size, fy=size)
            result_win = cv2.matchTemplate(screenshot,template_win,method)
            np.append(result_orig,result_win)

        #combine results of template match for both symbols
        #np.append(result_orig,result_win)

        #best match for both symbols and the coordinates
        bestMatch = np.where(result_orig == np.max(result_orig))
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result_orig)

        if max_val < threshold:
            print("no matches")
            #return
        loc = np.where(result_orig >= threshold)
        locWin = np.where(result_win >= threshold)
        
        #sotres coordinates of mathing symbols
        resCount = 0
        matchcoords = []

        #add best match to list
        matchcoords.append(max_loc)
        wasFound = False
        cv2.rectangle(screenshot, max_loc, (max_loc[0] + w, max_loc[1] + h), (0,0,255), 2)
        for pt in zip(*loc[::-1]):
            
            #check if coordinate of match is close to an existing coordinate. If it is then dont add it
            for coord in matchcoords:
                if abs(coord[0] - pt[0]) < 200:
                    wasFound = True

            #if match was not close then its unique so add it
            if wasFound == False:
                matchcoords.append(pt)
                cv2.rectangle(screenshot, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
                resCount = resCount + 1

            wasFound = False

        cv2.imwrite('res.png',screenshot)
        #print(f"meth={method} , min_val={min_val}, max_val={max_val}, min_loc={min_loc}, max_loc={max_loc}")


        self.controller.mouse.position = max_loc
        time.sleep(10)

        return len(matchcoords)
