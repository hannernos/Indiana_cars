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
turn=365
def closeDB(signal, frame):
    print("closeDB called")
    mh.getMotor(2).run(Raspi_MotorHAT.RELEASE)
    cur.close()
    db.close()
    timer.cancel()
    timer2.cancel()
    sys.exit(0)

def polling():
    global cur, db, ready
    #print("polling")
    lock.acquire()
    cur.execute("select * from command order by time desc limit 1")
    for (id, time, cmd_string, arg_string, is_finish) in cur:
        if is_finish == 1 : break
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
    # base
    num1 = pressure = sense.get_pressure()
    num2 = sense.get_temperature()
    num3 = sense.get_humidity()
    num4 = 10
    #raw = sense.get_accelerometer_raw()
    
    
    #num1=int(raw["x"]*1000)
    #num2=int(raw["y"]*1000)
    #num3=int(raw["z"]*1000)
    
    meta_string = '0|0|0'
    is_finish = 0

    #print(num1, num2, num3)
    query = "insert into sensing(time, num1, num2, num3,num4, meta_string, is_finish) values (%s, %s, %s, %s, %s,%s, %s)"
    value = (time, num1, num2, num3,num4, meta_string, is_finish)

    lock.acquire()
    cur.execute(query, value)
    db.commit()
    lock.release()

    global timer2
    timer2 = Timer(0.1, sensing)
    timer2.start()

def go():
    myMotor.setSpeed(230)
    myMotor.run(Raspi_MotorHAT.FORWARD)
    
    pass

# gear : 1.8  1:1.8=x:360
def back():
    myMotor.setSpeed(360)
    myMotor.run(Raspi_MotorHAT.BACKWARD)
    pass

def stop():
    myMotor.setSpeed(360)
    myMotor.run(Raspi_MotorHAT.RELEASE)
    pass


def left():
    global turn
    print(turn)
    if(turn-75>=290):
        turn=turn-75
    pwm.setPWM(0, 0, turn)
    pass

def mid():
    global turn
    turn=365
    pwm.setPWM(0, 0, turn)
    pass

def right():
    global turn
    print(turn)
    if(turn+75<=440):
        turn=turn+75
    pwm.setPWM(0, 0, turn+10)
    pass

#init

db = mysql.connector.connect(host='', user='', password='', database='', auth_plugin='mysql_native_password')
cur = db.cursor()
ready = None
timer = None
sense = SenseHat()

mh = Raspi_MotorHAT(addr=0x6f)
myMotor = mh.getMotor(2)
pwm = PWM(0x6F)
pwm.setPWMFreq(60)

sense = SenseHat()
timer2 = None
lock = Lock()

signal.signal(signal.SIGINT, closeDB)
polling()
sensing()

#main
while True:
    sleep(0.1)
    if ready == None : continue

    cmd, arg = ready
    ready = None
    
    print(cmd)

    if cmd == "go" : go()
    if cmd == "back" : back()
    if cmd == "stop" : stop()
    if cmd == "left" : left()
    if cmd == "mid" : mid()
    if cmd == "right" : right()
