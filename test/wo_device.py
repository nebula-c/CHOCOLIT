#!/usr/bin/env python3
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
import sys
from chocolit import Monitor as chocolit
from datetime import datetime



def main():
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = "HV_log_{}.txt".format(now)

    app = QApplication(sys.argv)
    monitor = chocolit.DataMonitor(log_filename,testmode=True)
    monitor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()