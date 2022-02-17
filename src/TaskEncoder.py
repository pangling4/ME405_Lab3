'''@file                TaskEncoder.py
   @brief               
   @details              
                    
   @author              Philip Pang
   @author              Tim Jain
   @author              Jonathan Cederquist
   @date                February 17, 2022   
'''

import EncoderDriver
import pyb

class TaskEncoder:
    
    def __init__(self, enc_ID, share_pos, share_Stop):
        self.share_Stop = share_Stop
        self.share_pos = share_pos
        self.enc_ID = enc_ID
        if enc_ID == 1:
            # Slo_Enco
            self.Enco = EncoderDriver.EncoderDriver(pyb.Pin(pyb.Pin.cpu.B6), pyb.Pin(pyb.Pin.cpu.B7), 4)
        elif enc_ID == 2:
            # Bro_Enco
            self.Enco = EncoderDriver.EncoderDriver(pyb.Pin(pyb.Pin.cpu.C6), pyb.Pin(pyb.Pin.cpu.C7), 8)
        
        self.Enco.zero()
    
    def task(self):
        while True: 
            if self.share_Stop.get():
                self.Enco.zero()
                print("Zeroing Encoder" + str(self.enc_ID))
                self.share_Stop.put(0)
            
            self.Enco.update()
            self.share_pos.put(self.Enco.read())
            yield (0)
        
