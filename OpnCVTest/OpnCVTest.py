import cv2
import mss.tools
import numpy as np
from PIL import Image
import time

static_templates = {
    'play': 'play60.png'
}
templates = {k: cv2.imread(v,0) for (k,v) in static_templates.items() }

frame = None

def convert_rgb_to_bgr(img):
    return img[:, :, ::-1]

def take_screenshot():

    with mss.mss() as sct:
    # Part of the screen to capture
        monitor = {"top": 40, "left": 0, "width": 800, "height": 640}

        while "Screen capturing":
            last_time = time.time()

        # Get raw pixels from the screen, save it to a Numpy array
            img = np.array(sct.grab(monitor))

        # Display the picture
            cv2.imshow("OpenCV/Numpy normal", img)

        # Display the picture in grayscale
        # cv2.imshow('OpenCV/Numpy grayscale',
        #            cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY))

            print(f"fps: {1 / (time.time() - last_time)}")

        # Press "q" to quit
            if cv2.waitKey(25) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
            break

def refresh_frame():
    frame = take_screenshot()

def match_template(img_grayscale, template, threshold=0.9):
    res = cv2.matchTemplate(img_grayscale,template,cv2.TM_CCOEFF_NORMED)
    matches = np.where(res >= threshold)

    return matches

def find_template(name, image=None,threshold=0.9):
    if image is None:
        if frame is None:
            refresh_frame()
        image = frame

    return match_template(image,templates['play'],threshold)

#img_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#img_rgb = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

mon = {"top": 0, "left": 0, "width": 1920, "height": 1080}
sct = mss.mss()
i = np.asarray(sct.grab(mon))
cv2.imshow("Test",i)
cv2.waitKey()

#refresh_frame()
#cv2.imshow("Test",frame)
#cv2.waitKey()
#matches = find_template("play",0.9)