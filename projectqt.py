import csv
import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QTableWidget, QLineEdit, QLabel, QPushButton


class SignedIn(Exception):
    pass


class CardNum(Exception):
    pass


class LenError(Exception):
    pass


class PasswordError(Exception):
    pass


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('project_d.ui', self)
        self.initUi()

    def loadTable(self, data):
        self.count = 1
        self.table = []
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(data):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setHorizontalHeaderLabels(['Название', 'Цена'])

    def initUi(self):
        self.flag = False
        self.cart_list = []
        self.pushButton_2.clicked.connect(self.categories)
        self.pushButton_11.clicked.connect(self.categories)
        self.pushButton_3.clicked.connect(self.categories)
        self.pushButton_4.clicked.connect(self.categories)
        self.pushButton_5.clicked.connect(self.categories)
        self.pushButton.clicked.connect(self.categories)
        self.pushButton_6.clicked.connect(self.categories)
        self.pushButton_10.clicked.connect(self.categories)
        self.pushButton_13.clicked.connect(self.categories)

        self.pushButton_9.clicked.connect(self.sign_up)
        self.pushButton_8.clicked.connect(self.sign_in)
        self.pushButton_15.clicked.connect(self.cart)
        self.pushButton_7.clicked.connect(self.search)
        self.pushButton_12.clicked.connect(self.add_to_cart)
        self.pushButton_14.clicked.connect(self.clear_filters)
        self.pushButton_16.clicked.connect(self.order)
        self.pushButton_12.setEnabled(False)
        self.pushButton_14.setEnabled(False)
        self.con = sqlite3.connect('market 12.57.26.db')
        cur = self.con.cursor()
        result = cur.execute(f"""SELECT DISTINCT goods.title, goods.price FROM goods ORDER BY goods.title""").fetchall()
        data = []
        for elem in result:
            data.append(elem)
        self.loadTable(data)
        if self.tableWidget.itemClicked:
            self.pushButton_12.setEnabled(True)

    def luhn_algorithm(self, card):
        odd = map(lambda x: self.double(int(x)), card[::2])
        even = map(int, card[1::2])
        return (sum(odd) + sum(even)) % 10 == 0

    def double(self, x):
        res = x * 2
        if res > 9:
            res = res - 9
        return res

    def check_password(self, password):
        if not password.isdigit() and not password.isalpha():
            return True
        elif len(password) < 8:
            return 'len'
        elif password.isdigit() or password.isalpha():
            return 'format'

    def sign_up(self):
        try:
            if not self.flag:
                name, ok_pressed = QInputDialog.getText(self, "Введите данные", "Ваше имя")
                if ok_pressed:
                    self.name = name
                num, ok_pressed = QInputDialog.getText(self, "Введите данные", "Ваш номер телефона")
                if ok_pressed:
                    self.num = int(num)
                address, ok_pressed = QInputDialog.getText(self, "Введите данные", "Ваш адрес")
                if ok_pressed:
                    self.address = address
                password, ok_pressed = QInputDialog.getText(self, "Придумайте пароль", "Пароль")
                if ok_pressed:
                    if self.check_password(password):
                        self.password = password
                cur = self.con.cursor()
                result = cur.execute(f"""SELECT id FROM customers""").fetchall()
                if result:
                    self.id = int(result[-1][0]) + 1
                else:
                    self.id = 1
                cur = self.con.cursor()
                cur.execute(f"""INSERT INTO customers 
                VALUES({self.id}, '{self.name}', {self.num}, '{self.address}', '{self.password}')""")
                self.con.commit()
                self.flag = True
                self.pushButton_8.setText(f'{self.name} [Выйти]')
            else:
                self.name = ''
                self.num = 0
                self.email = ''
                self.flag = False
                self.pushButton_8.setText('Войти')
            self.message = QMessageBox(self)
            self.message.setText("Успешно!")
            self.message.exec()
        except LenError:
            self.message = QMessageBox(self)
            self.message.setText("Пароль должен содержать не менее 8 символов")
            self.message.exec()
        except PasswordError:
            self.message = QMessageBox(self)
            self.message.setText("Пароль должен содержать и буквы, и цифры")
            self.message.exec()
        except Exception:
            self.message = QMessageBox(self)
            self.message.setText("Неверный формат")
            self.message.exec()

    def sign_in(self):
        try:
            if not self.flag:
                name, ok_pressed = QInputDialog.getText(self, "Введите данные", "Ваше имя")
                if ok_pressed:
                    self.name = name
                num, ok_pressed = QInputDialog.getText(self, "Введите данные", "Ваш номер телефона")
                if ok_pressed:
                    self.num = num
                address, ok_pressed = QInputDialog.getText(self, "Введите данные", "Ваш адрес")
                if ok_pressed:
                    self.address = address
                password, ok_pressed = QInputDialog.getText(self, "Введите пароль", "Пароль")
                if ok_pressed:
                    self.password = password
                cur = self.con.cursor()
                result = cur.execute(f"""SELECT id from customers WHERE name='{self.name}' 
                AND phone_number={self.num} 
                AND address='{self.address}' AND password='{self.password}'""").fetchall()
                if not result:
                    raise Exception
                self.flag = True
                self.id = result[0]
                self.pushButton_8.setText(f'{self.name} [Выйти]')
                self.pushButton_9.setEnabled(False)
            else:
                self.name = ''
                self.num = 0
                self.email = ''
                self.flag = False
                self.pushButton_8.setText('Войти')
            self.message = QMessageBox(self)
            self.message.setText("Успешно!")
            self.message.exec()
        except Exception:
            self.message = QMessageBox(self)
            self.message.setText("Неверный формат или неверные данные")
            self.message.exec()

    def total_price(self):
        total_price = 0
        for elem in self.cart_list:
            cur = self.con.cursor()
            result = cur.execute(f"""SELECT price from goods WHERE title='{elem[0]}'""").fetchall()
            total_price += int(result[0][0])
        return total_price

    def cart(self):
        if self.cart_list:
            self.message = QMessageBox(self)
            total_price = self.total_price()
            self.message_list = [' - '.join(elem) for elem in self.cart_list]
            self.message_text = '\n'.join(self.message_list)
            self.message.setText(f"В корзине: \n{self.message_text}\nИтого: {total_price}")
            self.message.exec()

    def search(self):
        cur = self.con.cursor()
        result = cur.execute(f"""SELECT
            goods.title, goods.price
        FROM
            goods
        WHERE goods.title LIKE '%{self.lineEdit.text().lower()}%' or 
        goods.title LIKE '%{self.lineEdit.text().capitalize()}%'
        ORDER BY goods.title""").fetchall()
        self.tableWidget.clear()
        self.loadTable(result)
        self.pushButton_14.setEnabled(True)

    def add_to_cart(self):
        num, ok_pressed = QInputDialog.getInt(self, "Введите количество", "Количество", 1)
        if ok_pressed:
            for elem in self.tableWidget.selectedItems():
                self.cart_list.append((elem.text(), str(num)))

    def categories(self):
        cur = self.con.cursor()
        result = cur.execute(f"""SELECT goods.title, goods.price FROM goods WHERE category_id in (SELECT id from categories
         WHERE title in ('{self.sender().text()}')) 
        ORDER BY goods.title""").fetchall()
        self.tableWidget.clear()
        self.loadTable(result)
        self.pushButton_14.setEnabled(True)

    def clear_filters(self):
        self.tableWidget.clear()
        cur = self.con.cursor()
        result = cur.execute(f"""SELECT DISTINCT goods.title, goods.price FROM goods ORDER BY goods.title""").fetchall()
        self.loadTable(result)
        self.pushButton_14.setEnabled(False)

    def order(self):
        try:
            if not self.flag:
                raise SignedIn
            total_price = 0
            for elem in self.cart_list:
                cur = self.con.cursor()
                result = cur.execute(f"""SELECT price from goods WHERE title='{elem[0]}'""").fetchall()
                total_price += int(result[0][0])
            payment, ok_pressed = QInputDialog.getItem(self, "Выберите способ оплаты", f"Сумма заказа: {total_price}",
                                                       ('Наличными', 'Банковской картой'))
            if ok_pressed:
                self.payment = payment
            if self.payment == 'Банковской картой':
                card_num, ok_pressed = QInputDialog.getText(self, "Введите номер карты",
                                                           "Номер карты")
                if ok_pressed:
                    if not self.luhn_algorithm(card_num):
                        raise CardNum
            cur = self.con.cursor()
            result = cur.execute(f"""SELECT id FROM orders""").fetchall()
            if result:
                self.order_id = result[-1][0] + 1
            else:
                self.order_id = 1
            with open(f'order{self.count}.csv', 'w', newline='', encoding="utf8") as file:
                writer = csv.writer(
                    file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(['Название', 'Цена'])
                for elem in self.cart_list:
                    writer.writerow(elem)
                total_price = self.total_price()
                writer.writerow(['Итого', f'{total_price}'])
            with open(f'order{self.count}.csv', 'r', newline='', encoding="utf8") as file:
                data = list(csv.reader(file, delimiter=';', quotechar='"'))
                new_list = ' '.join([';'.join(line) for line in data[1:-1]])
                cur = self.con.cursor()
                cur.execute(f"""INSERT INTO orders 
                    VALUES({int(self.order_id)}, '{new_list}', {int(self.id[0])}, {total_price})""")
                self.con.commit()
                self.count += 1
                self.cart_list = []
                self.message = QMessageBox(self)
                self.message.setText("Заказ оформлен")
                self.message.exec()
        except SignedIn:
            self.message = QMessageBox(self)
            self.message.setText("Для оформления заказа необходимо зарегистрироваться")
            self.message.exec()
        except CardNum:
            self.message = QMessageBox(self)
            self.message.setText("Неверные данные")
            self.message.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
