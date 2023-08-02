import time
import cv2
from time import sleep
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageFilter

import pandas as pd
from sqlalchemy import create_engine

import base64
from io import BytesIO
  


# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 25
SPI_PORT = 0
SPI_DEVICE = 0
# 128x64 display with hardware SPI:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()


def OLED_print():
    global engine
    # Alternatively load a different format image, resize it, and convert to 1 bit color.

    ############ AWS setting ######################
    engine = create_engine('mysql+pymysql://gideok1:7262@52.78.175.68/RCCAR', echo = False)
    ####################################################
    
    img_df = pd.read_sql(sql='select * from images order by image_nm desc limit 1' ,con=engine)
  
    img_str = img_df['image_data'].values[0]
  
    img = base64.decodebytes(img_str)
  
    im = Image.open(BytesIO(img))
    #im.show()

    # Filter
    #filter_list = [ImageFilter.EMBOSS, ImageFilter.EDGE_ENHANCE_MORE]
    #filter_img=image.filter(filter_list[1])
    
    # Clear display
    disp.clear()
    disp.display()
    im.save('./sample2.png', format='PNG')
    image = Image.open('sample2.png').resize((disp.width, disp.height), Image.ANTIALIAS).convert('1')
    print(im)
    print("============")
    print(image)
    # Display image.
    disp.image(image)
    #disp.image(filter_img)
    disp.display()

try:
    while True:
        OLED_print()
        sleep(0.5)
except:
    print("Bye")
    
