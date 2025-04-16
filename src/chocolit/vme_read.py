#!/usr/bin/env python3
from pycaenlibs import caenvme as vme
from .register_map import REGISTER_MAP
# from .register_map_rapid import REGISTER_MAP
import copy

class VME_READ():
    # __vme_base_address: int = field(default=0)
    # __address_modifier: vme.AddressModifiers = field(default=vme.AddressModifiers.A32_U_DATA)
    # __data_width: vme.DataWidth = field(default=vme.DataWidth.D32)

    __boardtype = "USB_V4718_LOCAL"
    __linknumber = 21475
    __conetnode = 0
    __vme_base_address = int("01230000", 16)
    __address_modifier = vme.AddressModifiers["A32_U_DATA"]
    __data_width = vme.DataWidth["D16"]
    __imon_zoom = False
    
    device: vme.Device
    
    def __init__(self,):
        self.device = vme.Device.open(vme.BoardType[self.__boardtype], self.__linknumber, self.__conetnode)
        self.register_map = copy.deepcopy(REGISTER_MAP)

    def setboardtype(self,myboardtype):
        self.__boardtype = myboardtype

    def setlinknumber(self,mylinknumber):
        self.__linknumber = mylinknumber
    
    def setconetnode(self,myconetnode):
        self.__conetnode = myconetnode
    
    def opendevice(self,):
        device = vme.Device.open(vme.BoardType[self.__boardtype], self.__linknumber, self.__conetnode)

    def test(self,):
        a = self.__vme_base_address
        print(a)

    def read_cycle(self,address):
        """Read cycle"""
        try:
            value = self.device.read_cycle(self.__vme_base_address | address, self.__address_modifier, self.__data_width)
        except vme.Error as ex:
            print(f'Failed: {ex}')
            return
        return value
    
    def convert_register_map(self,):
        converted = {}
        for key, address in self.register_map.items():
            converted[key] = self.read_cycle(address)
        # print(converted)
        return converted

    def settarget(self,):
        print("hello world")

    def setImonZoom(self,):
        if(self.__imon_zoom):
            self.__imon_zoom = False
            for i_ch in range(6):
                try:
                    self.write_cycle(self.register_map["CH{}_ImonRange".format(i_ch)],0x0000)
                except ValueError as e:
                    print(f"에러 발생: {e}")
                    print("error")
                    continue
            
        else:
            self.__imon_zoom = True
            for i_ch in range(6):
                try:
                    self.write_cycle(self.register_map["CH{}_ImonRange".format(i_ch)],0x001)
                except ValueError as e:
                    print(f"에러 발생: {e}")
                    print("error")
                    continue

    def modi_reg_map(self,bool_map):
        self.register_map = copy.deepcopy(REGISTER_MAP)
        false_keys = [k for k, v in bool_map.items() if v is False]
        for fk in false_keys:
            keys_to_remove = [k for k in self.register_map if fk in k]
            for k in keys_to_remove:
                del self.register_map[k]

        print(self.register_map)
    
    def write_cycle(self,address,val_01):
        """Write cycle"""
        try:
            self.device.write_cycle(self.__vme_base_address | address, val_01, self.__address_modifier, self.__data_width)
        except vme.Error as ex:
            print(f'Failed: {ex}')


