# coding: utf-8

# 1. 通过串口搜索 AnanasStepper
# 1. Ues Serial To Search AnanasStepper
from AnanasStepperSDK import AnanasDevice
import logging

logging.basicConfig(level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)s [%(filename)s:%(funcName)s:%(lineno)s]:%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")

myAnanas = AnanasDevice.AnanasManager()

if myAnanas.start_ananas() == True:
    logging.debug("Start AnanasManager Success")
else:
    logging.debug("Start AnanasManager Failed")
    exit(1)

myAnanas.print_info()
# 2. 通过CAN搜索到 全部的设备；（485不提供这种功能）
# 2. Search All AnanasStepper on CAN network

myAnanas.connect_ananas(0) # index 0 of AnanasStepper in Serial 
myAnanas.sertch_can_net_work()
myAnanas.print_info()

# 3. 驱动电机运动
# 3. Drive the motors
point = [1000, 2000, 3000] # steps
# point1= [2000, 3000, 4000] # steps
myAnanas.set_speed(1000)
myAnanas.force_reset_position()
myAnanas.drive_through_can(point)
# myAnanas.drive_through_485(point1)

# 4 关闭电机
# 4 close_ananas the driver
myAnanas.close_ananas()

