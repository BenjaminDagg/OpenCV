from Controller import Controller
import numpy as np
from pynput.mouse import Button, Controller as MouseController
import pytesseract

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

    def matching_symbol_count(self, template):
        scales = np.arange(0.5,4,0.1)
        matches = self.controller.scaled_find_template(template)
        return np.shape(matches)[1]
