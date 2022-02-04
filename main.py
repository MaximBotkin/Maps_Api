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
        self.setWindowTitle('Map API')
        self.setFixedSize(self.size())

        self.btn_group = QButtonGroup()
        self.btn_group.addButton(self.rb1)
        self.btn_group.addButton(self.rb2)
        self.btn_group.addButton(self.rb3)

        self.file_name = 'map.png'
        self.m = 10
        self.delta = 1
        self.coords = [37.620070, 55.753630]
        self.pt = ''
        self.map_type = {'Схема': 'map', 'Спутник': 'sat', 'Гибрид': 'sat,skl'}
        self.l_map = self.map_type['Схема']
        self.postal_code = False

        self.btn_group.buttonClicked.connect(self.change_map_type)
        self.search_btn.clicked.connect(self.search_pt)
        self.reset_btn.clicked.connect(self.reset)
        self.check_postal.clicked.connect(self.check_post)
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

    def search_pt(self):
        try:
            adress = self.search_text.text()
            geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

            geocoder_params = {
                "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
                "geocode": adress,
                "format": "json"}

            json_response = requests.get(geocoder_api_server, geocoder_params).json()
            geo_object = json_response["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]
            obj_long, obj_lat = geo_object["Point"]["pos"].split(' ')
            self.coords = [float(obj_long), float(obj_lat)]
            self.m = 14
            self.pt = f'{obj_long},{obj_lat},flag'

            self.get_adress()
            self.map_update()
        except Exception as e:
            self.adress_name.setText(f'Адрес: ')

    def reset(self):
        self.search_text.setText('')
        self.pt = ''
        self.adress_name.setText('Адрес:')
        self.map_update()

    def get_adress(self):
        server = 'http://geocode-maps.yandex.ru/1.x/'

        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": ','.join(list(map(str, self.coords))),
            "format": "json"}

        response = requests.get(server, params=geocoder_params)

        if response:
            try:
                json_response = response.json()
                toponym = \
                    json_response["response"]['GeoObjectCollection']["featureMember"][0]["GeoObject"][
                        "metaDataProperty"][
                        "GeocoderMetaData"]
                if self.postal_code:
                    toponym_adress = toponym['text']
                    toponym_post = \
                        toponym["AddressDetails"]["Country"]["AdministrativeArea"]["Locality"]["Thoroughfare"][
                            "Premise"][
                            "PostalCode"]["PostalCodeNumber"]
                    self.adress_name.setText(f'Адрес: {toponym_adress}, {toponym_post}')
                else:
                    toponym_adress = toponym['text']
                    self.adress_name.setText(f'Адрес: {toponym_adress}')
            except Exception:
                json_response = response.json()
                toponym = \
                    json_response["response"]['GeoObjectCollection']["featureMember"][0]["GeoObject"][
                        "metaDataProperty"][
                        "GeocoderMetaData"]
                toponym_adress = toponym['text']
                self.adress_name.setText(f'Адрес: {toponym_adress}')
        else:
            print("Ошибка выполнения запроса")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

    def check_post(self):
        if self.check_postal.checkState() == 2:
            self.postal_code = True
        else:
            self.postal_code = False
        self.map_update()

    def static_map_request(self):
        server = "http://static-maps.yandex.ru/1.x/"
        map_params = {
            "ll": ','.join(list(map(str, self.coords))),
            "l": self.l_map,
            'z': str(self.m),
            'pt': self.pt
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
