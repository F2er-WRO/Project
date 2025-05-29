import fischertechnik.factories as txt_factory

txt_factory.init()
txt_factory.init_input_factory()
txt_factory.init_motor_factory()
txt_factory.init_servomotor_factory()
txt_factory.init_counter_factory()
txt_factory.init_usb_factory()
txt_factory.init_camera_factory()

TXT_M = txt_factory.controller_factory.create_graphical_controller()
TXT_M_I1_ultrasonic_distance_meter = txt_factory.input_factory.create_ultrasonic_distance_meter(TXT_M, 3) #lijevi senzor
TXT_M_I2_ultrasonic_distance_meter = txt_factory.input_factory.create_ultrasonic_distance_meter(TXT_M, 2) #desni senzor
TXT_M_I3_ultrasonic_distance_meter = txt_factory.input_factory.create_ultrasonic_distance_meter(TXT_M, 1) #senzor u sredini
TXT_M_M1_encodermotor = txt_factory.motor_factory.create_encodermotor(TXT_M, 1)
TXT_M_S1_servomotor = txt_factory.servomotor_factory.create_servomotor(TXT_M, 1)
TXT_M_C1_motor_step_counter = txt_factory.counter_factory.create_encodermotor_counter(TXT_M, 1)
TXT_M_C1_motor_step_counter.set_motor(TXT_M_M1_encodermotor)
TXT_M_USB1_1_camera = txt_factory.usb_factory.create_camera(TXT_M, 1)

txt_factory.initialized()