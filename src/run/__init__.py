#!/usr/bin/env python3
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
import sys
# import chocolit.Monitor as chocolit
from chocolit import Monitor as chocolit
# import chocolit.vme_read as vme


def main():
    app = QApplication(sys.argv)
    monitor = chocolit.DataMonitor()
    monitor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()