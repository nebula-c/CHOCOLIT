#!/usr/bin/env python3
from caen_libs import caenvme as vme
from .register_map import REGISTER_MAP
import copy

class VME_READ():
    __boardtype = "USB_V4718_LOCAL"
    __linknumber = 21475
    __conetnode = 0
    __vme_base_address = int("01230000", 16)
    __address_modifier = vme.AddressModifiers["A32_U_DATA"]
    __data_width = vme.DataWidth["D16"]
    __imon_zoom = True
    __init_success = False
    
    device: vme.Device
    
    def __init__(self,):
        try:
            self.device = vme.Device.open(vme.BoardType[self.__boardtype], self.__linknumber, self.__conetnode)
            self.__init_success = True
            self.register_map = copy.deepcopy(REGISTER_MAP)
        except:
            self.__init_success = False
            

    def setboardtype(self,myboardtype):
        self.__boardtype = myboardtype

    def setlinknumber(self,mylinknumber):
        self.__linknumber = mylinknumber
    
    def setconetnode(self,myconetnode):
        self.__conetnode = myconetnode
    
    def opendevice(self,):
        device = vme.Device.open(vme.BoardType[self.__boardtype], self.__linknumber, self.__conetnode)

    def read_cycle(self,address):
        try:
            value = self.device.read_cycle(self.__vme_base_address | address, self.__address_modifier, self.__data_width)
        except vme.Error as ex:
            print(f'Failed: {ex}')
            return
        return value
    
    def convert_register_map(self,):
        if(self.__init_success):
            converted = {}
            for key, address in self.register_map.items():
                converted[key] = self.read_cycle(address)
            return converted
        else:
            return
            

    def write_pw(self,mych_address,val):
        if(self.__init_success):
            address = self.register_map[mych_address]
            try:
                self.device.write_cycle(self.__vme_base_address | address, val, self.__address_modifier, self.__data_width)
            except vme.Error as ex:
                print(f'Failed: {ex}')
        else:
            return


    def setImonZoom(self,):
        if(self.__init_success):
            if(self.__imon_zoom):
                self.__imon_zoom = False
                for i_ch in range(6):
                    try:
                        self.write_cycle(self.register_map["CH{}_ImonRange".format(i_ch)],0x0000)
                    except ValueError as e:
                        print(f"Error: {e}")
                        continue
                
            else:
                self.__imon_zoom = True
                for i_ch in range(6):
                    try:
                        self.write_cycle(self.register_map["CH{}_ImonRange".format(i_ch)],0x001)
                    except ValueError as e:
                        print(f"Error: {e}")
                        continue
        else:
            return

    def modi_reg_map(self,bool_map):
        if(self.__init_success):
            self.register_map = copy.deepcopy(REGISTER_MAP)
            false_keys = [k for k, v in bool_map.items() if v is False]
            for fk in false_keys:
                keys_to_remove = [k for k in self.register_map if fk in k]
                for k in keys_to_remove:
                    del self.register_map[k]
        else:
            return

        # print(self.register_map)
    
    def write_cycle(self,address,val_01):
        try:
            self.device.write_cycle(self.__vme_base_address | address, val_01, self.__address_modifier, self.__data_width)
        except vme.Error as ex:
            print(f'Failed: {ex}')
