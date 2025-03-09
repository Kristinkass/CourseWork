import mysql.connector, pymysql
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Цветkoff')
        self.setMinimumSize(1200, 900)
        self.resize(1200, 900)

        self.actor = None  # Роль пользователя (продавец/администратор)
        self.seller_id = None  # ID продавца

        self.setStyleSheet("""
            QPushButton { height: 50px; font-size: 16px; }
            QLabel { font-size: 52px; font-family: Arial; }
            QLineEdit { font-size: 16px; height: 50px; }
        """)
        self.show_initial_window()

    def show_initial_window(self):
        """Создание начального окна с кнопками Вход и Регистрация"""
        layout = QVBoxLayout()

        title_label = QLabel('Цветkoff')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 48px; font-weight: bold;")
        layout.addWidget(title_label)

        self.login_button = QPushButton('Вход')
        self.login_button.setMinimumSize(200, 50)
        self.login_button.clicked.connect(self.show_login_window)
        layout.addWidget(self.login_button, alignment=Qt.AlignCenter)

        self.register_button = QPushButton('Регистрация')
        self.register_button.setMinimumSize(200, 50)
        self.register_button.clicked.connect(self.show_register_window)
        layout.addWidget(self.register_button, alignment=Qt.AlignCenter)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.show()  # Гарантируем, что окно обновится

    def show_login_window(self):
        """Окно входа с полями для логина и пароля"""
        layout = QVBoxLayout()

        login_title = QLabel('Вход')
        login_title.setAlignment(Qt.AlignCenter)
        login_title.setStyleSheet("font-size: 36px; font-weight: bold;")
        layout.addWidget(login_title)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText('Логин')
        layout.addWidget(self.login_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Пароль')
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_action_button = QPushButton('Войти')
        self.login_action_button.clicked.connect(self.login)
        layout.addWidget(self.login_action_button)

        self.back_button = QPushButton('Назад')
        self.back_button.clicked.connect(self.show_initial_window)
        layout.addWidget(self.back_button)

        login_widget = QWidget()
        login_widget.setLayout(layout)
        self.setCentralWidget(login_widget)

    def show_register_window(self):
        """Окно регистрации пользователя"""
        layout = QVBoxLayout()

        title_label = QLabel('Регистрация')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 36px; font-weight: bold;")
        layout.addWidget(title_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('ФИО')
        layout.addWidget(self.name_input)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText('Логин')
        layout.addWidget(self.login_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Пароль')
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.shop_input = QLineEdit()
        self.shop_input.setPlaceholderText('№ Магазина')
        layout.addWidget(self.shop_input)

        register_button = QPushButton('Зарегистрироваться')
        register_button.clicked.connect(self.register_user)
        layout.addWidget(register_button)

        back_button = QPushButton('Назад')
        back_button.clicked.connect(self.show_initial_window)
        layout.addWidget(back_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def register_user(self):
        """Регистрация пользователя в базе данных"""
        name = self.name_input.text().strip()
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()
        shop_id = self.shop_input.text().strip()
        id_pdv = self._input.text().strip()

        # Проверка на пустые поля
        if not (name and login and password and shop_id):
            self.show_message('Ошибка', 'Все поля обязательны для заполнения!')
            return

        # Проверка длины строк
        if len(name) > 255:
            self.show_message('Ошибка', 'ФИО должно быть не длиннее 255 символов.')
            return
        if len(login) > 45:
            self.show_message('Ошибка', 'Логин должен быть не длиннее 45 символов.')
            return
        if len(password) > 10:
            self.show_message('Ошибка', 'Пароль должен быть не длиннее 10 символов.')
            return

        # Проверка, что shop_id является целым числом
        try:
            shop_id = int(shop_id)
        except ValueError:
            self.show_message('Ошибка', 'Номер магазина должен быть целым числом.')
            return

        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user='root',
                password='Cstud161620',
                database='flowersh',
                autocommit=True
            )

            cursor = conn.cursor()

            # Проверка уникальности логина (без учета регистра)
            cursor.execute("SELECT 1 FROM seller WHERE LOWER(login) = LOWER(%s)", (login,))
            if cursor.fetchone():
                self.show_message('Ошибка', 'Пользователь с таким логином уже существует!')
                return

            # Проверка существования магазина
            cursor.execute("SELECT 1 FROM shop WHERE id_shopa = %s", (shop_id,))
            if not cursor.fetchone():
                self.show_message('Ошибка', 'Магазин с указанным номером не существует!')
                return

            # Регистрация пользователя
            cursor.execute("""
                INSERT INTO seller (famio, login, password, id_mg, actor)
                VALUES (%s, %s, %s, %s, 'Продавец')
            """, (name, login, password, shop_id))

            self.show_message('Успех', 'Регистрация прошла успешно!')
            self.show_initial_window()  # Возвращаем пользователя на экран входа

        except mysql.connector.Error as err:
            self.show_message('Ошибка', f'Ошибка базы данных: {err}')

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def login(self):
        """Проверка логина и пароля с использованием базы данных MySQL"""
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        # Проверка на пустые поля
        if not login or not password:
            self.show_message("Ошибка", "Пожалуйста, введите логин и пароль.")
            return

        # Проверка длины строк
        if len(login) > 45:
            self.show_message("Ошибка", "Логин должен быть не длиннее 45 символов.")
            return
        if len(password) > 10:
            self.show_message("Ошибка", "Пароль должен быть не длиннее 10 символов.")
            return

        try:
            # Подключение к базе данных
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user='root',
                password='Cstud161620',
                database='flowersh'
            )
            cursor = conn.cursor()

            # Получаем данные о продавце, включая его id_pdv
            cursor.execute("SELECT id_pdv, actor FROM seller WHERE login = %s AND password = %s", (login, password))
            result = cursor.fetchone()

            if result:
                self.seller_id = result[0]  # Сохраняем id_pdv продавца
                self.actor = result[1].lower()  # Сохраняем роль
                self.close()  # Закрываем окно входа
            else:
                self.show_message("Ошибка", "Неверные данные")

        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Ошибка базы данных: {err}")

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def show_message(self, title, message):
        """Показывает сообщение пользователю"""
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def closeEvent(self, event):
        """Закрытие программы при закрытии окна"""
        if self.actor is None:  # Если пользователь не вошел
            QApplication.quit()  # Завершаем приложение
        event.accept()  # Корректное завершение без ошибок


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    if window.actor is not None:  # Показываем главное окно только если роль определена
        window.show()
    app.exec_()
