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


# from .vme_read import VME_READ


class DataMonitor(QMainWindow):
    # if(is_test):

    # else:    
    # if(not self.is_test):
    #     from .vme_read import VME_READ
    #     __vme = VME_READ()
    #     reg_map = __vme.convert_register_map()
    
    __vme = None
    reg_map = None
    __is_inzoomed = True
    index_vmon_col = -1
    index_imon_col = -1
    index_status_col = -1

    def __init__(self,log_filename,testmode=False):
        logging.basicConfig(
            filename=log_filename,
            level=logging.INFO,
            format="%(asctime)s, %(message)s"
        )
        self.is_test=testmode
        
        if(not self.is_test):
            from .vme_read import VME_READ
            self.__vme = VME_READ()
            self.reg_map = __vme.convert_register_map()


        
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

        
    

        

        # self.col_box = QHBoxLayout()
        # self.layout.addLayout(self.col_box)
        # for col in range(4):
        #     combo = QComboBox()
        #     combo.addItems(["보이기", "숨기기"])
        #     combo.currentIndexChanged.connect(lambda idx, c=col: self.table.setColumnHidden(c, idx == 1))
        #     self.col_box.addWidget(QLabel(f"Col {col}:"))
        #     self.col_box.addWidget(combo)

        
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
        
        for row in range(6):
            checkbox = QCheckBox("CH{}".format(row))
            checkbox.setChecked(True)
            checkbox.toggled.connect(lambda checked, r=row: self.table.setRowHidden(r, not checked))
            checkbox.toggled.connect(lambda checked, k="CH{}".format(row): self.dict_reg_bool.update({k: checked}))
            # checkbox.toggled.connect(lambda checked: print(self.dict_reg_bool))
            checkbox.toggled.connect(lambda checked: self.__vme.modi_reg_map(self.dict_reg_bool))
            checkbox.toggled.connect(lambda checked, r=row: logging.info(f"CH{r} logging :  {checked}"))

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

        if(self.__is_inzoomed):
            imon_key = "IMonL"
        else:
            imon_key = "IMonH"
        for col in range(self.table.columnCount()):
            if self.table.horizontalHeaderItem(col).text() == "VMON":
                self.index_vmon_col = col
            if self.table.horizontalHeaderItem(col).text() == imon_key:
                self.index_imon_col = col
            if self.table.horizontalHeaderItem(col).text() == "Status":
                self.index_status_col = col

        combo = QComboBox()
        combo.addItems(["IMon Inzoom", "Normal IMon"])
        combo.currentIndexChanged.connect(self.__vme.setImonZoom)
        toggle_row_box.addWidget(combo)
        
        toggle_layout.addLayout(toggle_row_box)
        toggle_layout.addLayout(toggle_col_box)

        
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
            
        self.timer = QTimer(self)
        
        if(is_test):
            self.timer.timeout.connect(self.Random_run)
        else:
            self.timer.timeout.connect(self.VME_Run)
        
        # self.timer.start(1000)
        self.timer.start(1)
        
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
                item = QTableWidgetItem(str(value))
                item.setBackground(self.colors_para[param])
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)
        
        time.sleep(0.1)

        

    def DataTaking(self,):
        self.reg_map = self.__vme.convert_register_map()


    def combo_func(self,):
        if(self.__is_inzoomed):
            temp_index = self.parameters.index("IMonH")
            self.parameters[temp_index] = "IMonL"
            self.table.setHorizontalHeaderItem(self.index_imon_col, QTableWidgetItem("IMonL"))
        else :
            temp_index = self.parameters.index("IMonL")
            self.parameters[temp_index] = "IMonH"
            self.table.setHorizontalHeaderItem(self.index_imon_col, QTableWidgetItem("IMonH"))


    def VME_Run(self):
        nowtime = datetime.now()
        # print("time : {}".format(nowtime))
        

        self.time_counter += 1
        before_readout = datetime.now()
        self.DataTaking()
        
        after_readout = datetime.now()
        time_diff = after_readout-before_readout
        # print("eachtime diff : {}".format(time_diff))
        # print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
        
        for row in range(len(self.channels)):
            if self.dict_reg_bool[self.channels[row]]:
                imon_values = []
                vmon_values = []

                i_key = "CH{}_IMonH".format(row)
                v_key = "CH{}_VMON".format(row)
                
                imon_val = self.reg_map[i_key] * 0.05
                vmon_val = self.reg_map[v_key] * 0.1
                # print(vmon_val)
                imon_values.append((self.time_counter, imon_val))
                vmon_values.append((self.time_counter, vmon_val))
                
                if len(imon_values) > self.max_data_points:
                    imon_values.pop(0)
                if len(vmon_values) > self.max_data_points:
                    vmon_values.pop(0)

                for x, y in imon_values:
                    self.all_imon_series[row].append(x, y)
                for x, y in vmon_values:
                    self.all_vmon_series[row].append(x, y)


                self.axis_x_IMON.setRange(0, 1000)
                self.axis_y_IMON.setRange(0,20)
                self.axis_x_VMON.setRange(0, 1000)
                self.axis_y_VMON.setRange(0,2500)


                for col, param in enumerate(self.parameters):
                    try:
                        # if col == 0:
                        if param == "Polarity":
                            mykey = "CH{}_Polarity".format(row)                    
                            origin_val = self.reg_map[mykey]
                            if origin_val == 0:
                                value = "NEG"
                            elif origin_val == 1:
                                value = "POS"
                            else:
                                value = "ERROR"
                        # elif col == 1:
                        elif param == "PW":
                            mykey = "CH{}_PW".format(row)
                            origin_val = self.reg_map[mykey]
                            mybutton = self.table.cellWidget(row,col)
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
                        # elif col == 2:
                        elif param == "IMonH":
                            mykey = "CH{}_IMonH".format(row)
                            origin_val = self.reg_map[mykey]
                            value = round(origin_val * 0.05,2)
                            # print("IMonH : {}".format(value))
                        # elif col == 3:
                        elif param == "IMonL":
                            mykey = "CH{}_IMonL".format(row)
                            origin_val = self.reg_map[mykey]
                            value = round(origin_val * 0.005,3)
                        # elif col == 4:
                        elif param == "VMON":
                            mykey = "CH{}_VMON".format(row)
                            origin_val = self.reg_map[mykey]
                            value = round(origin_val * 0.1,1)
                        # elif col == 5:
                        elif param == "ISet":
                            mykey = "CH{}_ISet".format(row)
                            origin_val = self.reg_map[mykey]
                            value = round(origin_val * 0.05,1)
                        # elif col == 6:
                        elif param == "VSet":
                            mykey = "CH{}_VSet".format(row)
                            origin_val = self.reg_map[mykey]
                            value = round(origin_val * 0.1,1)
                        # elif col == 7:
                        elif param == "RUp":
                            mykey = "CH{}_RUp".format(row)
                            origin_val = self.reg_map[mykey]
                            value = round(origin_val,0)
                        # elif col == 8:
                        elif param == "RDwn":
                            mykey = "CH{}_RDwn".format(row)
                            origin_val = self.reg_map[mykey]
                            value = round(origin_val,0)
                        # elif col == 9:
                        elif param == "Temp":
                            mykey = "CH{}_Temp".format(row)
                            origin_val = self.reg_map[mykey]
                            value = round(origin_val,0)
                        # elif col == 10:
                        elif param == "Trip":
                            mykey = "CH{}_Trip".format(row)
                            origin_val = self.reg_map[mykey]
                            value = round(origin_val * 0.1,1)
                        # elif col == 11:
                        elif param == "Status":
                            mykey = "CH{}_Status".format(row)
                            origin_val = self.reg_map[mykey]
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
                        else:
                            value = "ERROR"
                    except:
                        continue
                    
                    item = QTableWidgetItem(str(value))
                    item.setBackground(self.colors_para[param])
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, col, item)
        
        
        for row in range(self.table.rowCount()):
            mych = self.table.verticalHeaderItem(row).text()
            mych_vmon_val = self.table.item(row, self.index_vmon_col).text()
            mych_imon_val = self.table.item(row, self.index_imon_col).text()
            mych_status_val = self.table.item(row, self.index_status_col).text()
            
            mylog_message = "{},  VMON,  {}".format(mych,mych_vmon_val)
            logging.info(mylog_message)
            mylog_message = "{},  IMon,  {}".format(mych,mych_imon_val)
            logging.info(mylog_message)
            mylog_message = "{},  Status,  {}".format(mych,mych_status_val)
            logging.info(mylog_message)



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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    monitor = DataMonitor()
    # monitor.Random_run()
    monitor.show()
    sys.exit(app.exec())


