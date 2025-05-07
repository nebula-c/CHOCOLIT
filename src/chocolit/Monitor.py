#!/usr/bin/env python3

import random
import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from datetime import datetime
import os,sys
import pkg_resources
import logging
import time


from .vme_read import VME_READ


class DataMonitor(QMainWindow):
    
    __vme = VME_READ()
    reg_map_rapid = []
    reg_map_slow = []
    reg_map_once = []
    
    __is_inzoomed = True

    def __init__(self,log_filename,testmode=False):
        logging.basicConfig(
            filename=log_filename,
            level=logging.INFO,
            format="%(asctime)s, %(message)s"
        )
        self.is_test=testmode


        
        super().__init__()
        self.setWindowTitle("Channel Data Monitor")
        self.setGeometry(100, 100, 800, 600)
        
        
        self.channels = [f"CH{i}" for i in range(6)]
        # self.parameters = ["VMON", "IMON", "ISET", "VSET", "RampUp", "RampDown", "Temperature"]
        self.parameters = ["Polarity", "PW", "IMonH", "IMonL", "VMON", "ISet", "VSet", "RUp", "RDwn", "Temp", "Trip", "Status"]
        keys = self.channels + self.parameters
        self.dict_reg_bool = {key: True for key in keys}
        # self.colors = [QColor(255, 0, 0), QColor(255, 0, 0), QColor(255, 0, 0), QColor(255, 0, 0), QColor(255, 0, 0), QColor(255, 0, 0),QColor(255, 0, 0)]
        self.colors_para = {param: QColor(240,240,225) for param in self.parameters}
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        logo_layout = QHBoxLayout()
        logo_label_L = QLabel()
        logo_path = pkg_resources.resource_filename('chocolit', 'images/mylogo.png')
        pixmap_L = QPixmap(logo_path)
        scaled_pixmap_L = pixmap_L.scaled(1000, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label_L.setPixmap(scaled_pixmap_L)
        # self.layout.addWidget(logo_label_L)

        logo_label_R = QLabel()
        logo_path = pkg_resources.resource_filename('chocolit', 'images/Logo_letters_L.png')
        pixmap_R = QPixmap(logo_path)
        scaled_pixmap_R = pixmap_R.scaled(1000, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label_R.setPixmap(scaled_pixmap_R)
        # self.layout.addWidget(logo_label_R)

        logo_layout.addSpacing(20)
        logo_layout.addWidget(logo_label_L)
        logo_layout.addStretch()
        logo_layout.addWidget(logo_label_R)
        logo_layout.addSpacing(20)
        


        


        toggle_layout = QVBoxLayout()
        toggle_row_box = QHBoxLayout()
        toggle_col_box = QHBoxLayout()

        
        top_layout = QHBoxLayout()
        top_layout.addLayout(logo_layout)
        
        layout_container = QWidget()
        layout_container.setLayout(toggle_layout)
        
        layout_container.setStyleSheet("""
            QWidget {
                border: 2px solid black;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        top_right_layout = QVBoxLayout()
        top_right_layout.addWidget(layout_container)
        top_layout.addLayout(top_right_layout)
        self.layout.addLayout(top_layout)




        self.table = QTableWidget(len(self.channels), len(self.parameters))
        self.table.setHorizontalHeaderLabels(self.parameters)
        self.table.setVerticalHeaderLabels(self.channels)
        self.table.setFixedHeight(210)

        column_width = self.table.viewport().width() // self.table.columnCount()
        for row in range(self.table.columnCount()):
            self.table.setColumnWidth(row, column_width)
        
        self.layout.addWidget(self.table)
        self.table.setStyleSheet("QTableWidget { border: none; }")
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        target_col_index = self.parameters.index("PW")
        for row in range(self.table.rowCount()):
            button = QPushButton("OFF")
            button.setStyleSheet("background-color: red; color: white;")
            button.clicked.connect(self.toggle_button_state)
            self.table.setCellWidget(row, target_col_index, button)
        
        # self.table.cellChanged.connect()
        
        
        
        for row in range(6):
            checkbox = QCheckBox("CH{}".format(row))
            checkbox.setChecked(True)
            checkbox.toggled.connect(lambda checked, r=row: self.table.setRowHidden(r, not checked))
            checkbox.toggled.connect(lambda checked, k="CH{}".format(row): self.dict_reg_bool.update({k: checked}))
            # checkbox.toggled.connect(lambda checked: print(self.dict_reg_bool))
            checkbox.toggled.connect(lambda checked: self.__vme.modi_reg_map(self.dict_reg_bool))
            checkbox.toggled.connect(lambda checked, r=row: logging.info(f"CH{r} logging :  {checked}"))
            checkbox.toggled.connect(lambda checked: setattr(self, 'row_channels', [k for k, v in self.dict_reg_bool.items() if v and "CH" in k]))


            toggle_row_box.addWidget(checkbox)
        

        for col in range(len(self.parameters)):
            checkbox = QCheckBox("{}".format(self.parameters[col]))
            checkbox.setChecked(True)
            checkbox.toggled.connect(lambda checked, c=col: self.table.setColumnHidden(c, not checked))
            checkbox.toggled.connect(lambda checked, k="{}".format(self.parameters[col]): self.dict_reg_bool.update({k: checked}))
            # checkbox.toggled.connect(lambda checked: print(self.dict_reg_bool))
            checkbox.toggled.connect(lambda checked: self.__vme.modi_reg_map(self.dict_reg_bool))
            checkbox.toggled.connect(lambda checked, name=self.parameters[col]: logging.info(f"{name} logging :  {checked}"))


            toggle_col_box.addWidget(checkbox)
        
        
        self.col_headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
        # self.row_channels = [self.table.verticalHeaderItem(i).text() for i in range(self.table.rowCount())]
        self.row_channels = ch_true_keys = [k for k, v in self.dict_reg_bool.items() if v and "CH" in k]


        combo = QComboBox()
        combo.addItems(["IMon Inzoom", "Normal IMon"])
        combo.currentIndexChanged.connect(self.__vme.setImonZoom)
        toggle_row_box.addWidget(combo)
        
        toggle_layout.addLayout(toggle_row_box)
        toggle_layout.addLayout(toggle_col_box)

        self.DataTaking_once()
        
        for ch in self.row_channels:
            mykey = "{}_Polarity".format(ch)
            origin_val = self.reg_map_once[mykey]
            if origin_val == 0:
                value = "NEG"
            elif origin_val == 1:
                value = "POS"
            else:
                value = "ERROR"
            
            existing_item = self.table.item(self.row_channels.index(ch), self.col_headers.index("Polarity"))
            if existing_item is None or existing_item.text() != str(value):
                item = QTableWidgetItem(str(value))
                item.setBackground(self.colors_para["Polarity"])
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(self.row_channels.index(ch), self.col_headers.index("Polarity"), item)





        self.chart_IMON = QChart()
        self.chart_IMON.setTitle("IMON")
        self.chart_IMON_view = QChartView(self.chart_IMON)
        self.layout.addWidget(self.chart_IMON_view)
        
        self.chart_VMON = QChart()
        self.chart_VMON.setTitle("VMON")
        self.chart_VMON_view = QChartView(self.chart_VMON)
        self.layout.addWidget(self.chart_VMON_view)

        self.axis_x_IMON = QValueAxis()
        self.axis_x_IMON.setTitleText("Time")
        self.axis_x_IMON.setRange(0, 10)
        self.chart_IMON.addAxis(self.axis_x_IMON, Qt.AlignmentFlag.AlignBottom)

        self.axis_x_VMON = QValueAxis()
        self.axis_x_VMON.setTitleText("Time")
        self.axis_x_VMON.setRange(0, 10)
        self.chart_VMON.addAxis(self.axis_x_VMON, Qt.AlignmentFlag.AlignBottom)
        
        self.axis_y_IMON = QValueAxis()
        self.axis_y_IMON.setTitleText("Value")
        self.axis_y_IMON.setRange(0, 10)
        self.chart_IMON.addAxis(self.axis_y_IMON, Qt.AlignmentFlag.AlignLeft)
        
        self.axis_y_VMON = QValueAxis()
        self.axis_y_VMON.setTitleText("Value")
        self.axis_y_VMON.setRange(0, 10)
        self.chart_VMON.addAxis(self.axis_y_VMON, Qt.AlignmentFlag.AlignLeft)
        

        self.all_imon_series = []
        self.all_vmon_series = []
        for i_ch in range(0,6):
            if self.dict_reg_bool[self.channels[i_ch]]:
                imon_series = QLineSeries()
                vmon_series = QLineSeries()
                imon_series.setName("IMON")
                vmon_series.setName("VMON")    
                self.chart_IMON.addSeries(imon_series)
                self.chart_VMON.addSeries(vmon_series)
                self.all_imon_series.append(imon_series)
                self.all_vmon_series.append(vmon_series)

                self.all_imon_series[i_ch].attachAxis(self.axis_x_IMON)
                self.all_imon_series[i_ch].attachAxis(self.axis_y_IMON)
                self.all_vmon_series[i_ch].attachAxis(self.axis_x_VMON)
                self.all_vmon_series[i_ch].attachAxis(self.axis_y_VMON)
            
        # self.timer = QTimer(self)
        
        # if(self.is_test):
        #     self.timer.timeout.connect(self.Random_run)
        # else:
        #     self.timer.timeout.connect(self.VME_Run)
        
        # self.timer.start(1000)
        # self.timer.start(0)


        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.VME_Run_mon)
        self.timer1.start(0)        


        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(self.VME_Run_set)
        self.timer2.start(500)

        
        self.time_counter = 0
        self.imon_values = []
        self.vmon_values = []
        self.max_data_points = 20  # 유지할 데이터 개수
        
        # self.Random_run()
    
    def Random_run(self):
        self.time_counter += 1
        
        for i_ch in range(0,6):
            imon_values = []
            vmon_values = []
            
            imon_val = random.uniform(0, 10)
            vmon_val = random.uniform(0, 10)
            
            imon_values.append((self.time_counter, imon_val))
            vmon_values.append((self.time_counter, vmon_val))
            
            if len(imon_values) > self.max_data_points:
                imon_values.pop(0)
            if len(vmon_values) > self.max_data_points:
                vmon_values.pop(0)

            for x, y in imon_values:
                self.all_imon_series[i_ch].append(x, y)
            for x, y in vmon_values:
                self.all_vmon_series[i_ch].append(x, y)


            self.axis_x_IMON.setRange(0, 1000)
            self.axis_y_IMON.setRange(-10,10)
            self.axis_x_VMON.setRange(0, 1000)
            self.axis_y_VMON.setRange(-10,10)



        for row in range(len(self.channels)):
            for col, param in enumerate(self.parameters):
                value = round(random.uniform(0, 100), 2)

                # existing_item = self.table.item(row, col)
                # if existing_item is None or existing_item.text() != str(value):
                #     item = QTableWidgetItem(str(value))
                #     item.setBackground(self.colors_para[param])
                #     item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                #     self.table.setItem(row, col, item)
                
                
                item = QTableWidgetItem(str(value))
                item.setBackground(self.colors_para[param])
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)
        
        
        # for row in range(self.table.rowCount()):
        #     mych = self.table.verticalHeaderItem(row).text()
        #     mych_vmon_val = self.table.item(row, self.index_vmon_col).text()
        #     mych_imon_val = self.table.item(row, self.index_imon_col).text()
        #     mych_status_val = self.table.item(row, self.index_status_col).text()
            
        #     mylog_message = "{},  VMON,  {}".format(mych,mych_vmon_val)
        #     logging.info(mylog_message)
        #     mylog_message = "{},  IMon,  {}".format(mych,mych_imon_val)
        #     logging.info(mylog_message)
        #     mylog_message = "{},  Status,  {}".format(mych,mych_status_val)
        #     logging.info(mylog_message)


        for ch_key, ch_enabled in self.dict_reg_bool.items():
            if ch_key.startswith("CH") and ch_enabled:
                ch_index = int(ch_key[2:])
                mych = ch_key

                if self.dict_reg_bool.get("VMON", False):
                    # vmon_val = self.table.item(ch_index, self.index_vmon_col).text()
                    vmon_val = self.table.item(ch_index, self.col_headers.index("VMON")).text()
                    logging.info(f"{mych},  VMON,  {vmon_val}")

                if self.dict_reg_bool.get("IMonH", False):
                    # imonh_val = self.table.item(ch_index, self.index_imon_col).text()
                    imonh_val = self.table.item(ch_index, self.col_headers.index("IMonH")).text()
                    logging.info(f"{mych},  IMonH,  {imonh_val}")

                if self.dict_reg_bool.get("IMonL", False):
                    # imonl_val = self.table.item(ch_index, self.index_imon_col).text()
                    imonl_val = self.table.item(ch_index, self.col_headers.index("IMonL")).text()
                    logging.info(f"{mych},  IMonL,  {imonl_val}")

                if self.dict_reg_bool.get("Status", False):
                    # status_val = self.table.item(ch_index, self.index_status_col).text()
                    status_val = self.table.item(ch_index, self.col_headers.index("Status")).text()
                    logging.info(f"{mych},  Status,  {status_val}")


        time.sleep(1)

        

    # def DataTaking(self,):
    #     self.reg_map = self.__vme.convert_register_map()
    
    def DataTaking_rapid(self,):
        self.reg_map_rapid = self.__vme.Get_data_rapid()
    
    def DataTaking_slow(self,):
        self.reg_map_slow = self.__vme.Get_data_slow()
    
    def DataTaking_once(self,):
        self.reg_map_once = self.__vme.Get_data_once()


    def combo_func(self,):
        if(self.__is_inzoomed):
            temp_index = self.parameters.index("IMonH")
            self.parameters[temp_index] = "IMonL"
            self.table.setHorizontalHeaderItem(self.index_imon_col, QTableWidgetItem("IMonL"))
        else :
            temp_index = self.parameters.index("IMonL")
            self.parameters[temp_index] = "IMonH"
            self.table.setHorizontalHeaderItem(self.index_imon_col, QTableWidgetItem("IMonH"))


    # def VME_Run(self):
    #     nowtime = datetime.now()
    #     # print("time : {}".format(nowtime))
        

    #     self.time_counter += 1
    #     before_readout = datetime.now()
    #     self.DataTaking()
        
    #     after_readout = datetime.now()
    #     time_diff = after_readout-before_readout
    #     # print("eachtime diff : {}".format(time_diff))
    #     # print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
        
    #     for row in range(len(self.channels)):
    #         if self.dict_reg_bool[self.channels[row]]:
    #             imon_values = []
    #             vmon_values = []

    #             i_key = "CH{}_IMonH".format(row)
    #             v_key = "CH{}_VMON".format(row)
                
    #             imon_val = self.reg_map[i_key] * 0.05
    #             vmon_val = self.reg_map[v_key] * 0.1
    #             # print(vmon_val)
    #             imon_values.append((self.time_counter, imon_val))
    #             vmon_values.append((self.time_counter, vmon_val))
                
    #             if len(imon_values) > self.max_data_points:
    #                 imon_values.pop(0)
    #             if len(vmon_values) > self.max_data_points:
    #                 vmon_values.pop(0)

    #             for x, y in imon_values:
    #                 self.all_imon_series[row].append(x, y)
    #             for x, y in vmon_values:
    #                 self.all_vmon_series[row].append(x, y)


    #             self.axis_x_IMON.setRange(0, 1000)
    #             self.axis_y_IMON.setRange(0,20)
    #             self.axis_x_VMON.setRange(0, 1000)
    #             self.axis_y_VMON.setRange(0,2500)


    #             for col, param in enumerate(self.parameters):
    #                 try:
    #                     if param == "Polarity":
    #                         mykey = "CH{}_Polarity".format(row)                    
    #                         origin_val = self.reg_map[mykey]
    #                         if origin_val == 0:
    #                             value = "NEG"
    #                         elif origin_val == 1:
    #                             value = "POS"
    #                         else:
    #                             value = "ERROR"
    #                     elif param == "PW":
    #                         mykey = "CH{}_PW".format(row)
    #                         origin_val = self.reg_map[mykey]
    #                         mybutton = self.table.cellWidget(row,col)
    #                         if origin_val == 0:
    #                             value = "OFF"
    #                             mybutton.setText("OFF")
    #                             mybutton.setStyleSheet("background-color: red; color: white;")
    #                         elif origin_val == 1:
    #                             value = "ON"
    #                             mybutton.setText("ON")
    #                             mybutton.setStyleSheet("background-color: green; color: white;")
    #                         else:
    #                             value = "ERROR"
    #                     elif param == "IMonH":
    #                         mykey = "CH{}_IMonH".format(row)
    #                         origin_val = self.reg_map[mykey]
    #                         value = round(origin_val * 0.05,2)
    #                     elif param == "IMonL":
    #                         mykey = "CH{}_IMonL".format(row)
    #                         origin_val = self.reg_map[mykey]
    #                         value = round(origin_val * 0.005,3)
    #                     elif param == "VMON":
    #                         mykey = "CH{}_VMON".format(row)
    #                         origin_val = self.reg_map[mykey]
    #                         value = round(origin_val * 0.1,1)
    #                     elif param == "ISet":
    #                         mykey = "CH{}_ISet".format(row)
    #                         origin_val = self.reg_map[mykey]
    #                         value = round(origin_val * 0.05,1)
    #                     elif param == "VSet":
    #                         mykey = "CH{}_VSet".format(row)
    #                         origin_val = self.reg_map[mykey]
    #                         value = round(origin_val * 0.1,1)
    #                     elif param == "RUp":
    #                         mykey = "CH{}_RUp".format(row)
    #                         origin_val = self.reg_map[mykey]
    #                         value = round(origin_val,0)
    #                     elif param == "RDwn":
    #                         mykey = "CH{}_RDwn".format(row)
    #                         origin_val = self.reg_map[mykey]
    #                         value = round(origin_val,0)
    #                     elif param == "Temp":
    #                         mykey = "CH{}_Temp".format(row)
    #                         origin_val = self.reg_map[mykey]
    #                         value = round(origin_val,0)
    #                     elif param == "Trip":
    #                         mykey = "CH{}_Trip".format(row)
    #                         origin_val = self.reg_map[mykey]
    #                         value = round(origin_val * 0.1,1)
    #                     elif param == "Status":
    #                         mykey = "CH{}_Status".format(row)
    #                         origin_val = self.reg_map[mykey]
    #                         if origin_val == 0:
    #                             value = "ON"
    #                         elif origin_val == 1:
    #                             value = "Ramp UP"
    #                         elif origin_val == 2:
    #                             value = "Ramp DOWN"
    #                         elif origin_val == 3:
    #                             value = "OVER CURRENT"
    #                         elif origin_val == 4:
    #                             value = "OVER VOLTAGE"
    #                         elif origin_val == 5:
    #                             value = "UNDER VOLTAGE"
    #                         elif origin_val == 6:
    #                             value = "MAXV"
    #                         elif origin_val == 7:
    #                             value = "MAXI"
    #                         elif origin_val == 8:
    #                             value = "TRIP"
    #                         elif origin_val == 9:
    #                             value = "OVER POWER"
    #                         elif origin_val == 10:
    #                             value = "OVER TEMPERATURE"
    #                         elif origin_val == 11:
    #                             value = "DISABLED"
    #                         elif origin_val == 12:
    #                             value = "INTERLOCK"
    #                         elif origin_val == 13:
    #                             value = "UNCALIBRATED"
    #                         elif origin_val == 14:
    #                             value = "UNKNOWN"
    #                         elif origin_val == 15:
    #                             value = "UNKNOWN"
    #                         else:
    #                             value = "UNKNOWN"
    #                     else:
    #                         value = "ERROR"
    #                 except:
    #                     continue
                    
    #                 # item = QTableWidgetItem(str(value))
    #                 # item.setBackground(self.colors_para[param])
    #                 # item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #                 # self.table.setItem(row, col, item)

    #                 existing_item = self.table.item(row, col)
    #                 if existing_item is None or existing_item.text() != str(value):
    #                     item = QTableWidgetItem(str(value))
    #                     item.setBackground(self.colors_para[param])
    #                     item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    #                     self.table.setItem(row, col, item)
        
        
    #     # for row in range(self.table.rowCount()):
    #     #     mych = self.table.verticalHeaderItem(row).text()
    #     #     mych_vmon_val = self.table.item(row, self.index_vmon_col).text()
    #     #     mych_imon_val = self.table.item(row, self.index_imon_col).text()
    #     #     mych_status_val = self.table.item(row, self.index_status_col).text()
            
    #     #     mylog_message = "{},  VMON,  {}".format(mych,mych_vmon_val)
    #     #     logging.info(mylog_message)
    #     #     mylog_message = "{},  IMon,  {}".format(mych,mych_imon_val)
    #     #     logging.info(mylog_message)
    #     #     mylog_message = "{},  Status,  {}".format(mych,mych_status_val)
    #     #     logging.info(mylog_message)

    #     for ch_key, ch_enabled in self.dict_reg_bool.items():
    #         if ch_key.startswith("CH") and ch_enabled:
    #             ch_index = int(ch_key[2:])
    #             mych = ch_key

    #             if self.dict_reg_bool.get("VMON", False):
    #                 vmon_val = self.table.item(ch_index, self.col_headers.index("VMON")).text()
    #                 logging.info(f"{mych},  VMON,  {vmon_val}")

    #             if self.dict_reg_bool.get("IMonH", False):
    #                 imonh_val = self.table.item(ch_index, self.col_headers.index("IMonH")).text()
    #                 logging.info(f"{mych},  IMonH,  {imonh_val}")

    #             if self.dict_reg_bool.get("IMonL", False):
    #                 imonl_val = self.table.item(ch_index, self.col_headers.index("IMonL")).text()
    #                 logging.info(f"{mych},  IMonL,  {imonl_val}")

    #             if self.dict_reg_bool.get("Status", False):
    #                 status_val = self.table.item(ch_index, self.col_headers.index("Status")).text()
    #                 logging.info(f"{mych},  Status,  {status_val}")


    def toggle_button_state(self,):
        button = self.sender()
        key = None
        for row in range(self.table.rowCount()):
            if self.table.cellWidget(row, 1) == button:
                channel_name = self.table.verticalHeaderItem(row).text()
                key = "{}_PW".format(channel_name)
                break
        
        if button.text() == "ON":
            button.setText("OFF")
            button.setStyleSheet("background-color: red; color: white;")
            self.__vme.write_pw(key,0)
        else:
            button.setText("ON")
            button.setStyleSheet("background-color: green; color: white;")
            self.__vme.write_pw(key,1)

    def VME_Run_mon(self,):        
        self.DataTaking_rapid()
        for ch in self.row_channels:
        
            if self.dict_reg_bool["PW"]:
                mykey = "{}_PW".format(ch)
                origin_val = self.reg_map_rapid[mykey]
                mybutton = self.table.cellWidget(self.row_channels.index(ch),self.col_headers.index("PW"))
                if origin_val == 0:
                    value = "OFF"
                    mybutton.setText("OFF")
                    mybutton.setStyleSheet("background-color: red; color: white;")
                elif origin_val == 1:
                    value = "ON"
                    mybutton.setText("ON")
                    mybutton.setStyleSheet("background-color: green; color: white;")
                else:
                    value = "ERROR"
            
            if self.dict_reg_bool["IMonH"]:
            
                mykey = "{}_IMonH".format(ch)
                origin_val = self.reg_map_rapid[mykey]
                value = round(origin_val * 0.05,2)
                
                existing_item = self.table.item(self.row_channels.index(ch), self.col_headers.index("IMonH"))
                if existing_item is None or existing_item.text() != str(value):
                    item = QTableWidgetItem(str(value))
                    item.setBackground(self.colors_para["IMonH"])
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(self.row_channels.index(ch), self.col_headers.index("IMonH"), item)


            if self.dict_reg_bool["IMonL"]:
                mykey = "{}_IMonL".format(ch)
                origin_val = self.reg_map_rapid[mykey]
                value = round(origin_val * 0.005,3)

                existing_item = self.table.item(self.row_channels.index(ch), self.col_headers.index("IMonL"))
                if existing_item is None or existing_item.text() != str(value):
                    item = QTableWidgetItem(str(value))
                    item.setBackground(self.colors_para["IMonL"])
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(self.row_channels.index(ch), self.col_headers.index("IMonL"), item)


            if self.dict_reg_bool["VMON"]:
                mykey = "{}_VMON".format(ch)
                origin_val = self.reg_map_rapid[mykey]
                value = round(origin_val * 0.1,1)
                
                existing_item = self.table.item(self.row_channels.index(ch), self.col_headers.index("VMON"))
                if existing_item is None or existing_item.text() != str(value):
                    item = QTableWidgetItem(str(value))
                    item.setBackground(self.colors_para["VMON"])
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(self.row_channels.index(ch), self.col_headers.index("VMON"), item)


            if self.dict_reg_bool["Status"]:
                mykey = "{}_Status".format(ch)
                origin_val = self.reg_map_rapid[mykey]
                if origin_val == 0:
                    value = "ON"
                elif origin_val == 1:
                    value = "Ramp UP"
                elif origin_val == 2:
                    value = "Ramp DOWN"
                elif origin_val == 3:
                    value = "OVER CURRENT"
                elif origin_val == 4:
                    value = "OVER VOLTAGE"
                elif origin_val == 5:
                    value = "UNDER VOLTAGE"
                elif origin_val == 6:
                    value = "MAXV"
                elif origin_val == 7:
                    value = "MAXI"
                elif origin_val == 8:
                    value = "TRIP"
                elif origin_val == 9:
                    value = "OVER POWER"
                elif origin_val == 10:
                    value = "OVER TEMPERATURE"
                elif origin_val == 11:
                    value = "DISABLED"
                elif origin_val == 12:
                    value = "INTERLOCK"
                elif origin_val == 13:
                    value = "UNCALIBRATED"
                elif origin_val == 14:
                    value = "UNKNOWN"
                elif origin_val == 15:
                    value = "UNKNOWN"
                else:
                    value = "UNKNOWN"

                existing_item = self.table.item(self.row_channels.index(ch), self.col_headers.index("Status"))
                if existing_item is None or existing_item.text() != str(value):
                    item = QTableWidgetItem(str(value))
                    item.setBackground(self.colors_para["Status"])
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(self.row_channels.index(ch), self.col_headers.index("Status"), item)



    def VME_Run_set(self,):        
        self.DataTaking_slow()
        
        for ch in self.row_channels:
            if self.dict_reg_bool["ISet"]:
                mykey = "{}_ISet".format(ch)
                origin_val = self.reg_map_slow[mykey]
                value = round(origin_val * 0.05,1)

                existing_item = self.table.item(self.row_channels.index(ch), self.col_headers.index("ISet"))
                if existing_item is None or existing_item.text() != str(value):
                    item = QTableWidgetItem(str(value))
                    item.setBackground(self.colors_para["ISet"])
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(self.row_channels.index(ch), self.col_headers.index("ISet"), item)

            if self.dict_reg_bool["VSet"]:
                mykey = "{}_VSet".format(ch)
                origin_val = self.reg_map_slow[mykey]
                value = round(origin_val * 0.1,1)

                existing_item = self.table.item(self.row_channels.index(ch), self.col_headers.index("VSet"))
                if existing_item is None or existing_item.text() != str(value):
                    item = QTableWidgetItem(str(value))
                    item.setBackground(self.colors_para["VSet"])
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(self.row_channels.index(ch), self.col_headers.index("VSet"), item)


            if self.dict_reg_bool["RUp"]:
                mykey = "{}_RUp".format(ch)
                origin_val = self.reg_map_slow[mykey]
                value = round(origin_val,0)

                existing_item = self.table.item(self.row_channels.index(ch), self.col_headers.index("RUp"))
                if existing_item is None or existing_item.text() != str(value):
                    item = QTableWidgetItem(str(value))
                    item.setBackground(self.colors_para["RUp"])
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(self.row_channels.index(ch), self.col_headers.index("RUp"), item)


            if self.dict_reg_bool["RDwn"]:
                mykey = "{}_RDwn".format(ch)
                origin_val = self.reg_map_slow[mykey]
                value = round(origin_val,0)

                existing_item = self.table.item(self.row_channels.index(ch), self.col_headers.index("RDwn"))
                if existing_item is None or existing_item.text() != str(value):
                    item = QTableWidgetItem(str(value))
                    item.setBackground(self.colors_para["RDwn"])
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(self.row_channels.index(ch), self.col_headers.index("RDwn"), item)


            if self.dict_reg_bool["Temp"]:
                mykey = "{}_Temp".format(ch)
                origin_val = self.reg_map_slow[mykey]
                value = round(origin_val,0)

                existing_item = self.table.item(self.row_channels.index(ch), self.col_headers.index("Temp"))
                if existing_item is None or existing_item.text() != str(value):
                    item = QTableWidgetItem(str(value))
                    item.setBackground(self.colors_para["Temp"])
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(self.row_channels.index(ch), self.col_headers.index("Temp"), item)


            if self.dict_reg_bool["Trip"]:
                mykey = "{}_Trip".format(ch)
                origin_val = self.reg_map_slow[mykey]
                value = round(origin_val * 0.1,1)
                
                existing_item = self.table.item(self.row_channels.index(ch), self.col_headers.index("Trip"))
                if existing_item is None or existing_item.text() != str(value):
                    item = QTableWidgetItem(str(value))
                    item.setBackground(self.colors_para["Trip"])
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(self.row_channels.index(ch), self.col_headers.index("Trip"), item)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    monitor = DataMonitor()
    # monitor.Random_run()
    monitor.show()
    sys.exit(app.exec())


