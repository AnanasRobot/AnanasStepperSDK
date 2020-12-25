#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import serial
import logging
import binascii
import platform
import threading

if platform.system() == "Windows":
    from  serial.tools import list_ports
else:
    import glob, os, re

class SerialHelper(object):
    def __init__(self, Port="COM6", BaudRate="9600", ByteSize="8", Parity="N", Stopbits="1"):
        '''
        初始化一些参数
        '''
        self.port = Port
        self.baudrate = BaudRate
        self.bytesize = ByteSize
        self.parity = Parity
        self.stopbits = Stopbits
        self.threshold_value = 1
        self.receive_data = ""

        self._serial = None
        self._is_connected = False
        self.tDataReceived = None
        
        self.serial_lock = threading.RLock()

    def connect(self, timeout=2):
        '''
        连接设备
        '''
        self.serial_lock.acquire()
        
        self._serial = serial.Serial()
        self._serial.port = self.port
        self._serial.baudrate = self.baudrate
        self._serial.bytesize = int(self.bytesize)
        self._serial.parity = self.parity
        self._serial.stopbits = int(self.stopbits)
        self._serial.timeout = timeout

        try:
            self._serial.open()
            if self._serial.isOpen():
                self._is_connected = True
        except Exception as e:
            self._is_connected = False
            logging.error(e)
            
        self.serial_lock.release()
        
    def disconnect(self):
        '''
        断开连接
        '''
        self.serial_lock.acquire()
        if self._serial:
            self._is_connected = False
            self._serial.close()
            self._serial = None
        self.serial_lock.release()

    def write(self, data, isHex=False):
        '''
        发送数据给串口设备
        '''
        if self._is_connected:
            if isHex:
                data = binascii.unhexlify(data)
            self._serial.write(bytes(data))

    def on_connected_changed(self, func):
        '''
        set serial connected status change callback
        '''
        tConnected = threading.Thread(target=self._on_connected_changed, args=(func, ))
        tConnected.setDaemon(True)
        tConnected.start()

    def _on_connected_changed(self, func):
        '''
        set serial connected status change callback
        '''
        self._is_connected_temp = False
        while True:
            self.serial_lock.acquire()
            if platform.system() == "Windows":
                for com in list_ports.comports():
                    if com[0] == self.port:
                        self._is_connected = True
                        break
            elif platform.system() == "Linux":
                if self.port in self.find_usb_tty():
                    self._is_connected = True

            if self._is_connected_temp != self._is_connected:
                func(self._is_connected)
            self._is_connected_temp = self._is_connected
            time.sleep(0.8)
            self.serial_lock.release()

    def on_data_received(self, func):
        '''
        set serial data recieved callback
        '''
        self.tDataReceived = threading.Thread(target=self._on_data_received, args=(func, ))
        self.tDataReceived.setDaemon(True)
        self.tDataReceived.start()
    
    def _on_data_received(self, func):
        '''
        set serial data recieved callback
        '''
        while True:
            self.serial_lock.acquire()
            if self._is_connected and self._serial is not None:
                try:
                    number = self._serial.inWaiting()
                    if number > 0:
                        data = self._serial.read(number)
                        if data:
                            func(data)
                except Exception as e:
                    self._is_connected = False
                    self._serial = None
                    logging.exception(e)
                    logging.error("except: leave data receive thread")
                    break
            self.serial_lock.release()

    def find_usb_tty(self, vendor_id=None, product_id=None):
        '''
        查找Linux下的串口设备
        '''
        tty_devs = list()
        for dn in glob.glob('/sys/bus/usb/devices/*') :
            try:
                vid = int(open(os.path.join(dn, "idVendor" )).read().strip(), 16)
                pid = int(open(os.path.join(dn, "idProduct")).read().strip(), 16)
                if  ((vendor_id is None) or (vid == vendor_id)) and ((product_id is None) or (pid == product_id)) :
                    dns = glob.glob(os.path.join(dn, os.path.basename(dn) + "*"))
                    for sdn in dns :
                        for fn in glob.glob(os.path.join(sdn, "*")) :
                            if  re.search(r"\/ttyUSB[0-9]+$", fn) :
                                tty_devs.append(os.path.join("/dev", os.path.basename(fn)))
            except Exception as ex:
                logging.error("find usb tty occur a error")

        return tty_devs

class testHelper(object):
    def __init__(self):
        self.myserial = SerialHelper(Port="COM4", BaudRate="115200")
        self.myserial.on_connected_changed(self.myserial_on_connected_changed)

    def write(self, data):
        self.myserial.write(data, False)

    def myserial_on_connected_changed(self, is_connected):
        if is_connected:
            print("Connected")
            self.myserial.connect_ananas()
            self.myserial.on_data_received(self.myserial_on_data_received)
        else:
            print("DisConnected")

    def myserial_on_data_received(self, data):
        print(data)
        
    def disconnect(self):
        if self.myserial:
            self.myserial.disconnect()

if __name__ == '__main__':
    myserial = testHelper()
    print(str(myserial))
    time.sleep(1)
    myserial.write("G28 X1 F2000 D0\n")
    myserial.write("G28 X2 F2000 D1\n")
    myserial.write("G0 X1 P-10000 F10000\n")
    myserial.write("G0 X2 P10000 F10000\n")
    count = 0
    while count < 16:
        print("Waiting: %s s"%count)
        time.sleep(1)
        count += 1
        
    myserial.disconnect()
