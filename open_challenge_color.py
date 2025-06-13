import fischertechnik.factories as txt_factory
import time
import fischertechnik.factories as txt_factory
from lib.controller import *
import time
from fischertechnik.controller.Motor import Motor
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
TXT_M_I1_ultrasonic_distance_meter = txt_factory.input_factory.create_ultrasonic_distance_meter(TXT_M, 1)  # sredina
TXT_M_I5_ultrasonic_distance_meter = txt_factory.input_factory.create_ultrasonic_distance_meter(TXT_M, 5)  # desno
TXT_M_I3_ultrasonic_distance_meter = txt_factory.input_factory.create_ultrasonic_distance_meter(TXT_M, 3)  # lijevo
TXT_M_M1_encodermotor = txt_factory.motor_factory.create_encodermotor(TXT_M, 1)
TXT_M_S1_servomotor = txt_factory.servomotor_factory.create_servomotor(TXT_M, 1)
TXT_M_C1_motor_step_counter = txt_factory.counter_factory.create_encodermotor_counter(TXT_M, 1)
TXT_M_C1_motor_step_counter.set_motor(TXT_M_M1_encodermotor)

txt_factory.initialized()

cam_port = 0
video_capture = cv2.VideoCapture(cam_port)

orange_lower_hsv = np.array([5, 100, 100])  
orange_upper_hsv = np.array([25, 255, 255])

blue_lower_hsv = np.array([100, 150, 50])  
blue_upper_hsv = np.array([130, 255, 255])


def zavoj_boja(frame):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask_orange = cv2.inRange(hsv_frame, orange_lower_hsv, orange_upper_hsv)
    mask_blue = cv2.inRange(hsv_frame, blue_lower_hsv, blue_upper_hsv)

    # Brojimo piksele u maskama
    blue_pixels = cv2.countNonZero(mask_blue)
    orange_pixels = cv2.countNonZero(mask_orange)
    print('nasao boje')
    print('plavi pikseli ', blue_pixels, 'narancasti pikseli ', orange_pixels)
    # Uporedi broj piksela i vrati boju sa većim brojem piksela
    if orange_pixels > blue_pixels:
        return "orange"
    else:
        return "blue"

# Funkcija za skretanje na uglu
def skreni_desno(udaljenost_prva):
    print("Skrecem desno za 90")
    print(TXT_M_I5_ultrasonic_distance_meter.get_distance())
    TXT_M_S1_servomotor.set_position(50)  # Oštro lijevo
    TXT_M_M1_encodermotor.set_speed(150, TXT_M_M1_encodermotor.CCW)
    #TXT_M_M1_encodermotor.start()
    
    time.sleep(0.5)  # Vozi udesno da se okrene (prilagodi po potrebi)
    
    #TXT_M_M1_encodermotor.stop()
    TXT_M_S1_servomotor.set_position(200)  # Vrati kotače ravno
    time.sleep(0.1)
    while(TXT_M_I5_ultrasonic_distance_meter.get_distance()>udaljenost_prva + 20):
       TXT_M_M1_encodermotor.set_speed(200, TXT_M_M1_encodermotor.CCW)
    
def skreni_lijevo(udaljenost_prva):
    print("Skrecem lijevo za 90")
    print(TXT_M_I3_ultrasonic_distance_meter.get_distance())

    TXT_M_M1_encodermotor.set_speed(150, TXT_M_M1_encodermotor.CCW)

    TXT_M_S1_servomotor.set_position(350)  # Oštro lijevo
    time.sleep(2.5)  

    TXT_M_S1_servomotor.set_position(200)  # Vrati kotače ravno
    time.sleep(0.2)
    
    while(TXT_M_I3_ultrasonic_distance_meter.get_distance()>udaljenost_prva + 20):
       time.sleep(0.5)
       print("idem jos ravno ", TXT_M_I3_ultrasonic_distance_meter.get_distance())
       TXT_M_M1_encodermotor.set_speed(260, TXT_M_M1_encodermotor.CCW)
    
    

# Funkcija za praćenje zida
def prati_zid(counter, boja, udaljenost_prva):
    TXT_M_S1_servomotor.set_position(200)
    time.sleep(0.2)
    TXT_M_M1_encodermotor.set_speed(210, TXT_M_M1_encodermotor.CCW)
    TXT_M_M1_encodermotor.start()
    print("Robot pokrenut...")

    if boja == 'orange':
        lijevo = 1
    else:
        lijevo = 0
    print(lijevo)

    while (counter<12):

        if(lijevo == 0):
            if TXT_M_I5_ultrasonic_distance_meter.get_distance() < udaljenost_prva - 3:  # Preblizu
                TXT_M_S1_servomotor.set_position(250)
                time.sleep(0.1)  # malo lijevo
                print('blago ulijevo: ', TXT_M_I5_ultrasonic_distance_meter.get_distance())
            elif TXT_M_I5_ultrasonic_distance_meter.get_distance() > udaljenost_prva + 20:
                for _ in range(5):
                 video_capture.read()
                ret, frame = video_capture.read()
                if ret:
                    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    mask_blue = cv2.inRange(hsv_frame, blue_lower_hsv, blue_upper_hsv)
                    blue_pixels = cv2.countNonZero(mask_blue)

                if blue_pixels > 15000 and TXT_M_I5_ultrasonic_distance_meter.get_distance() >200:  # Prag ovisno o testiranju
                    print("Zavoj detektiran s bojom, skrecem desno")
                    TXT_M_S1_servomotor.set_position(300)
                    time.sleep(0.3)
                    skreni_desno(udaljenost_prva)
                    if blue_pixels > 15000:
                        counter += 1
                        print('counter je: ', counter)
                else:
                    TXT_M_S1_servomotor.set_position(120)
                    time.sleep(0.1)
                    print('malo jace udesno: ', TXT_M_I5_ultrasonic_distance_meter.get_distance())
                   

            elif TXT_M_I5_ultrasonic_distance_meter.get_distance()> udaljenost_prva + 3:  # Predaleko
                TXT_M_S1_servomotor.set_position(120) # malo desno
                time.sleep(0.1)
            else:
                TXT_M_S1_servomotor.set_position(210)
                time.sleep(0.1)  # ravno
            
        else:
            if TXT_M_I3_ultrasonic_distance_meter.get_distance() < udaljenost_prva - 3:  
                TXT_M_S1_servomotor.set_position(120)  
                time.sleep(0.1)
                print('blago udesno:', TXT_M_I3_ultrasonic_distance_meter.get_distance())

            elif TXT_M_I3_ultrasonic_distance_meter.get_distance() > udaljenost_prva + 20:
              for _ in range(5):
                 video_capture.read()
              ret, frame = video_capture.read()
              if ret:
                hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                mask_orange = cv2.inRange(hsv_frame, orange_lower_hsv, orange_upper_hsv)
                orange_pixels = cv2.countNonZero(mask_orange)

              if orange_pixels > 15000 and TXT_M_I3_ultrasonic_distance_meter.get_distance()>200:  
                  print("Zavoj detektiran s bojom, skrecem lijevo")
                  TXT_M_S1_servomotor.set_position(100)
                  time.sleep(0.3)
                  skreni_lijevo(udaljenost_prva)
                  if orange_pixels > 15000:
                    print('prosao sam boju')
                    counter += 1
                    print('counter je: ' , counter)
              else:
                TXT_M_S1_servomotor.set_position(300)
                time.sleep(0.1)
                print('malo jace ulijevo',  TXT_M_I3_ultrasonic_distance_meter.get_distance())

            elif TXT_M_I3_ultrasonic_distance_meter.get_distance() > udaljenost_prva + 3 :  # Predaleko
                TXT_M_S1_servomotor.set_position(250)  # malo lijevo
                time.sleep(0.1)
                print('blago ulijevo: ', TXT_M_I3_ultrasonic_distance_meter.get_distance())
 
            else:
                TXT_M_S1_servomotor.set_position(210)  # ravno
                time.sleep(0.1)
                
           
    print('zavrsio sam krugove')
    time.sleep(1)
    TXT_M_M1_encodermotor.stop()

# Glavni program
if __name__ == '__main__':

 counter = 0
 time.sleep(0.2)    
 ret, frame = video_capture.read()
 if ret: 
      boja = zavoj_boja(frame)   
      print('boja uspjesno nadena:', boja)   
 else:
    print('greska')


 if boja == 'orange':
    udaljenost_prva = TXT_M_I3_ultrasonic_distance_meter.get_distance()
    print('moja pocetna lijeva udaljenost: ' , udaljenost_prva)
 else:
     udaljenost_prva = TXT_M_I5_ultrasonic_distance_meter.get_distance()
     print('moja pocetna desna udaljenost: ' , udaljenost_prva)

prati_zid(counter, boja, udaljenost_prva)