import fischertechnik.factories as txt_factory
import time
import fischertechnik.factories as txt_factory
from lib.controller import *
import time
from fischertechnik.controller.Motor import Motor
from lib.controller import *


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

# Funkcija za skretanje na uglu
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
    
    

# Funkcija za praćenje zida
def prati_zid(counter):
    TXT_M_S1_servomotor.set_position(200)
    time.sleep(0.2)
    TXT_M_M1_encodermotor.set_speed(260, TXT_M_M1_encodermotor.CCW)
    TXT_M_M1_encodermotor.start()
    print("Robot pokrenut...")

    lijevo=5
    time.sleep(0.1)
    print( "1Lijevi: ", TXT_M_I3_ultrasonic_distance_meter.get_distance(), "1Desni: ", TXT_M_I5_ultrasonic_distance_meter.get_distance())
    udaljenost=TXT_M_I3_ultrasonic_distance_meter.get_distance()
    while(udaljenost<70 ):
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
    print(lijevo)

    while (counter<13): ##tri puna kruga
        # Održavanje udaljenosti od zida
        if(lijevo == 0):


            if TXT_M_I5_ultrasonic_distance_meter.get_distance() > 50:
                skreni_desno()
                counter = counter + 1
                
            if TXT_M_I5_ultrasonic_distance_meter.get_distance() < 12:  # Preblizu
                TXT_M_S1_servomotor.set_position(270)
                time.sleep(0.1)  # malo lijevo
            elif TXT_M_I5_ultrasonic_distance_meter.get_distance()> 20:  # Predaleko
                TXT_M_S1_servomotor.set_position(120) # malo desno
                time.sleep(0.1)
            else:
                TXT_M_S1_servomotor.set_position(200)
                time.sleep(0.1)  # ravno

            # Detekcija kuta (kad nema zida desno)
            
            
        if(lijevo==1):
                
            if TXT_M_I3_ultrasonic_distance_meter.get_distance() <15:  # Preblizu
                TXT_M_S1_servomotor.set_position(120)  # malo desno
                time.sleep(0.3)

            elif TXT_M_I3_ultrasonic_distance_meter.get_distance() > 20:  # Predaleko
                TXT_M_S1_servomotor.set_position(250)  # malo lijevo
                time.sleep(0.3)

            else:
                TXT_M_S1_servomotor.set_position(200)  # ravno
                time.sleep(0.3)
                        
            if TXT_M_I3_ultrasonic_distance_meter.get_distance() > 50:
                print( "Lijevi: ", TXT_M_I3_ultrasonic_distance_meter.get_distance(), "Desni: ", TXT_M_I5_ultrasonic_distance_meter.get_distance())
                TXT_M_S1_servomotor.set_position(120)
                time.sleep(0.3)
                skreni_lijevo()
                counter = counter + 1

           

    time.sleep(1)
    TXT_M_M1_encodermotor.stop()

# Glavni program
if __name__ == '__main__':

 counter = 0
 print("prvi" , TXT_M_I3_ultrasonic_distance_meter.get_distance(), TXT_M_I5_ultrasonic_distance_meter.get_distance())

    
 prati_zid(counter)
