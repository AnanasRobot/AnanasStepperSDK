# coding: utf-8
import platform
import logging
import time
import copy
import threading

# 根据系统 引用不同的库
if platform.system() == "Windows":
    from serial.tools import list_ports
else:
    import glob
    import os
    import re
    
import traceback

from AnanasStepperSDK.SerialCon import SerialCon
from AnanasStepperSDK import AnanasTools

class AnanasManager:
    
    def __init__(self):
        logging.debug("AnanasManager __init__")
        self.AnanasStepperList = []
        self.AnanasStepperCanList = []
        self.serialdata = ""
        self.mySerialConnected = False
        self.maxReconnctTime = 10
        self.serialcon = None
        self.myComStore = ""
        
        # about serial
        self.serial_conneted = None
        self.serial_get_reply = False
        self.serial_lock = threading.RLock()
        # motion 
        self.motion_speed = 0
    
    def default_config(self):
        logging.basicConfig(level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)s [%(filename)s:%(funcName)s:%(lineno)s]:%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")
        logging.debug("AnanasManager default_config")
        
    def start_ananas(self):
        logging.debug("AnanasManager Start")
        self._find_all_devices()
        
        if len(self.AnanasStepperList) > 0:
            logging.debug("Start Ananas Manager success :" + str(self.AnanasStepperList))
            return True
        else:
            logging.debug("Start Ananas Manager failed")
            return False
        
    def connect_ananas(self, index):
        logging.debug("AnanasManager connect_ananas " + str(index))
        
        if len(self.AnanasStepperList) < index -1:
            return False;
        
        logging.debug("Try to Connect " + self.AnanasStepperList[index])
        self.serial_conneted = SerialCon(self.AnanasStepperList[index])
        self.serial_conneted.on_connected_changed(self._serial_on_charge_targe)
        self.serial_conneted.myserial_data_received_callback(self._serial_receive)
        time.sleep(0.5)
        return True
        
    def close_ananas(self):
        logging.debug("AnanasManager close_ananas ")
        if self.serial_conneted is None:
            return False
        self.serial_conneted.disconnect();
        self.serial_conneted = None
        
    def sertch_can_net_work(self):
        logging.debug("AnanasManager sertch_can_net_work")
        
        
    def print_info(self):
        logging.info("Print Info of AnanasManager Start")
        for ananas in self.AnanasStepperList:
            logging.info("Ananas Serial Device " + str(ananas))
            
        
        logging.info("Print Info of AnanasManager End")
        if self.serial_conneted is not None:
            self._reset_serial_receive()
            self.serial_conneted.write("M0\n")
            self._wait_for_serial_receive(2)
            print("M0 Receice %s \n" %(self.serialdata))
            
            data = copy.deepcopy(self.serialdata)
            self.serialdata = "" # 置空
            return data
        return None
    
    def _find_all_devices(self):
        '''
        线程检测连接设备的状态
        '''
        logging.debug("Try To Find All AnanasStepper")
        self._find_all_serial_devices()
        if self.AnanasStepperList is []:
            self.start_thread_timer(self.find_all_devices, 1)
        
    def _find_all_serial_devices(self):
        '''
        检查串口设备
        '''
        try:
            if platform.system() == "Windows":
                self.temp_serial = []
                for com in list(list_ports.comports()):
                    try:
                        strCom = com[0].encode(
                            "utf-8") 
                    except:
                        strCom = com[0]
                            
                    self.temp_serial.append(strCom)
                
                logging.debug("Find device " + str(self.temp_serial))

            elif platform.system() == "Linux":
                self.temp_serial = []
                self.temp_serial = self.find_usb_tty()
                logging.debug("Find device " + str(self.temp_serial))
            
        except Exception as e:
            logging.error(e)
            traceback.print_exc()    
            
        self._find_all_ananas_steppers()
    
    def _find_all_ananas_steppers(self):
        logging.debug("Try To _find_all_ananas_steppers")
        for comStr in self.temp_serial:
            logging.debug("Try to open " +str(comStr))
            tempCon = SerialCon(comStr)
            tempCon.on_connected_changed(self._serial_on_charge_targe)
            tempCon.myserial_data_received_callback(self._serial_receive)
#                         tempCon.myserial_on_connected_changed(True)
            time.sleep(0.5)
            if tempCon:
                
                logging.debug("Try to connect_ananas serial : " + str(comStr))
                connectTime = 0;
                while self.mySerialConnected == False:
                    logging.debug("wait serial to be connected")
                    connectTime = connectTime + 1
                    if connectTime > self.maxReconnctTime:
                        break
                    time.sleep(0.1)
                    
                if self.mySerialConnected == False:
                    logging.debug("Connect serial : " + str(comStr) + "failed")
                    continue
                    
                logging.debug("Try To send M0")
                self._reset_serial_receive()
                tempCon.write("M0\n")
                self._wait_for_serial_receive(1)
                if self.serialdata.find("End CMD") != -1:
                    logging.debug("Find AnanasStepper")
                    self.serialcon = tempCon
                    self.myComStore = comStr
                    self.AnanasStepperList.append(comStr)
                
                logging.debug("close_ananas the serial " +str(comStr))
                tempCon.disconnect()
                self.serialcon = None
                self.myComStore = ""
                self.serialdata = ""
    
    def _serial_on_charge_targe(self, is_connected):
        if is_connected:
            if self.myComStore and self.serialcon == None:
                logging.debug("reconnet " + str(self.myComStore))
                self.serialcon = SerialCon(self.myComStore)
            logging.debug("Serial Connect");
            self.mySerialConnected = True
        else:
            if self.serialcon:
                logging.debug("disconnet " + str(self.myComStore))
                self.serialcon.disconnect()
                self.serialcon = None
            logging.debug("Serial Close");
            self.mySerialConnected = False
    
    def _wait_for_serial_receive(self, seconds):
        loop_max = seconds/ 0.5
        loop_time = 0
        while self.serial_get_reply == False:
            time.sleep(0.5)
            loop_time += 1
            print("_wait_for_serial_receive time %d state %s"%(loop_time, str(self.serial_get_reply)) )
            if loop_time > loop_max:
                logging.error("_wait_for_serial_receive time out " + str(seconds))
                return False
        return True
    
    def _reset_serial_receive(self):
        self.serial_lock.acquire()
        self.serialdata = ""
        self.serial_get_reply = False
        print("_reset_serial_receive  serial_get_reply " + str(self.serial_get_reply))
        self.serial_lock.release()
        
    def _serial_receive(self, data):
        logging.debug("_serial_receive Get data " + str(data))
        if data:
            self.serial_lock.acquire()
            self.serialdata += data
            logging.debug("now serial data " + str(self.serialdata))
            if self.serialdata.find("Start CMD") != -1 and \
                self.serialdata.find("End CMD") != -1:
                self.serial_get_reply = True
                print("_serial_receive serial_get_reply " + str(self.serial_get_reply))
            self.serial_lock.release()
            
    def set_pulse_mode(self):
        logging.debug("Set AnanasManager Pulse Mode ")
        if self.serial_conneted == None:
            return False        
        self.serial_conneted.write("M1")
        
    def set_current(self, current):
        logging.debug("Set AnanasManager current " + str(current))
        if self.serial_conneted == None:
            return False
        self.serial_conneted.write("M2 B%d\n" %(current))
        
    def set_can_baudrate(self, baudrate):
        logging.debug("Set AnanasManager Can Baudrate " + str(baudrate))
        if self.serial_conneted == None:
            return False
        self.serial_conneted.write("M3 S%d\n" %(baudrate))
        
    def set_485_baudrate(self, baudrate):
        logging.debug("Set AnanasManager 485 Baudrate " + str(baudrate))
        if self.serial_conneted == None:
            return False
        self.serial_conneted.write("M3 B%d\n" %(baudrate))
        
    def set_motion_index(self, index):
        logging.debug("Set AnanasManager Motion Index " + str(index))
        if self.serial_conneted == None:
            return False
        self.serial_conneted.write("M4 S%d\n" %(index))
        
    def set_step_subdevide(self, subdevide):
        logging.debug("Set AnanasManager Subdevide " + str(subdevide))
        if self.serial_conneted == None:
            return False
        self.serial_conneted.write("M5 B%d\n" %(subdevide))
        
    def set_speed(self, speed):
        logging.debug("Set AnanasManager speed " + str(speed))
        self.motion_speed = speed
        
    def drive_through_can(self, point):
        logging.debug("AnanasManager Drive " + str(point))
        if self.serial_conneted == None:
            return False
        for index, value in enumerate(point):
            comamnd = "G1 X%d P%d F%d"%(index, value, self.motion_speed)
            self.serial_conneted.write(comamnd)
    
    def drive_through_485(self, point):
        logging.debug("AnanasManager Drive " + str(point))
        if self.serial_conneted == None:
            return False
        for index, value in enumerate(point):
            comamnd = "G4 X%d P%d F%d\n"%(index, value, self.motion_speed)
            self.serial_conneted.write(comamnd)
        
    def force_reset_position(self):
        logging.debug("Force Reset AnanasManager Point ")
        if self.serial_conneted == None:
            return False
        self.serial_conneted.write("G28\n")
