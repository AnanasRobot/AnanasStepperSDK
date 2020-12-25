# -*- coding=utf-8 -*-
'''
Created on 2019年7月15日

@author: Dark
'''
from AnanasStepperSDK import SerialHelper
import logging


class SerialCon(object):
    '''
    Serial Connect 
    Hanlder with Ananas Serial Interface with SerialHelper
    '''
    
    def __init__(self, Port="COM5"):
        
        self.com = Port
        self.myserial = SerialHelper.SerialHelper(Port=self.com, BaudRate="115200")
        
        self.change_target_callback = None
        self.serial_receive_data_callback = None
        
        print("Open Com %s at"%(self.com) + str(self.myserial))
        
    def on_connected_changed(self, change_target_callback):
        
        self.change_target_callback = change_target_callback
        
        self.myserial.on_connected_changed(self.myserial_on_connected_changed)
        
    def write(self, data):
        self.myserial.write(data, False);

    def myserial_on_connected_changed(self, is_connected):
        if is_connected:
            logging.debug("myserial_on_connected_changed Connected")
            self.myserial.connect()
            self.myserial.on_data_received(self.myserial_on_data_received)
        else:
            logging.debug("myserial_on_connected_changed DisConnected")
        try:
            if self.change_target_callback:
                logging.debug("charge target callback is registed call it now")
                self.change_target_callback(is_connected)
        except Exception as e:
            logging.error("error " +str(e))
    
    def myserial_data_received_callback(self,receive_callback):
        if receive_callback:
            logging.debug("register data receive callback")
            self.serial_receive_data_callback = receive_callback
        
    def myserial_on_data_received(self, data):
        
        print(data)
        # call back function may have exception
        try:
            if self.serial_receive_data_callback:
                self.serial_receive_data_callback(data)
        except Exception as e:
            logging.error("error " + str(e))
        
    def disconnect(self):
        if self.myserial:
            self.myserial.disconnect()


if __name__ == '__main__':
    import time
    
    def seiarl_change(is_connect):
        print("connect state is " + str(is_connect))
    
    con = SerialCon("COM5")
    print(str(con))
    if con:
        con.on_connected_changed(seiarl_change)
    
    time.sleep(10)
