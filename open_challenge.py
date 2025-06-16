import fischertechnik.factories as txt_factory
import time
import fischertechnik.factories as txt_factory
from lib.controller import *
import time
from fischertechnik.controller.Motor import Motor
from lib.controller import *

# initialization 
txt_factory.init()
txt_factory.init_input_factory()
txt_factory.init_motor_factory()
txt_factory.init_counter_factory()
txt_factory.init_servomotor_factory()

TXT_M = txt_factory.controller_factory.create_graphical_controller()
TXT_M_I1_ultrasonic_distance_meter = txt_factory.input_factory.create_ultrasonic_distance_meter(TXT_M, 1)  # middle/front
TXT_M_I5_ultrasonic_distance_meter = txt_factory.input_factory.create_ultrasonic_distance_meter(TXT_M, 5)  # right
TXT_M_I3_ultrasonic_distance_meter = txt_factory.input_factory.create_ultrasonic_distance_meter(TXT_M, 3)  # left
TXT_M_M1_encodermotor = txt_factory.motor_factory.create_encodermotor(TXT_M, 1)
TXT_M_S1_servomotor = txt_factory.servomotor_factory.create_servomotor(TXT_M, 1)
TXT_M_C1_motor_step_counter = txt_factory.counter_factory.create_encodermotor_counter(TXT_M, 1)
TXT_M_C1_motor_step_counter.set_motor(TXT_M_M1_encodermotor)

txt_factory.initialized()

#function for turning right
def turn_right():
   
    print("Right turn for 90")
    print(TXT_M_I5_ultrasonic_distance_meter.get_distance())
    #TXT_M_M1_encodermotor.set_speed(150, TXT_M_M1_encodermotor.CCW)
   
    TXT_M_S1_servomotor.set_position(50)  # sharp left
    time.sleep(2.3)
        
    TXT_M_S1_servomotor.set_position(210)  # wheels in neutral
    time.sleep(0.2)
    
    while(TXT_M_I5_ultrasonic_distance_meter.get_distance()>100):
        print('r')
        time.sleep(0.5)
    time.sleep(1.5)
       
    
def turn_left():
   
    print("Left turn for 90")
    print(TXT_M_I3_ultrasonic_distance_meter.get_distance())
    #TXT_M_M1_encodermotor.set_speed(150, TXT_M_M1_encodermotor.CCW)

    TXT_M_S1_servomotor.set_position(320)  # sharp left
    time.sleep(2.2)
        
    TXT_M_S1_servomotor.set_position(210)  # wheels in neutral
    time.sleep(0.2)
 
    
    while(TXT_M_I3_ultrasonic_distance_meter.get_distance()>100):
       print('r')
       time.sleep(0.5)
    time.sleep(1.5)
   
#function for wall following
def follow_wall(counter):
    TXT_M_S1_servomotor.set_position(210) # wheels in neutral
    time.sleep(0.2)
    TXT_M_M1_encodermotor.set_speed(260, TXT_M_M1_encodermotor.CCW)
    TXT_M_M1_encodermotor.start()
    print("The robot has started...")

    left=5
    time.sleep(0.1)
    global udaljenost
    
    #selecting the inner wall-following side
    while(True):
        TXT_M_S1_servomotor.set_position(210)
        time.sleep(0.1)
        TXT_M_S1_servomotor.set_position(180)
        time.sleep(0.1)
        
        '''if(TXT_M_I3_ultrasonic_distance_meter.get_distance()<10):
            TXT_M_S1_servomotor.set_position(120)
            time.sleep(0.3)
            TXT_M_S1_servomotor.set_position(210)
            time.sleep(0.3)
        if(TXT_M_I5_ultrasonic_distance_meter.get_distance()<10):
            TXT_M_S1_servomotor.set_position(270)
            time.sleep(0.3)
            TXT_M_S1_servomotor.set_position(200)
            time.sleep(0.3)'''
        '''if(TXT_M_I5_ultrasonic_distance_meter.get_distance()<10):
            TXT_M_S1_servomotor.set_position(240)
            time.sleep(0.3)
            TXT_M_S1_servomotor.set_position(210)
            time.sleep(0.1)

        elif(TXT_M_I3_ultrasonic_distance_meter.get_distance()<15):
            TXT_M_S1_servomotor.set_position(180)
            time.sleep(0.3)
            TXT_M_S1_servomotor.set_position(210)
            time.sleep(0.1)'''
    
        
        if(TXT_M_I5_ultrasonic_distance_meter.get_distance()>100):
            left=0
            
            turn_right()
            counter=counter+1
            break
        if(TXT_M_I3_ultrasonic_distance_meter.get_distance()>100):
            left=1
            #udaljenost = TXT_M_I5_ultrasonic_distance_meter.get_distance()
            turn_left()
            counter=counter+1
            break

    while (counter<12): #12 turns for 3 laps
  
        print('left sensor: ', TXT_M_I3_ultrasonic_distance_meter.get_distance(), 'front sensor: ', TXT_M_I1_ultrasonic_distance_meter.get_distance(), ' right sensor: ', TXT_M_I5_ultrasonic_distance_meter.get_distance())

        # maintaining distance from the wall
        if(left == 0): # following the right wall
            if TXT_M_I5_ultrasonic_distance_meter.get_distance() > 200: # corner detection (when there is no wall on the right)
                TXT_M_S1_servomotor.set_position(280)
                time.sleep(0.3)
                turn_right()
                counter = counter + 1
                
            if TXT_M_I5_ultrasonic_distance_meter.get_distance() < 30:  # too close
                TXT_M_S1_servomotor.set_position(250) # a bit to the left
                time.sleep(0.2) 
                TXT_M_S1_servomotor.set_position(210)  # a bit to the left
                time.sleep(0.1)
            elif TXT_M_I5_ultrasonic_distance_meter.get_distance()> 30:  # too far
                TXT_M_S1_servomotor.set_position(130) # a bit to the right
                time.sleep(0.2)
                TXT_M_S1_servomotor.set_position(210)  # a bit to the left
                time.sleep(0.1)
            else:
                TXT_M_S1_servomotor.set_position(210) # straight
                time.sleep(0.1)  
            if(TXT_M_I1_ultrasonic_distance_meter.get_distance()<15):
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

        if(left==1): # following the left wall
            '''if(TXT_M_I3_ultrasonic_distance_meter.get_distance()<100):
             
                   udaljenost = TXT_M_I3_ultrasonic_distance_meter.get_distance()
            '''
            if TXT_M_I3_ultrasonic_distance_meter.get_distance() > 200:
                TXT_M_S1_servomotor.set_position(120)
                time.sleep(0.1)
                turn_left()
                counter = counter + 1
                
            if TXT_M_I3_ultrasonic_distance_meter.get_distance() <30:  # too close
                TXT_M_S1_servomotor.set_position(130)  # a bit to the right
                time.sleep(0.2)
                TXT_M_S1_servomotor.set_position(210)  # a bit to the left
                time.sleep(0.1)

            elif TXT_M_I3_ultrasonic_distance_meter.get_distance() > 30:  # too far
                TXT_M_S1_servomotor.set_position(250)  # a bit to the left
                time.sleep(0.2)
                TXT_M_S1_servomotor.set_position(210)  # a bit to the left
                time.sleep(0.1)

            else:
                TXT_M_S1_servomotor.set_position(210)  # straight
                time.sleep(0.1)
            if(TXT_M_I1_ultrasonic_distance_meter.get_distance()<10):
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
                 

                                 

    time.sleep(1)
    TXT_M_M1_encodermotor.stop()

# main program
if __name__ == '__main__':

 counter = 0
 
 follow_wall(counter)
