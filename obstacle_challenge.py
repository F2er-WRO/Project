import fischertechnik.factories as txt_factory
from fischertechnik.controller.Motor import Motor
import time
from lib.controller import *
import cv2
import numpy as np


# initialization
txt_factory.init()
txt_factory.init_input_factory()
txt_factory.init_motor_factory()
txt_factory.init_counter_factory()
txt_factory.init_servomotor_factory()

TXT_M = txt_factory.controller_factory.create_graphical_controller()
TXT_M_I1_ultrasonic_distance_meter = txt_factory.input_factory.create_ultrasonic_distance_meter(TXT_M, 1)
TXT_M_I5_ultrasonic_distance_meter = txt_factory.input_factory.create_ultrasonic_distance_meter(TXT_M, 5)
TXT_M_I3_ultrasonic_distance_meter = txt_factory.input_factory.create_ultrasonic_distance_meter(TXT_M, 3)
TXT_M_M1_encodermotor = txt_factory.motor_factory.create_encodermotor(TXT_M, 1)
TXT_M_S1_servomotor = txt_factory.servomotor_factory.create_servomotor(TXT_M, 1)
TXT_M_C1_motor_step_counter = txt_factory.counter_factory.create_encodermotor_counter(TXT_M, 1)
TXT_M_C1_motor_step_counter.set_motor(TXT_M_M1_encodermotor)

txt_factory.initialized()

# loading an image
cam_port = 0
video_capture = cv2.VideoCapture(cam_port)

RED_LOWER1 = np.array([0, 70, 50])
RED_UPPER1 = np.array([10, 255, 255])
RED_LOWER2 = np.array([170, 70, 50])
RED_UPPER2 = np.array([180, 255, 255])
GREEN_LOWER = np.array([40, 70, 50])
GREEN_UPPER = np.array([80, 255, 255])
MIN_PIXELS = 1200


# color detection
def detect_color(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    height, width = frame.shape[:2]

    left_width = int(width*0.4)          # 40% of width
    right_width = int(width*0.4)        # 40% of width
    center_width = width - (left_width + right_width)  # 20% of width

    left = frame[:, :left_width]
    center = frame[:, left_width:left_width + center_width]
    right = frame[:, left_width + center_width:]


    def check(region):
        hsv_region = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
        red1 = cv2.inRange(hsv_region, RED_LOWER1, RED_UPPER1)
        red2 = cv2.inRange(hsv_region, RED_LOWER2, RED_UPPER2)
        red = cv2.bitwise_or(red1, red2)
        green = cv2.inRange(hsv_region, GREEN_LOWER, GREEN_UPPER)
        if cv2.countNonZero(red) > MIN_PIXELS and cv2.countNonZero(red) > cv2.countNonZero(green):
            return "red"
        elif cv2.countNonZero(green) > MIN_PIXELS:
            return "green"
        return "unknown"

    return {
        "left": check(left),
        "center": check(center),
        "right": check(right)
    }
    
# identifying the closest color
def close_color(frame):
    
    red_h1 = height_red(frame)
    green_h1 = height_green(frame)
    
    if red_h1 > green_h1 and red_h1 > 0:
        return "red"
    elif green_h1 > 0:
        return "green"
    else:
        return "unknown"
    
def height_red(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    red_mask1 = cv2.inRange(hsv, RED_LOWER1, RED_UPPER1)
    red_mask2 = cv2.inRange(hsv, RED_LOWER2, RED_UPPER2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    def max_height(mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        max_h = 0
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w * h > 1000 and h > max_h:
                max_h = h
        return max_h
   
    return max_height(red_mask)

def height_green(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(hsv, GREEN_LOWER, GREEN_UPPER)

    def max_height(mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        max_h = 0
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w * h > 1000 and h > max_h:
                max_h = h
        return max_h
   
    return max_height(green_mask)

# avoiding obstacles based on color and position
def avoid_obstacle():
    for _ in range(5):  
        video_capture.read()

    ret, frame = video_capture.read()
    boje = detect_color(frame)

    hr=height_red(frame)
    hg=height_green(frame)
    print("red and green height ", hr, hg)
      
    color_near=close_color(frame)
    print("The closest obstacle:", color_near) 

    
    if(color_near=='green' and hg>100 ): # determining obstacle color and how close it is
            org_angle=270
            print('green, going left')
            print('left sensor ', TXT_M_I3_ultrasonic_distance_meter.get_distance(), ' front sensor ', TXT_M_I1_ultrasonic_distance_meter.get_distance(), ' right sensor ', TXT_M_I5_ultrasonic_distance_meter.get_distance())

            while(TXT_M_I3_ultrasonic_distance_meter.get_distance()>25 ):
                print(TXT_M_I1_ultrasonic_distance_meter.get_distance(), TXT_M_I3_ultrasonic_distance_meter.get_distance())
                TXT_M_S1_servomotor.set_position(org_angle)
                time.sleep(0.7)
                while(TXT_M_I1_ultrasonic_distance_meter.get_distance()<35 and TXT_M_I1_ultrasonic_distance_meter.get_distance()>15 and org_angle>=100 ):
                    TXT_M_S1_servomotor.set_position(org_angle-15)
                    time.sleep(0.3)
                    org_angle=org_angle-15
                if(TXT_M_I1_ultrasonic_distance_meter.get_distance()<20):
                    TXT_M_S1_servomotor.set_position(50)
                    time.sleep(1)
                    break
            print('color done') 
 
    if(color_near=='red' and hr>100):
        org_angle=120
        print('red, going right')
        print('left sensor ', TXT_M_I3_ultrasonic_distance_meter.get_distance(), ' front sensor ', TXT_M_I1_ultrasonic_distance_meter.get_distance(), ' right sensor ', TXT_M_I5_ultrasonic_distance_meter.get_distance())
        while( TXT_M_I5_ultrasonic_distance_meter.get_distance()>25 ):
            print(TXT_M_I1_ultrasonic_distance_meter.get_distance(), TXT_M_I5_ultrasonic_distance_meter.get_distance())
            TXT_M_S1_servomotor.set_position(150)
            time.sleep(0.7)  
            while(TXT_M_I1_ultrasonic_distance_meter.get_distance()<35 and TXT_M_I1_ultrasonic_distance_meter.get_distance()>15 and org_angle<=350):
                    TXT_M_S1_servomotor.set_position(org_angle+15)
                    time.sleep(0.3)
                    org_angle=org_angle+15
            if(TXT_M_I1_ultrasonic_distance_meter.get_distance()<20):
                    TXT_M_S1_servomotor.set_position(370)
                    time.sleep(1)
                    break
        print('color done')  

    TXT_M_S1_servomotor.set_position(210)
    time.sleep(0.3)

def turn_right():
    print("Right turn for 90")
    print(TXT_M_I5_ultrasonic_distance_meter.get_distance())
    TXT_M_M1_encodermotor.set_speed(150, TXT_M_M1_encodermotor.CCW)
    TXT_M_S1_servomotor.set_position(50)  # sharp right 
    time.sleep(0.5)

    TXT_M_S1_servomotor.set_position(200)  # wheels in neutral
    time.sleep(0.1)
    while(TXT_M_I5_ultrasonic_distance_meter.get_distance()>100):
       TXT_M_M1_encodermotor.set_speed(200, TXT_M_M1_encodermotor.CCW)
    
def turn_left():
    print("Left turn for 90")
    print(TXT_M_I3_ultrasonic_distance_meter.get_distance())

    TXT_M_M1_encodermotor.set_speed(150, TXT_M_M1_encodermotor.CCW)
    TXT_M_S1_servomotor.set_position(350)  # sharp left
    time.sleep(2) 
    
    TXT_M_S1_servomotor.set_position(200)  # wheels in neutral
    time.sleep(0.2)
    while(TXT_M_I3_ultrasonic_distance_meter.get_distance()>100):
      TXT_M_M1_encodermotor.set_speed(260, TXT_M_M1_encodermotor.CCW)
   

def follow_wall(counter):
    TXT_M_S1_servomotor.set_position(210)
    time.sleep(0.5)
    TXT_M_M1_encodermotor.set_speed(160, TXT_M_M1_encodermotor.CCW)
    TXT_M_M1_encodermotor.start()
    print("The robot has started...")
    br=0
    while counter < 12: # three laps
        if(br%5==0):
            avoid_obstacle()
        br=br+1
        left=5
        time.sleep(0.1)

        while(TXT_M_I3_ultrasonic_distance_meter.get_distance()<200 and TXT_M_I5_ultrasonic_distance_meter.get_distance()<200):
            if(TXT_M_I3_ultrasonic_distance_meter.get_distance()<10):
                TXT_M_S1_servomotor.set_position(120)
                time.sleep(0.1)
                TXT_M_S1_servomotor.set_position(200)
                time.sleep(0.1)
            if(TXT_M_I5_ultrasonic_distance_meter.get_distance()<10):
                TXT_M_S1_servomotor.set_position(270)
                time.sleep(0.1)
                TXT_M_S1_servomotor.set_position(200)
                time.sleep(0.1)
            if(TXT_M_I5_ultrasonic_distance_meter.get_distance()>200):
                left=0
                turn_right()
                counter=counter+1
                break
            if(TXT_M_I3_ultrasonic_distance_meter.get_distance()>200):
                left=1
                turn_left()
                counter=counter+1
                break
        
        # maintaining distance from the wall
        if(left == 0):
            if TXT_M_I5_ultrasonic_distance_meter.get_distance() > 200:
                    TXT_M_S1_servomotor.set_position(300)
                    time.sleep(0.3)
                    turn_right()
                    counter = counter + 1

            if TXT_M_I5_ultrasonic_distance_meter.get_distance() <20 and TXT_M_I5_ultrasonic_distance_meter.get_distance()<TXT_M_I3_ultrasonic_distance_meter.get_distance():  # Preblizu
                    TXT_M_S1_servomotor.set_position(300) 
                    time.sleep(0.5)
                    print('sharp left adjustment')
                    
            elif TXT_M_I5_ultrasonic_distance_meter.get_distance() <50  and TXT_M_I5_ultrasonic_distance_meter.get_distance()<TXT_M_I3_ultrasonic_distance_meter.get_distance():  # Preblizu
                    TXT_M_S1_servomotor.set_position(250)  
                    time.sleep(0.3)
                    print('slight left adjustment')
            if TXT_M_I5_ultrasonic_distance_meter.get_distance() > 70:  # too far
                    TXT_M_S1_servomotor.set_position(90)  
                    time.sleep(0.5)
                    print('sharp right adjustment')

            elif TXT_M_I3_ultrasonic_distance_meter.get_distance() > 50: 
                    TXT_M_S1_servomotor.set_position(140)  
                    time.sleep(0.3)
                    print('slight right adjustment')

            else:
                    TXT_M_S1_servomotor.set_position(210)  
                    time.sleep(0.3)

        if(left==1):
                if TXT_M_I3_ultrasonic_distance_meter.get_distance() > 200:
                    TXT_M_S1_servomotor.set_position(120)
                    time.sleep(0.3)
                    turn_left()
                    counter = counter + 1

                if TXT_M_I3_ultrasonic_distance_meter.get_distance() <20 and TXT_M_I5_ultrasonic_distance_meter.get_distance()>TXT_M_I3_ultrasonic_distance_meter.get_distance():  # Preblizu
                    TXT_M_S1_servomotor.set_position(90)  
                    time.sleep(0.5)
                    print('sharp right adjustment')
                    
                elif TXT_M_I3_ultrasonic_distance_meter.get_distance() <50  and TXT_M_I5_ultrasonic_distance_meter.get_distance()>TXT_M_I3_ultrasonic_distance_meter.get_distance():  # Preblizu
                    TXT_M_S1_servomotor.set_position(140)  
                    time.sleep(0.3)
                    print('slight right adjustment')
                if TXT_M_I3_ultrasonic_distance_meter.get_distance() > 70:  # too far
                    TXT_M_S1_servomotor.set_position(300)  
                    time.sleep(0.5)
                    print('sharp left adjustment')

                elif TXT_M_I3_ultrasonic_distance_meter.get_distance() > 50:
                    TXT_M_S1_servomotor.set_position(250) 
                    time.sleep(0.1)
                    print('slight left adjustment')

                else:
                    TXT_M_S1_servomotor.set_position(200)  
                    time.sleep(0.1)
                            
        print(TXT_M_I3_ultrasonic_distance_meter.get_distance(), TXT_M_I1_ultrasonic_distance_meter.get_distance(), TXT_M_I5_ultrasonic_distance_meter.get_distance())        

    time.sleep(1)
    TXT_M_M1_encodermotor.stop()   


# main program
if __name__ == '__main__':
    counter = 0
    follow_wall(counter)
