import os
import sys

import PyQt5
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QButtonGroup


class Main_window(PyQt5.QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi('uic.ui', self)
        self.setWindowTitle('Программа для учета финансов')
        self.setFixedSize(self.size())

        self.btn_group = QButtonGroup()
        self.btn_group.addButton(self.rb1)
        self.btn_group.addButton(self.rb2)
        self.btn_group.addButton(self.rb3)

        self.file_name = 'map.png'
        self.m = 6
        self.delta = 1
        self.coords = [37.620070, 55.753630]
        self.pt = ''
        self.map_type = {'Схема': 'map', 'Спутник': 'sat', 'Гибрид': 'sat,skl'}
        self.l_map = self.map_type['Схема']

        self.btn_group.buttonClicked.connect(self.change_map_type)
        self.map_update()

    def save_image(self, response):
        with open(self.file_name, "wb") as file:
            file.write(response.content)

    def change_map_type(self):
        if self.rb1.isChecked():
            self.l_map = self.map_type['Схема']
        if self.rb2.isChecked():
            self.l_map = self.map_type['Спутник']
        if self.rb3.isChecked():
            self.l_map = self.map_type['Гибрид']
        self.map_update()

    def static_map_request(self):
        server = "http://static-maps.yandex.ru/1.x/"
        map_params = {
            "ll": ','.join(list(map(str, self.coords))),
            "l": self.l_map,
            'z': str(self.m),
        }
        response = requests.get(server, map_params)
        return response

    def map_update(self):
        response = self.static_map_request()
        if response:
            self.save_image(response)
            self.pixmap = QPixmap(self.file_name)
            self.image.move(10, 40)
            self.image.resize(691, 471)
            self.image.setPixmap(self.pixmap)
        else:
            print("Ошибка выполнения запроса")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

    def keyPressEvent(self, event):
        print(event.key())
        if event.key() == 16777238:
            if self.m > 0:
                self.m -= 1
        if event.key() == 16777239:
            if self.m < 30:
                self.m += 1
        if event.key() == 16777234:
            if self.coords[0] < 180:
                self.coords[0] += self.delta
        if event.key() == 16777236:
            if self.coords[0] > -180:
                self.coords[0] -= self.delta
        if event.key() == 16777235:
            if self.coords[1] < 90:
                self.coords[1] += self.delta
        if event.key() == 16777237:
            if self.coords[1] < 90:
                self.coords[1] -= self.delta
        self.map_update()

    def closeEvent(self, event):
        os.remove(self.file_name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main_window()
    ex.show()
    sys.exit(app.exec())
