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

#ucitavanje slike
cam_port = 0
video_capture = cv2.VideoCapture(cam_port)

RED_LOWER1 = np.array([0, 50, 40])
RED_UPPER1 = np.array([12, 255, 255])
RED_LOWER2 = np.array([165, 50, 40])
RED_UPPER2 = np.array([180, 255, 255])
GREEN_LOWER = np.array([25, 30, 30])
GREEN_UPPER = np.array([95, 255, 255])
MIN_PIXELS = 5000

BLUE_LOWER = np.array([100, 150, 50])
BLUE_UPPER = np.array([130, 255, 255])

ORANGE_LOWER = np.array([10, 100, 100])
ORANGE_UPPER = np.array([20, 255, 255])

MAGENTA_LOWER = np.array([140, 100, 100])
MAGENTA_UPPER = np.array([170, 255, 255])  

def detektiraj_magenta_zidove():
    for _ in range(2):  
            video_capture.read()

    ret, frame = video_capture.read()

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, MAGENTA_LOWER, MAGENTA_UPPER)
    konture, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    zidovi = []
    for cnt in konture:
        površina = cv2.contourArea(cnt)
        if površina > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            zidovi.append((x, y, w, h))

    return cv2.countNonZero(mask)
def paralelno_parkiranje(frame):
    zidovi = detektiraj_magenta_zidove(frame)

    if len(zidovi) >= 2:
        zidovi.sort()  # Sortiraj po X (lijevi/desni zid)
        zid1, zid2 = zidovi[0], zidovi[1]
        udaljenost = abs(zid2[0] - zid1[0])
        if 180 <= udaljenost <= 230:
            print("Pronadeni magenta zidovi! Parking detektiran.")
            izvrsi_parkiranje()
            return True
    return False

def izvrsi_parkiranje():
    # malo naprijed
    TXT_M_M1_encodermotor.set_speed(200, TXT_M_M1_encodermotor.CCW)
    TXT_M_M1_encodermotor.start()
    time.sleep(0.2)
    TXT_M_M1_encodermotor.stop()

    # nazad udesno
    TXT_M_S1_servomotor.set_position(100)
    TXT_M_M1_encodermotor.set_speed(150, TXT_M_M1_encodermotor.CW)
    TXT_M_M1_encodermotor.start()
    time.sleep(1.3)
    TXT_M_M1_encodermotor.stop()

    # kotači izravnat i iza
    TXT_M_S1_servomotor.set_position(210)
    TXT_M_M1_encodermotor.start()
    time.sleep(0.6)
    TXT_M_M1_encodermotor.stop()

    # naprijed ulijevo
    TXT_M_S1_servomotor.set_position(280)
    TXT_M_M1_encodermotor.set_speed(150, TXT_M_M1_encodermotor.CCW)
    TXT_M_M1_encodermotor.start()
    time.sleep(1.0)
    TXT_M_M1_encodermotor.stop()

    # kotači izravnat
    TXT_M_S1_servomotor.set_position(210)

def detect_color_ob(frame):
        global orange_flag, blue_flag, brojac
        orange_flag=0
        blue_flag=0

        hsv_region = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        blue=cv2.inRange(hsv_region,BLUE_LOWER, BLUE_UPPER)
        orange=cv2.inRange(hsv_region, ORANGE_LOWER, ORANGE_UPPER)

        if(brojac==0):
            if cv2.countNonZero(orange)>MIN_PIXELS:
                orange_flag=1
                brojac=brojac+1
            if(brojac==0):
                if cv2.countNonZero(blue)>MIN_PIXELS:
                    blue_flag=1
                    brojac=brojac+2 
        else:
            if cv2.countNonZero(orange)>MIN_PIXELS:
                  orange_flag=1
            if cv2.countNonZero(blue)>MIN_PIXELS:
                blue_flag=1
        print('brojac ', brojac)

       
       
        if cv2.countNonZero(orange)>MIN_PIXELS and cv2.countNonZero(orange)>cv2.countNonZero(blue):
             print('orange', cv2.countNonZero(orange))
             return "orange"
        elif cv2.countNonZero(blue)>MIN_PIXELS:
             print('plava ', cv2.countNonZero(blue))
             return "blue"
        #print('unknown')
        return "unknown"

def detect_color_rg(frame):
   
        hsv_region = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        red1 = cv2.inRange(hsv_region, RED_LOWER1, RED_UPPER1)
        red2 = cv2.inRange(hsv_region, RED_LOWER2, RED_UPPER2)
        red = cv2.bitwise_or(red1, red2)
        green = cv2.inRange(hsv_region, GREEN_LOWER, GREEN_UPPER)
        
        
        if cv2.countNonZero(red) > MIN_PIXELS and cv2.countNonZero(red) > cv2.countNonZero(green):

            #print('crvena')
            return "red"
        elif cv2.countNonZero(green) > MIN_PIXELS:
            #print('zelena')
            return "green"
        #print('unknown')
        return "unknown"

def zavoj_boja(frame):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask_orange = cv2.inRange(hsv_frame, ORANGE_LOWER, ORANGE_UPPER)
    mask_blue = cv2.inRange(hsv_frame, BLUE_LOWER, BLUE_UPPER)

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

def centary(color):
    for _ in range(2):  
            video_capture.read()

    ret, frame = video_capture.read()
    height, width, _ = frame.shape
    frame_center_y=height//2
    hsv=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    if(color=='orange'):
         mask=cv2.inRange(hsv, ORANGE_LOWER, ORANGE_UPPER)
    elif(color=='blue'):
         mask=cv2.inRange(hsv, BLUE_LOWER, BLUE_UPPER)
    else:
         print('nepoznata boja')


    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # Uzimamo najveću konturu
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)

        if M["m00"] != 0:
         # x-koordinata centra konture
            cy = int(M["m01"] / M["m00"])  # y-koordinata centra konture

            offset_y=cy-frame_center_y
            print('offset y ', offset_y)
            return offset_y
        
    print("Nema objekta")
    return 0

def centarx(color):
     # Dimenzije slike
    for _ in range(4):  
            video_capture.read()

    ret, frame = video_capture.read()
    height, width, _ = frame.shape
    frame_center_x=width//2
    hsv=cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if(color=='red'):
        red1 = cv2.inRange(hsv, RED_LOWER1, RED_UPPER1)
        red2 = cv2.inRange(hsv, RED_LOWER2, RED_UPPER2)
        mask = cv2.bitwise_or(red1, red2)
    elif(color=='green'):
        mask = cv2.inRange(hsv, GREEN_LOWER, GREEN_UPPER)
    else:
         print('nepoznata boja')
         
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # Uzimamo najveću konturu
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)

        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])  # x-koordinata centra konture
            cy = int(M["m01"] / M["m00"])  # y-koordinata centra konture
            frame_center_x = frame.shape[1] // 2

            offset_x = cx - frame_center_x  # pozitivno: desno, negativno: lijevo
            return offset_x
    print("Nema objekta")
    return 0

def najbliza_boja(frame):
    
    green_h1, red_h1 = visina(frame)
    boja = detect_color_rg(frame)
    if red_h1 > green_h1 and red_h1 > 0 and boja=='red':
        return "red"
    elif green_h1 > 0 and boja=='green':
        return "green"
    else:
        return "unknown"
    

def visina(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(hsv, GREEN_LOWER, GREEN_UPPER)
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
   
    return max_height(green_mask), max_height(red_mask)

def zaobidji_prepreku(counter):
    global  glavna_boja, br, orange_flag, blue_flag, brojac, orange_flag_stari, blue_flag_stari, gl

    print(br)
    if(br==0):
        gl=0
        orange_flag=0
        orange_flag_stari=0
        blue_flag_stari=0
        blue_flag=0
        brojac=0
        br=br+1

    for _ in range(4):  
            video_capture.read()

    ret, frame = video_capture.read()


 
    #hg, hr=visina(frame)

    if(gl==0):
        if(najbliza_boja(frame)=='unknown'):
        
            
            if TXT_M_I3_ultrasonic_distance_meter.get_distance()>TXT_M_I5_ultrasonic_distance_meter.get_distance() and TXT_M_I3_ultrasonic_distance_meter.get_distance()>100 :
                print('skretanje lijevoo zbog senzora')
                glavna_boja= 'blue'
                skreni_lijevo()
                gl=1

            elif TXT_M_I3_ultrasonic_distance_meter.get_distance()<TXT_M_I5_ultrasonic_distance_meter.get_distance() and TXT_M_I5_ultrasonic_distance_meter.get_distance()>100 :
                print('skretanje desnoo zbog senzora')
                glavna_boja='orange'
                skreni_desno()
                gl=2
    if(gl==1):
         if(najbliza_boja(frame)=='unknown'):
            if TXT_M_I3_ultrasonic_distance_meter.get_distance()>TXT_M_I5_ultrasonic_distance_meter.get_distance() and TXT_M_I3_ultrasonic_distance_meter.get_distance()>100 :
                    print('skretanje lijevoo zbog senzora')
                    glavna_boja= 'blue'
                    skreni_lijevo()
    elif(gl==2):
        if(najbliza_boja(frame)=='unknown'):
            if TXT_M_I3_ultrasonic_distance_meter.get_distance()<TXT_M_I5_ultrasonic_distance_meter.get_distance() and TXT_M_I5_ultrasonic_distance_meter.get_distance()>100 :
                    print('skretanje desnoo zbog senzora')
                    glavna_boja='orange'
                    skreni_desno()
            
           
    
    if(najbliza_boja(frame)=='green'  ): #provjeravanje boje prepreke i koliko je blizu
          counter=zelena(counter)
 
    if(najbliza_boja(frame)=='red' ):
       counter=crvena(counter)

    for _ in range(4):  
            video_capture.read()

    ret, frame = video_capture.read()

   
    print('orangle flag ', orange_flag, ' blue flag ', blue_flag)
    print('counter ', counter)
    print('lijevi senzor ', TXT_M_I3_ultrasonic_distance_meter.get_distance(), ' sredina ', TXT_M_I1_ultrasonic_distance_meter.get_distance(), ' desni senzor ', TXT_M_I5_ultrasonic_distance_meter.get_distance())
    return counter

def zelena(counter):
    print('zelena')
    global orange_flag_stari, blue_flag_stari, blue_flag, orange_flag
    if(TXT_M_I1_ultrasonic_distance_meter.get_distance()<30):
        print('skrecem jako u lijevo prvi')
        TXT_M_M1_encodermotor.set_speed(200, TXT_M_M1_encodermotor.CW)
        TXT_M_M1_encodermotor.start()
        time.sleep(1.2)
        TXT_M_M1_encodermotor.set_speed(200, TXT_M_M1_encodermotor.CCW)
        TXT_M_M1_encodermotor.start()
        TXT_M_S1_servomotor.set_position(320)
        time.sleep(1.2)
        TXT_M_S1_servomotor.set_position(120)
        time.sleep(0.9)
    
    pomak=centarx('green')
        
    if(pomak!=0):
       
        while(TXT_M_I1_ultrasonic_distance_meter.get_distance()>40):
            
 
            while(pomak<=2 and pomak!=0 and TXT_M_I1_ultrasonic_distance_meter.get_distance()>30):
                print('skrecem malo u lijevo')
                if(pomak<-30):

                    TXT_M_S1_servomotor.set_position(300)
                    time.sleep(0.2)
                    TXT_M_S1_servomotor.set_position(210)
                    time.sleep(0.1)
                if(pomak<2):
                    TXT_M_S1_servomotor.set_position(250)
                    time.sleep(0.2)
                    TXT_M_S1_servomotor.set_position(210)
                    time.sleep(0.1)
                pomak=centarx('green')
                print(pomak)
        
            while(pomak>=2 and pomak!=0 and TXT_M_I1_ultrasonic_distance_meter.get_distance()>30):
                print('skrecem malo u desno')
                if(pomak>100):
                    TXT_M_S1_servomotor.set_position(100)
                    time.sleep(0.2)
                    TXT_M_S1_servomotor.set_position(210)
                    time.sleep(0.1)
                if(pomak>50):
                    TXT_M_S1_servomotor.set_position(120)
                    time.sleep(0.2)
                    TXT_M_S1_servomotor.set_position(210)
                    time.sleep(0.1)
                pomak=centarx('green')
                print(pomak)
  

    print(TXT_M_I1_ultrasonic_distance_meter.get_distance())  
    if(TXT_M_I1_ultrasonic_distance_meter.get_distance()<30):
        print('skrecem jako u lijevo drugi')
        TXT_M_S1_servomotor.set_position(320)
        time.sleep(1)
        TXT_M_S1_servomotor.set_position(150)
        time.sleep(0.7)

        if glavna_boja=='blue':
        
         TXT_M_S1_servomotor.set_position(290)
         time.sleep(0.4)
        elif glavna_boja=='orange':
            TXT_M_S1_servomotor.set_position(120)
            time.sleep(0.7)
        if(TXT_M_I3_ultrasonic_distance_meter.get_distance()>100):
            TXT_M_S1_servomotor.set_position(290)
            time.sleep(0.4)
        elif(TXT_M_I5_ultrasonic_distance_meter.get_distance()>100):
            TXT_M_S1_servomotor.set_position(120)
            time.sleep(0.7)
             
    
    for _ in range(5):  
            video_capture.read()
           

    ret, frame = video_capture.read()

    '''if(najbliza_boja(frame)=='green'):
         counter=zelena(counter)
    elif(najbliza_boja(frame)=='red'):
         
         counter=crvena(counter)'''
    #print(visina(frame))
    color=detect_color_ob(frame)

    if(brojac==1):
        if(orange_flag==1 and orange_flag_stari==0):
         counter=counter+1
    if(brojac==2):
     if(blue_flag==1 and blue_flag_stari==0):
         counter=counter+1
    
    orange_flag_stari=orange_flag
    blue_flag_stari=blue_flag
    print(counter)
    return counter
          

def crvena(counter):
    global orange_flag_stari, blue_flag_stari, blue_flag, orange_flag
    print('crvena')
    oznaka=0
    if(detektiraj_magenta_zidove()<2000):
        if(TXT_M_I1_ultrasonic_distance_meter.get_distance()<30):
            print('skrecem jako u desno prvi')
            TXT_M_M1_encodermotor.set_speed(200, TXT_M_M1_encodermotor.CW)
            TXT_M_M1_encodermotor.start()
            time.sleep(1.2)
            TXT_M_M1_encodermotor.set_speed(200, TXT_M_M1_encodermotor.CCW)
            TXT_M_M1_encodermotor.start()
            TXT_M_S1_servomotor.set_position(100)
            time.sleep(1.2)
            TXT_M_S1_servomotor.set_position(300)
            time.sleep(0.9)
            oznaka=1
    
        pomak=centarx('red')
        if(pomak!=0 and oznaka==0):
                
                while(TXT_M_I1_ultrasonic_distance_meter.get_distance()>40):
                    
                    while(pomak>=2 and TXT_M_I1_ultrasonic_distance_meter.get_distance()>40 and pomak!=0 ):
                        print('skrecem malo u desno')
                        if(pomak>30):
                            TXT_M_S1_servomotor.set_position(70)
                            time.sleep(0.2)
                            TXT_M_S1_servomotor.set_position(210)
                            time.sleep(0.1)
                        if(pomak>2):
                            TXT_M_S1_servomotor.set_position(120)
                            time.sleep(0.2)
                            TXT_M_S1_servomotor.set_position(210)
                            time.sleep(0.1)
                            
                        pomak=centarx('red')
                        print(pomak)
                    while(pomak<=2  and TXT_M_I1_ultrasonic_distance_meter.get_distance()>40 and pomak!=0 ):
                        print('skrecem malo u lijevo')
                        if(pomak<-30):
                            TXT_M_S1_servomotor.set_position(320)
                            time.sleep(0.2)
                            TXT_M_S1_servomotor.set_position(210)
                            time.sleep(0.1)
                        if(pomak<2):
                            TXT_M_S1_servomotor.set_position(280)
                            time.sleep(0.2)
                            TXT_M_S1_servomotor.set_position(210)
                            time.sleep(0.1)
                            
                        pomak=centarx('red')
                        print(pomak)

        print(TXT_M_I1_ultrasonic_distance_meter.get_distance())  
        if(TXT_M_I1_ultrasonic_distance_meter.get_distance()<45 and oznaka==0):
            print('skrecem jako u desno drugi')
            TXT_M_S1_servomotor.set_position(100)
            time.sleep(1.5)
            TXT_M_S1_servomotor.set_position(320)
            time.sleep(1.5)
            if(glavna_boja=='blue'):
                TXT_M_S1_servomotor.set_position(340)
                time.sleep(0.5)
            elif(glavna_boja=='orange'):
                TXT_M_S1_servomotor.set_position(100)
                time.sleep(0.5)
            if(TXT_M_I3_ultrasonic_distance_meter.get_distance()):
                TXT_M_S1_servomotor.set_position(320)
                time.sleep(0.5)
            elif(TXT_M_I5_ultrasonic_distance_meter.get_distance()):
                TXT_M_S1_servomotor.set_position(100)
                time.sleep(0.5)


    for _ in range(5):  
            video_capture.read()

    ret, frame = video_capture.read()

    '''if(najbliza_boja(frame)=='green'):
         counter=zelena(counter)
    elif(najbliza_boja(frame)=='red'):
         
         counter=crvena(counter)
    #print(visina(frame))'''

    color=detect_color_ob(frame)
    if(brojac==1):
        if(orange_flag==1 and orange_flag_stari==0):
         counter=counter+1
    if(brojac==2):
     if(blue_flag==1 and blue_flag_stari==0):
         counter=counter+1
    
    orange_flag_stari=orange_flag
    blue_flag_stari=blue_flag
    print(counter)
    return counter


def skreni_desno():
    print("Skrecem desno za 90")
    print(TXT_M_I5_ultrasonic_distance_meter.get_distance())

    TXT_M_M1_encodermotor.set_speed(100, TXT_M_M1_encodermotor.CCW)
    TXT_M_S1_servomotor.set_position(50)  # Oštro lijevo
    time.sleep(2)
    TXT_M_S1_servomotor.set_position(210)  # Vrati kotače ravno
    time.sleep(0.3)

    #TXT_M_M1_encodermotor.set_speed(260, TXT_M_M1_encodermotor.CCW)
    while(TXT_M_I5_ultrasonic_distance_meter.get_distance()>100):
        for _ in range(5):  
                video_capture.read()
       

        ret, frame = video_capture.read()
        if(najbliza_boja(frame)=='green' or najbliza_boja(frame)=='red'):
             break
        if(TXT_M_I1_ultrasonic_distance_meter.get_distance()<15):
                if(TXT_M_I1_ultrasonic_distance_meter.get_distance()<25 ):
                 print ('zid')
                 TXT_M_S1_servomotor.set_position(210)
                 time.sleep(0.2)
                 TXT_M_M1_encodermotor.set_speed(200, TXT_M_M1_encodermotor.CW)
                 TXT_M_M1_encodermotor.start()
                 time.sleep(1.5)
                 TXT_M_M1_encodermotor.set_speed(200, TXT_M_M1_encodermotor.CCW)
                 TXT_M_M1_encodermotor.start()
                 TXT_M_S1_servomotor.set_position(100)
                 time.sleep(0.5)
                 zaobidji_prepreku(counter)
             
       

   
    
def skreni_lijevo():
    #time.sleep(0.3)
    print("Skrecem lijevo za 90")
    #print(TXT_M_I3_ultrasonic_distance_meter.get_distance())
        #TXT_M_M1_encodermotor.set_speed(150, TXT_M_M1_encodermotor.CCW)
    TXT_M_S1_servomotor.set_position(340)  # Oštro lijevo
    time.sleep(0.9) 
    TXT_M_S1_servomotor.set_position(210)  # Vrati kotače ravno
    time.sleep(0.1)
    #print(TXT_M_I3_ultrasonic_distance_meter.get_distance())
    while(TXT_M_I3_ultrasonic_distance_meter.get_distance()>100 ):
       
        for _ in range(5):  
                video_capture.read()
            

        ret, frame = video_capture.read()
        if(najbliza_boja(frame)=='green' or najbliza_boja(frame)=='red'):
             break
        if(TXT_M_I1_ultrasonic_distance_meter.get_distance()<15):
            print('zid')
            TXT_M_S1_servomotor.set_position(210)
            time.sleep(0.2) 
            TXT_M_M1_encodermotor.set_speed(200, TXT_M_M1_encodermotor.CW)
            TXT_M_M1_encodermotor.start()
            time.sleep(1.5)
            TXT_M_M1_encodermotor.set_speed(200, TXT_M_M1_encodermotor.CCW)
            TXT_M_M1_encodermotor.start()
            TXT_M_S1_servomotor.set_position(300)
            time.sleep(1)   
            zaobidji_prepreku(counter)
             
        print(TXT_M_I3_ultrasonic_distance_meter.get_distance())
        #time.sleep(0.8)
       #TXT_M_M1_encodermotor.set_speed(260, TXT_M_M1_encodermotor.CCW)
    #print(TXT_M_I3_ultrasonic_distance_meter.get_distance())
    
    


def prati_zid(counter):
    global  glavna_boja, br, orange_flag, blue_flag, brojac, orange_flag_stari, blue_flag_stari, gl
    br=0
    gl=0
    if(br==0):
        gl=0
        orange_flag=0
        orange_flag_stari=0
        blue_flag_stari=0
        blue_flag=0
        brojac=0
        br=br+1
    glavna_boja='unknown'
    TXT_M_S1_servomotor.set_position(210)
    time.sleep(0.2)
    TXT_M_M1_encodermotor.set_speed(160, TXT_M_M1_encodermotor.CCW)
    TXT_M_M1_encodermotor.start()
    for _ in range(5):  
            video_capture.read()
           

    ret, frame = video_capture.read()

    if(najbliza_boja(frame)=='red'):
         counter =crvena(counter)
    elif(najbliza_boja(frame)=='green'):
         counter =zelena(counter)
    TXT_M_S1_servomotor.set_position(210)
    time.sleep(0.2)
    TXT_M_M1_encodermotor.set_speed(220, TXT_M_M1_encodermotor.CCW)
    TXT_M_M1_encodermotor.start()
    print("Robot pokrenut...")
  
    while counter < 12:
        desired_distance=50
        K=1.7#koeficijent proporcionalnosti
                
        counter = zaobidji_prepreku(counter)
        print('glavna boja', glavna_boja)
        
        
        for _ in range(5):  
            video_capture.read()

        ret, frame = video_capture.read()
        boja=najbliza_boja(frame)
        
        if(boja=='unknown'):
            if(gl==0):
                
                    if TXT_M_I3_ultrasonic_distance_meter.get_distance()>TXT_M_I5_ultrasonic_distance_meter.get_distance() and TXT_M_I3_ultrasonic_distance_meter.get_distance()>100:
                            print('skretanje lijevoo zbog senzora')
                            glavna_boja='blue'
                            gl=1
                            skreni_lijevo()

                    elif TXT_M_I3_ultrasonic_distance_meter.get_distance()<TXT_M_I5_ultrasonic_distance_meter.get_distance() and TXT_M_I5_ultrasonic_distance_meter.get_distance()>100 :
                            print('skretanje desnoo zbog senzora')
                            glavna_boja='orange'
                            gl=2
                            skreni_desno()
            if(gl==1):
                
                    if TXT_M_I3_ultrasonic_distance_meter.get_distance()>TXT_M_I5_ultrasonic_distance_meter.get_distance() and TXT_M_I3_ultrasonic_distance_meter.get_distance()>100:
                            print('skretanje lijevoo zbog senzora')
                            glavna_boja='blue'
                            gl=1
                            skreni_lijevo()
            elif(gl==2):
                
                    if TXT_M_I3_ultrasonic_distance_meter.get_distance()<TXT_M_I5_ultrasonic_distance_meter.get_distance() and TXT_M_I5_ultrasonic_distance_meter.get_distance()>100 :
                            print('skretanje desnoo zbog senzora')
                            glavna_boja='orange'
                            gl=2
                            skreni_desno()
            elif (boja=='red'):
                 counter=crvena(counter)
            else:
                 counter=zelena(counter)
                 
             
             
        # Održavanje udaljenosti od zida
        if(glavna_boja=='blue'):

            if(TXT_M_I1_ultrasonic_distance_meter.get_distance()<25 ):
                 print('zid')
                 TXT_M_S1_servomotor.set_position(210)
                 time.sleep(0.2) 
                 TXT_M_M1_encodermotor.set_speed(200, TXT_M_M1_encodermotor.CW)
                 TXT_M_M1_encodermotor.start()
                 time.sleep(1.5)
                 TXT_M_M1_encodermotor.set_speed(200, TXT_M_M1_encodermotor.CCW)
                 TXT_M_M1_encodermotor.start()
                 TXT_M_S1_servomotor.set_position(300)
                 time.sleep(1)   
                 zaobidji_prepreku(counter)
       
        elif(glavna_boja=='orange'):
                if(TXT_M_I1_ultrasonic_distance_meter.get_distance()<25 ):
                 print ('zid')
                 TXT_M_S1_servomotor.set_position(210)
                 time.sleep(0.2)
                 TXT_M_M1_encodermotor.set_speed(200, TXT_M_M1_encodermotor.CW)
                 TXT_M_M1_encodermotor.start()
                 time.sleep(1.5)
                 TXT_M_M1_encodermotor.set_speed(200, TXT_M_M1_encodermotor.CCW)
                 TXT_M_M1_encodermotor.start()
                 TXT_M_S1_servomotor.set_position(100)
                 time.sleep(0.5)
                 zaobidji_prepreku(counter)

             
        error_D=desired_distance-TXT_M_I5_ultrasonic_distance_meter.get_distance()
        error_L=desired_distance-TXT_M_I3_ultrasonic_distance_meter.get_distance()
        if(error_D<0):
             error_D=error_D*(-1)
        if(error_L<0):
             error_L=error_L*(-1)
        if(TXT_M_I5_ultrasonic_distance_meter.get_distance()>TXT_M_I3_ultrasonic_distance_meter.get_distance()):
                     correction = 210 -int(error_L*K)
        else:
                     correction=210+int(error_D*K)
        print('kut zakreta: ', correction)

        TXT_M_S1_servomotor.set_position(correction)
        time.sleep(0.5)

        if(TXT_M_I5_ultrasonic_distance_meter.get_distance()>50 or TXT_M_I3_ultrasonic_distance_meter.get_distance()>50):
            
            TXT_M_S1_servomotor.set_position(210)
            time.sleep(0.1)

        print(TXT_M_I3_ultrasonic_distance_meter.get_distance(), TXT_M_I1_ultrasonic_distance_meter.get_distance(), TXT_M_I5_ultrasonic_distance_meter.get_distance())        
       

            

    time.sleep(1)
    TXT_M_M1_encodermotor.stop()   


# Glavni program
if __name__ == '__main__':
    counter = 0
    # za start s parkinga 
''' for _ in range(4): video_capture.read()
    ret, frame = video_capture.read()
    if ret and paralelno_parkiranje(frame):
        print("start s parkinga")
        TXT_M_M1_encodermotor.set_speed(200, TXT_M_M1_encodermotor.CCW)
        TXT_M_M1_encodermotor.start()
        time.sleep(1.5)
        TXT_M_M1_encodermotor.stop()
'''

    # inače 3 kruga
prati_zid(counter)
print("3 kruga napravio, sad parking")
for _ in range(4): video_capture.read()
ret, frame = video_capture.read()
paralelno_parkiranje(frame)
