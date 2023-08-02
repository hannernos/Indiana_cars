from Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor
from Raspi_PWM_Servo_Driver import PWM
import mysql.connector
from threading import Timer, Lock
from time import sleep
import signal
import sys
from sense_hat import SenseHat
from time import sleep
import datetime

import math

#sonic
from gpiozero import DistanceSensor
from time import sleep

#motor
import RPi.GPIO as GPIO



def check_obs():
    global ultrasonic
    res = -1
    dist = ultrasonic.distance
    if dist<1:
        res = 1
    elif dist <2:
        res = 2
    elif dist<3:
        res = 3
    elif dist<=4:
        res = 4
    else: 
        res = -1
    return res

#servo motor
def setServoPos(degree):
    global SERVO_MIN_DUTY, SERVO_MAX_DUTY,SERVO_MIN_DUTY 
    if degree>180:
        degree = 180
    duty = SERVO_MIN_DUTY + (degree * (SERVO_MAX_DUTY - SERVO_MIN_DUTY)/180.0)
    servo.ChangeDutyCycle(duty)




#no use_geometry
def get_distance():
    global sense, pre_pos,tem_pos
    
    tem_pos = sense.get_accelerometer_raw()
    #m->cm, 0.1 sec -> 10 ->v cm/s
    x_tem = tem_pos["x"]*100*10
    y_tem = tem_pos["y"]*100*10
    z_tem = tem_pos["z"]*100*10

    x_pre = pre_pos["x"]*100*10
    y_pre = pre_pos["y"]*100*10
    z_pre = pre_pos["z"]*100*10

    distance = math.sqrt(((x_tem + x_pre)/20)**2+((y_tem + y_pre)/20)**2+(((z_tem + z_pre)/2)*0.1)**2)
    

    pre_pos = sense.get_accelerometer_raw()
    
    print("x:" +str(x_tem)
            )
    print ("y: "+str(y_tem))
    print ("z: "+str(z_tem))

    print("dis : "+str(distance))

def closeDB(signal, frame):
    print("BYE")
    mh.getMotor(2).run(Raspi_MotorHAT.RELEASE)
    cur.close()
    db.close()
    timer.cancel()
    timer2.cancel()
    sys.exit(0)


def polling():
    global cur, db, ready

    lock.acquire()
    cur.execute("select * from command order by time desc limit 1")
    for (id, time, cmd_string, arg_string, is_finish) in cur:
        if is_finish == 1: break
        ready = (cmd_string, arg_string)
        cur.execute("update command set is_finish=1 where is_finish=0")

    db.commit()
    lock.release()

    global timer
    timer = Timer(0.1, polling)
    timer.start()


def sensing():
    global cur, db, sense

    pressure = sense.get_pressure()
    temp = sense.get_temperature()
    humidity = sense.get_humidity()

    time = datetime.datetime.now()
    num1 = round(pressure / 10000, 3)
    num2 = round(temp / 100, 2)
    num3 = round(humidity / 100, 2)
    meta_string = '0|0|0'
    is_finish = 0

    print(num1, num2, num3)
    query = "insert into sensing(time, num1, num2, num3, meta_string, is_finish) values (%s, %s, %s, %s, %s, %s)"
    value = (time, num1, num2, num3, meta_string, is_finish)

    lock.acquire()
    cur.execute(query, value)
    db.commit()
    lock.release()

    global timer2
    timer2 = Timer(1, sensing)
    timer2.start()


def go():
    myMotor.setSpeed(100)
    myMotor.run(Raspi_MotorHAT.FORWARD)


def back():
    myMotor.setSpeed(100)
    myMotor.run(Raspi_MotorHAT.BACKWARD)


def stop():
    myMotor.setSpeed(100)
    myMotor.run(Raspi_MotorHAT.RELEASE)


def left():
    pwm.setPWM(0, 0, 280)


def mid():
    pwm.setPWM(0, 0, 370)


def right():
    pwm.setPWM(0, 0, 440)


# init
db = mysql.connector.connect(host='', user='usr1', password='', database='ss_map',
                             auth_plugin='mysql_native_password')
cur = db.cursor()
ready = None
timer = None

mh = Raspi_MotorHAT(addr=0x6f)
myMotor = mh.getMotor(2)
pwm = PWM(0x6F)
pwm.setPWMFreq(60)

sense = SenseHat()
timer2 = None
lock = Lock()

#servo_motor
servoPin = 12
SERVO_MAX_DUTY = 12
SERVO_MIN_DUTY = 3

GPIO.setmode(GPIO.BOARD)
GPIO.setup(servoPin, GPIO.OUT)

servo = GPIO.PWM(servoPin, 50)
servo.start(0)

#sonic
ultrasonic = DistanceSensor(echo = 17, trigger = 4, max_distance = 4)
degree_para = 90

signal.signal(signal.SIGINT, closeDB)
polling()
sensing()

#clock
time_interval = 0.1

pre_pos = sense.get_accelerometer_raw()
# main thread
sector_x_arr = [90,120,150,180,30,60]
sector_x = 0 
sector_y = 0
while True:
    sleep(time_interval)
    if ready == None: continue

    cmd, arg = ready
    ready = None
   
   #move
    if cmd == "go": go()
    if cmd == "back": back()
    if cmd == "stop": stop()
    if cmd == "left": left()
    if cmd == "mid": mid()
    if cmd == "right": right()

    #servo&sonic
    
    if sector_x > 5:
        sector_x = 0
    
    #motor

    setServoPos(sector_x_arr[sector_x])
    sector_x=sector_x+1


    #sonic
    sector_y = check_obs()
    print("sectorX: "+str(sector_x)+"sectorY: "+str(sector_y))

    #get_distance()
