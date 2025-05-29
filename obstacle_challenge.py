import fischertechnik.factories as txt_factory
from fischertechnik.controller.Motor import Motor
import time
from lib.controller import *
import cv2
import numpy as np


# Inicijalizacija
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


cam_port = 0
video_capture = cv2.VideoCapture(cam_port)

RED_LOWER1 = np.array([0, 70, 50])
RED_UPPER1 = np.array([10, 255, 255])
RED_LOWER2 = np.array([170, 70, 50])
RED_UPPER2 = np.array([180, 255, 255])
GREEN_LOWER = np.array([40, 70, 50])
GREEN_UPPER = np.array([80, 255, 255])
MIN_PIXELS = 550



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
    


def max_height(mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        max_h = 0
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w * h > 1000 and h > max_h:
                max_h = h
        return max_h
  

# Zaobilaženje prepreke na temelju boje i pozicije
def zaobidji_prepreku(frame, boje):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    red_mask1 = cv2.inRange(hsv, RED_LOWER1, RED_UPPER1)
    red_mask2 = cv2.inRange(hsv, RED_LOWER2, RED_UPPER2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)
    green_mask = cv2.inRange(hsv, GREEN_LOWER, GREEN_UPPER)
    
    hr=max_height(red_mask)
    hg=max_height(green_mask)
    print("crvena i zelena visina ", hr, hg)
    boja_blizu = "unknown"
    if hr > hg and hr > 0:
        boja_blizu='red'
    elif hg > 0:
        boja_blizu= "green"
    
    print("Najbliza prepreka:", boja_blizu)   
    

    if(boja_blizu=='green' and max_height(green_mask)>90 ):
        print('zelena, idem lijevo')
        print('lijevi senzor ', TXT_M_I3_ultrasonic_distance_meter.get_distance(), ' sredina ', TXT_M_I1_ultrasonic_distance_meter.get_distance(), ' desni senzor ', TXT_M_I5_ultrasonic_distance_meter.get_distance())
    
        while(TXT_M_I3_ultrasonic_distance_meter.get_distance()>30 ):
            print(max_height(green_mask))
            TXT_M_S1_servomotor.set_position(275)
            time.sleep(1)
            print(TXT_M_I3_ultrasonic_distance_meter.get_distance())
            
            
    if(boja_blizu=='red'  and max_height(red_mask)>90):
        print('crvena, idem desno')
        print('lijevi senzor ', TXT_M_I3_ultrasonic_distance_meter.get_distance(), ' sredina ', TXT_M_I1_ultrasonic_distance_meter.get_distance(), ' desni senzor ', TXT_M_I5_ultrasonic_distance_meter.get_distance())
        while( TXT_M_I5_ultrasonic_distance_meter.get_distance()>25):
            print(max_height(red_mask))
            TXT_M_S1_servomotor.set_position(170)
            time.sleep(1)
            print(TXT_M_I5_ultrasonic_distance_meter.get_distance())
            
    TXT_M_S1_servomotor.set_position(210)
    time.sleep(1)

    
def skreni_desno():
    print("Skrecem desno za 90")
    print(TXT_M_I5_ultrasonic_distance_meter.get_distance())
    TXT_M_S1_servomotor.set_position(50)  # Oštro lijevo
    TXT_M_M1_encodermotor.set_speed(150, TXT_M_M1_encodermotor.CCW)
    #TXT_M_M1_encodermotor.start()
    
    time.sleep(0.5)  # Vozi udesno da se okrene (prilagodi po potrebi)
    
    #TXT_M_M1_encodermotor.stop()
    TXT_M_S1_servomotor.set_position(200)  # Vrati kotače ravno
    time.sleep(0.1)
    while(TXT_M_I5_ultrasonic_distance_meter.get_distance()>70):
       TXT_M_M1_encodermotor.set_speed(200, TXT_M_M1_encodermotor.CCW)
    
def skreni_lijevo():
    print("Skrecem lijevo za 90")
    print(TXT_M_I3_ultrasonic_distance_meter.get_distance())

    TXT_M_M1_encodermotor.set_speed(150, TXT_M_M1_encodermotor.CCW)
    TXT_M_S1_servomotor.set_position(350)  # Oštro lijevo
    #TXT_M_M1_encodermotor.start()
    
    time.sleep(2)  # Vozi udesno da se okrene (prilagodi po potrebi)
    
    #TXT_M_M1_encodermotor.stop()
    TXT_M_S1_servomotor.set_position(200)  # Vrati kotače ravno
    time.sleep(0.2)
    
    while(TXT_M_I3_ultrasonic_distance_meter.get_distance()>50):
       time.sleep(0.5)
       print("ravno ", TXT_M_I3_ultrasonic_distance_meter.get_distance())
    
       TXT_M_M1_encodermotor.set_speed(260, TXT_M_M1_encodermotor.CCW)
    print("zid ", TXT_M_I3_ultrasonic_distance_meter.get_distance())


def prati_zid(counter):
    TXT_M_S1_servomotor.set_position(210)
    time.sleep(0.5)
    TXT_M_M1_encodermotor.set_speed(160, TXT_M_M1_encodermotor.CCW)
    TXT_M_M1_encodermotor.start()
    print("Robot pokrenut...")
   
    while counter < 4:
        ret, frame = video_capture.read()
        if ret:
            
            boje = detect_color(frame)
            #print(boje)
    
            zaobidji_prepreku(frame, boje)
            
            
        else:
            print('greska')

        lijevo=1
        time.sleep(0.1)
        print( "1Lijevi: ", TXT_M_I3_ultrasonic_distance_meter.get_distance(), "1Desni: ", TXT_M_I5_ultrasonic_distance_meter.get_distance())
        #udaljenost=TXT_M_I3_ultrasonic_distance_meter.get_distance()
        '''while(udaljenost<70 ):
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
            if(TXT_M_I5_ultrasonic_distance_meter.get_distance()>70):
                lijevo=0
                break
            if(TXT_M_I3_ultrasonic_distance_meter.get_distance()>70):
                lijevo=1
                skreni_lijevo()
                counter=counter+1
                break
        print( "2Lijevi: ", TXT_M_I3_ultrasonic_distance_meter.get_distance(), "2Desni: ", TXT_M_I5_ultrasonic_distance_meter.get_distance())
        print(lijevo)'''

            # Održavanje udaljenosti od zida
        if(lijevo == 0):


                if TXT_M_I5_ultrasonic_distance_meter.get_distance() > 100 :
                    skreni_desno()
                    counter = counter + 1
                    
                if TXT_M_I5_ultrasonic_distance_meter.get_distance() < 30 and TXT_M_I1_ultrasonic_distance_meter.get_distance()>40:  # Preblizu
                    TXT_M_S1_servomotor.set_position(270)
                    time.sleep(0.3)  # malo lijevo
                elif TXT_M_I5_ultrasonic_distance_meter.get_distance()> 70 and TXT_M_I1_ultrasonic_distance_meter.get_distance()>40:  # Predaleko
                    TXT_M_S1_servomotor.set_position(120) # malo desno
                    time.sleep(0.3)
                else:
                    TXT_M_S1_servomotor.set_position(200)
                    time.sleep(0.3)  # ravno

                
                
                
        if(lijevo==1):
                if TXT_M_I3_ultrasonic_distance_meter.get_distance() > 100:
                    print( "Lijevi: ", TXT_M_I3_ultrasonic_distance_meter.get_distance(), "Desni: ", TXT_M_I5_ultrasonic_distance_meter.get_distance())
                    TXT_M_S1_servomotor.set_position(120)
                    time.sleep(0.3)
                
                    skreni_lijevo()
                    counter = counter + 1
                    
                if TXT_M_I3_ultrasonic_distance_meter.get_distance() <40 and TXT_M_I1_ultrasonic_distance_meter.get_distance()>40:  # Preblizu
                    TXT_M_S1_servomotor.set_position(120)  # malo desno
                    time.sleep(0.3)

                elif TXT_M_I3_ultrasonic_distance_meter.get_distance() > 60 and TXT_M_I1_ultrasonic_distance_meter.get_distance()>40:  # Predaleko
                    TXT_M_S1_servomotor.set_position(250)  # malo lijevo
                    time.sleep(0.3)

                else:
                    TXT_M_S1_servomotor.set_position(200)  # ravno
                    time.sleep(0.3)
                            
                

            

    time.sleep(1)
    TXT_M_M1_encodermotor.stop()   


# Glavni program
if __name__ == '__main__':
    counter = 0
    time.sleep(0.5)
    prati_zid(counter)