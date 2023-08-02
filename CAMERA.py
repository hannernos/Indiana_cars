import pandas as pd
from sqlalchemy import create_engine
from PIL import Image
import base64
from io import BytesIO
from picamera import PiCamera
import time
from time import sleep
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import ImageFilter


engine = create_engine('mysql+pymysql://(db아이디):7262@(서버IP)/(프로젝트 명)', echo = False)


# open camera

camera = PiCamera()

#set dimensions

camera.resolution=(128, 64)
while True:
  sleep(1)
  camera.capture('image.png')


# write frame to file

  im = Image.open('image.png')

# im.show()
  buffer = BytesIO()
  im.save(buffer, format='png')
  img_str = base64.b64encode(buffer.getvalue())
  #print(img_str) 
  
  # send to MySQL
  img_df = pd.DataFrame({'image_data':[img_str]})
  img_df.to_sql('images', con=engine, if_exists='append', index=False)

