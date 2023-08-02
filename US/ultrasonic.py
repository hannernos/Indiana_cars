from gpiozero import DistanceSensor
from time import sleep
ultrasonic = DistanceSensor(echo=17, trigger=4,max_distance=4)
while True:
    print(ultrasonic.distance)
    sleep(0.5)
