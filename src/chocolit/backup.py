#!/usr/bin/env python3

import sys
import random
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView, QSizePolicy
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

import chocolit.vme_read as vme


class DataMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Channel Data Monitor")
        self.setGeometry(100, 100, 800, 600)
        
        self.channels = [f"CH{i}" for i in range(6)]
        # self.parameters = ["VMON", "IMON", "ISET", "VSET", "RampUp", "RampDown", "Temperature"]
        self.parameters = ["Polarity", "PW", "IMON", "VMON", "ISET", "VSET", "RampUp", "RampDown", "Temp", "Trip", "Status"]
        # self.colors = [QColor(255, 0, 0), QColor(255, 0, 0), QColor(255, 0, 0), QColor(255, 0, 0), QColor(255, 0, 0), QColor(255, 0, 0),QColor(255, 0, 0)]
        self.colors_para = {param: QColor(240,240,225) for param in self.parameters}
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.table = QTableWidget(len(self.channels), len(self.parameters))
        self.table.setHorizontalHeaderLabels(self.parameters)
        self.table.setVerticalHeaderLabels(self.channels)
        # self.table.setMinimumHeight(200)  # 테이블 최소 높이 보장
        self.table.setFixedHeight(210)

        column_width = self.table.viewport().width() // self.table.columnCount()
        for row in range(self.table.columnCount()):
            self.table.setColumnWidth(row, column_width)
        
        self.layout.addWidget(self.table)
        self.table.setStyleSheet("QTableWidget { border: none; }")
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # self.chart = QChart()
        # self.chart.setTitle("IMON & VMON Over Time")
        # self.chart_view = QChartView(self.chart)
        # self.layout.addWidget(self.chart_view)
        
        self.chart_IMON = QChart()
        self.chart_IMON.setTitle("IMON")
        self.chart_IMON_view = QChartView(self.chart_IMON)
        self.layout.addWidget(self.chart_IMON_view)
        
        self.chart_VMON = QChart()
        self.chart_VMON.setTitle("VMON")
        self.chart_VMON_view = QChartView(self.chart_VMON)
        self.layout.addWidget(self.chart_VMON_view)
        
        # self.imon_series_both = QLineSeries()
        # self.vmon_series_both = QLineSeries()
        # self.imon_series_both.setName("IMON")
        # self.vmon_series_both.setName("VMON")
        # self.chart.addSeries(self.imon_series_both)
        # self.chart.addSeries(self.vmon_series_both)

        self.imon_series = QLineSeries()
        self.vmon_series = QLineSeries()
        self.imon_series.setName("IMON")
        self.vmon_series.setName("VMON")
        self.chart_IMON.addSeries(self.imon_series)
        self.chart_VMON.addSeries(self.vmon_series)
        # self.chart_IMON.addSeries(self.imon_series)
        # self.chart_VMON.addSeries(self.vmon_series)
        
        # self.axis_x = QValueAxis()
        # self.axis_x.setTitleText("Time")
        # self.axis_x.setRange(0, 10)
        # self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)

        self.axis_x_IMON = QValueAxis()
        self.axis_x_IMON.setTitleText("Time")
        self.axis_x_IMON.setRange(0, 10)
        self.chart_IMON.addAxis(self.axis_x_IMON, Qt.AlignmentFlag.AlignBottom)

        self.axis_x_VMON = QValueAxis()
        self.axis_x_VMON.setTitleText("Time")
        self.axis_x_VMON.setRange(0, 10)
        self.chart_VMON.addAxis(self.axis_x_VMON, Qt.AlignmentFlag.AlignBottom)
        
        # self.axis_y = QValueAxis()
        # self.axis_y.setTitleText("Value")
        # self.axis_y.setRange(0, 10)
        # self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)

        self.axis_y_IMON = QValueAxis()
        self.axis_y_IMON.setTitleText("Value")
        self.axis_y_IMON.setRange(0, 10)
        self.chart_IMON.addAxis(self.axis_y_IMON, Qt.AlignmentFlag.AlignLeft)
        
        self.axis_y_VMON = QValueAxis()
        self.axis_y_VMON.setTitleText("Value")
        self.axis_y_VMON.setRange(0, 10)
        self.chart_VMON.addAxis(self.axis_y_VMON, Qt.AlignmentFlag.AlignLeft)
        
        # self.imon_series_both.attachAxis(self.axis_x)
        # self.imon_series_both.attachAxis(self.axis_y)
        # self.vmon_series_both.attachAxis(self.axis_x)
        # self.vmon_series_both.attachAxis(self.axis_y)
        self.imon_series.attachAxis(self.axis_x_IMON)
        self.imon_series.attachAxis(self.axis_y_IMON)
        self.vmon_series.attachAxis(self.axis_x_VMON)
        self.vmon_series.attachAxis(self.axis_y_VMON)
        
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.Random_run)
        # self.timer.timeout.connect(self.Random_run)
        self.timer.start(1000)
        
        self.time_counter = 0
        self.imon_values = []
        self.vmon_values = []
        self.max_data_points = 20  # 유지할 데이터 개수
        
        # self.Random_run()
    
    def Random_run(self):
        self.time_counter += 1
        imon_val = random.uniform(0, 10)
        vmon_val = random.uniform(0, 10)
        
        self.imon_values.append((self.time_counter, imon_val))
        self.vmon_values.append((self.time_counter, vmon_val))
        
        if len(self.imon_values) > self.max_data_points:
            self.imon_values.pop(0)
        if len(self.vmon_values) > self.max_data_points:
            self.vmon_values.pop(0)
        
        self.imon_series.clear()
        self.vmon_series.clear()
        # self.imon_series_both.clear()
        # self.vmon_series_both.clear()
        
        for x, y in self.imon_values:
            self.imon_series.append(x, y)
            # self.imon_series_both.append(x, y)
        for x, y in self.vmon_values:
            self.vmon_series.append(x, y)
            # self.vmon_series_both.append(x, y)
        
        # 축 범위 자동 조정
        min_x = min(x for x, _ in self.imon_values)
        max_x = max(x for x, _ in self.imon_values)
        min_y = min(min(y for _, y in self.imon_values), min(y for _, y in self.vmon_values))
        max_y = max(max(y for _, y in self.imon_values), max(y for _, y in self.vmon_values))
        
        # self.axis_x.setRange(min_x, max_x)
        # self.axis_y.setRange(min_y - 1, max_y + 1)
        self.axis_x_IMON.setRange(min_x, max_x)
        self.axis_y_IMON.setRange(min_y - 1, max_y + 1)
        self.axis_x_VMON.setRange(min_x, max_x)
        self.axis_y_VMON.setRange(min_y - 1, max_y + 1)
        
        for row in range(len(self.channels)):
            for col, param in enumerate(self.parameters):
                value = round(random.uniform(0, 100), 2)
                item = QTableWidgetItem(str(value))
                item.setBackground(self.colors_para[param])
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)

    def VME_Run(self):
        reg_map = vme.convert_register_map()
        
        self.time_counter += 1
        imon_val = reg_map[""]
        vmon_val = reg_map[""]
        
        self.imon_values.append((self.time_counter, imon_val))
        self.vmon_values.append((self.time_counter, vmon_val))
        
        if len(self.imon_values) > self.max_data_points:
            self.imon_values.pop(0)
        if len(self.vmon_values) > self.max_data_points:
            self.vmon_values.pop(0)
        
        self.imon_series.clear()
        self.vmon_series.clear()
       
        
        for x, y in self.imon_values:
            self.imon_series.append(x, y)
        for x, y in self.vmon_values:
            self.vmon_series.append(x, y)
        
        
        min_x = min(x for x, _ in self.imon_values)
        max_x = max(x for x, _ in self.imon_values)
        min_y = min(min(y for _, y in self.imon_values), min(y for _, y in self.vmon_values))
        max_y = max(max(y for _, y in self.imon_values), max(y for _, y in self.vmon_values))
        

        self.axis_x_IMON.setRange(min_x, max_x)
        self.axis_y_IMON.setRange(min_y - 1, max_y + 1)
        self.axis_x_VMON.setRange(min_x, max_x)
        self.axis_y_VMON.setRange(min_y - 1, max_y + 1)
        
        for row in range(len(self.channels)):
            for col, param in enumerate(self.parameters):
                value = round(random.uniform(0, 100), 2)
                item = QTableWidgetItem(str(value))
                item.setBackground(self.colors_para[param])
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    monitor = DataMonitor()
    monitor.Random_run()
    monitor.show()
    sys.exit(app.exec())





