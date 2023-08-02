import RPi.GPIO as GPIO 
from time import sleep

servoPin          = 12
SERVO_MAX_DUTY    = 12
SERVO_MIN_DUTY    = 3

GPIO.setmode(GPIO.BOARD)
GPIO.setup(servoPin, GPIO.OUT)

servo = GPIO.PWM(servoPin, 50)
servo.start(0)




def setServoPos(degree):

  if degree > 180:
    degree = 180


  duty = SERVO_MIN_DUTY+(degree*(SERVO_MAX_DUTY-SERVO_MIN_DUTY)/180.0)

  print("Degree: {} to {}(Duty)".format(degree, duty))


  servo.ChangeDutyCycle(duty)





if __name__ == "__main__":
  AREA=[90,120,150,180,30,60]
  TMP=0
  while True:

      setServoPos(AREA[TMP])
      TMP=(TMP+1)%6
      sleep(1/6)


  servo.stop()

  GPIO.cleanup()
