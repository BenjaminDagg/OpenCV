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
        matches = self.controller.scaled_find_template(template)
        if np.shape(matches)[1] < 1:
            return

        x = matches[1][0] + offset[0]
        y = matches[0][0] + offset[1]

        self.controller.mouse.position = (x,y)
        self.controller.mouse.press(Button.left)
        self.controller.mouse.release(Button.left)

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

    def sp_noise(self,image,prob):
        '''
        Add salt and pepper noise to image
        prob: Probability of the noise
        '''
        output = np.zeros(image.shape,np.uint8)
        thres = 1 - prob 
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                rdn = random.random()
                if rdn < prob:
                    output[i][j] = 0
                elif rdn > thres:
                    output[i][j] = 255
                else:
                    output[i][j] = image[i][j]
        return output

    def matching_symbol_count(self, template):
        time.sleep(5)
        filepath = self.controller.static_templates['symbol10']
        image = np.asarray(self.controller.sct.grab(self.controller.monitor))
        original = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        
        matches = []
        threshold = 0.8

        img = original
        img2 = img.copy()
        template = cv2.imread(filepath,0)
        template = cv2.resize(template, (0,0), fx=0.92, fy=0.92)
        #cv2.imshow("test",template)
        #cv2.waitKey()
        w, h = template.shape[::-1]
        # All the 3 methods for comparison in a list
        methods = ['cv2.TM_CCORR_NORMED']#,'cv.TM_CCORR','cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED'

        img = img2.copy()
        method = eval(methods[0])

        # Apply template Matching
        res = cv2.matchTemplate(original,template,method)
        
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val < threshold:
            return

        print(f"meth={method} , min_val={min_val}, max_val={max_val}, min_loc={min_loc}, max_loc={max_loc}")
        print(len(np.shape(res)))
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc#max_loc

        if top_left not in matches:
            matches.append(top_left)

        self.controller.mouse.position = top_left
        time.sleep(10)

        return len(matches)
