import mysql.connector, sys, re
from fpdf import FPDF
from datetime import datetime
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QComboBox, QHBoxLayout, QWidget, QSplitter,
    QLabel, QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem, QRadioButton, QButtonGroup,
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QTableWidget, QTableWidgetItem,
    QRadioButton, QButtonGroup, QHeaderView
)
from PyQt5.QtCore import Qt
from Entry import MainWindow


def get_db_connection():
    """Быстрое подключение к базе данных"""
    return mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='Cstud161620',
        database='flowersh'
    )
def get_next_id(table_name, id_column):
    """Возвращает следующий доступный ID для указанной таблицы и столбца."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT MAX({id_column}) FROM {table_name}")
        max_id = cursor.fetchone()[0]
        return (max_id + 1) if max_id is not None else 1
    except mysql.connector.Error as err:
        print(f"Ошибка при получении следующего ID: {err}")
        return 1
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def validate_datetime(date_str):
    """Проверяет, соответствует ли строка формату 'YYYY-MM-DD HH:MM:SS'."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        return False
def validate_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def validate_decimal(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def validate_string(value, max_length):
    return isinstance(value, str) and len(value) <= max_length

class FlowerShop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Цветкoff')
        self.setMinimumSize(1200, 900)
        self.resize(1200, 900)
        self.actor = None # Переменная для хранения роли
        self.seller_id = None
        self.login()
        self.content_widget = None  # Инициализация виджета
        self.active_button = None  # Храним активную кнопку
        self.init_main_window()

    def login(self):
        login_window = MainWindow()
        login_window.show()
        app = QApplication.instance()  # Получаем экземпляр приложения PyQt
        app.exec_()  # Запускаем цикл обработки событий для окна входа

        self.actor = login_window.actor  # Получаем роль пользователя
        self.seller_id = login_window.seller_id  # Получаем id продавца

        if self.actor is None:
            QApplication.quit()
            login_window.close()  # Закрываем окно входа

    def init_main_window(self):
        """Создаёт главное окно в зависимости от роли пользователя"""
        if self.content_widget is None:
            self.content_widget = QWidget()  # Инициализация, если не была создана ранее

        """Создаёт главное окно в зависимости от роли пользователя"""
        # Инициализация кнопок
        self.catalog_button = QPushButton('Каталог')
        self.catalog_button.clicked.connect(lambda: self.show_section("Каталог"))

        self.cart_button = QPushButton('Корзина')
        self.cart_button.clicked.connect(lambda: self.show_section("Корзина"))

        # Новые кнопки для разделов
        self.sell_button = QPushButton('Продажи')
        self.sell_button.clicked.connect(lambda: self.show_section("Продажи"))

        self.management_button = QPushButton('Магазин')
        self.management_button.clicked.connect(lambda: self.show_section("Магазин"))

        self.client_button = QPushButton('Продавцы')
        self.client_button.clicked.connect(lambda: self.show_section("Продавцы"))

        self.post_button = QPushButton('Поставки')
        self.post_button.clicked.connect(lambda: self.show_section("Поставки"))

        self.psh_button = QPushButton('Поставщики')
        self.psh_button.clicked.connect(lambda: self.show_section("Поставщики"))

        self.report_button = QPushButton('Отчет')
        self.report_button.clicked.connect(lambda: self.show_section("Отчет"))

        # Улучшаем стиль интерфейса
        self.setStyleSheet("""
            QPushButton { height: 50px; font-size: 18px; }
            QLabel { font-size: 24px; font-weight: bold; }
            QTableWidget { font-size: 16px; }
        """)

        # Создание вертикального макета для кнопок
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.catalog_button)
        # button_layout.addWidget(self.cart_button)
        button_layout.addWidget(self.sell_button)

        if self.actor == 'продавец':
            button_layout.addWidget(self.cart_button)
        if self.actor == 'администратор':
            button_layout.addWidget(self.management_button)
            button_layout.addWidget(self.client_button)
            button_layout.addWidget(self.post_button)
            button_layout.addWidget(self.psh_button)
            button_layout.addWidget(self.report_button)
        if self.actor is None:  # Если роль не определена, завершаем программу
            QApplication.quit()
            return
        button_layout.addStretch()

        # Контейнер с кнопками разделов
        self.section_button_widget = QWidget()
        self.section_button_widget.setLayout(button_layout)
        self.section_button_widget.setFixedWidth(200)

        # Основной сплиттер для разделения кнопок разделов и содержимого
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.addWidget(self.section_button_widget)

        self.main_splitter.addWidget(self.content_widget)

        # Создание заголовка раздела
        self.section_title_label = QLabel("")
        self.section_title_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #333;")
        self.section_title_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Добавление заголовка сверху
        top_layout = QVBoxLayout()
        top_layout.addWidget(self.section_title_label)
        self.content_widget.setLayout(top_layout)

        self.main_splitter.setSizes([200, 1720])
        self.setCentralWidget(self.main_splitter)

    def show_section(self, section_name):
        """Показывает выбранный раздел и обновляет заголовок"""
        self.section_title_label.setText(section_name)  # Обновление заголовка

        section_methods = {
            "Каталог": self.show_catalog_table,
            "Магазин": self.show_management_table,
            "Продавцы": self.show_clients_table,
            "Поставки": self.show_post_table,
            "Поставщики": self.show_suppliers_table,
            "Корзина": self.show_cart_table,
            "Продажи": self.show_sales_table,
            "Отчет": self.show_report_section
        }

        if section_name in section_methods:
            section_methods[section_name]()


    def show_cart_table(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            self.section_title_label.setText("Корзина")
            cursor.execute("""
                SELECT c.cart_id, c.tov_id, k.name, c.quantity, k.cena, k.shop
                FROM cart AS c
                JOIN catalog AS k ON c.tov_id = k.id_tov
            """)
            rows = cursor.fetchall()

            # Основная таблица корзины
            table = QTableWidget()
            table.setColumnCount(7)  # Добавлен 7-й столбец для кнопки удаления
            table.setHorizontalHeaderLabels([
                "Корзина", "Товар", "Наименование", "Количество", "Цена x1", "Магазин", "Удалить"
            ])

            if not rows:
                table.setRowCount(0)
            else:
                table.setRowCount(len(rows))
                for i, row in enumerate(rows):
                    table.setItem(i, 0, QTableWidgetItem(str(row[0])))  # cart_id
                    table.setItem(i, 1, QTableWidgetItem(str(row[1])))  # Товар ID
                    table.setItem(i, 2, QTableWidgetItem(row[2]))  # Наименование
                    table.setItem(i, 3, QTableWidgetItem(str(row[3])))  # Количество
                    table.setItem(i, 4, QTableWidgetItem(str(row[4])))  # Цена
                    table.setItem(i, 5, QTableWidgetItem(str(row[5])))  # Магазин

                    # Делаем поля (кроме количества) нередактируемыми
                    for col in range(table.columnCount() - 1):
                        if col != 3:
                            item = table.item(i, col)
                            if item:
                                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

                    # Кнопка удаления
                    btn = QPushButton("×")
                    btn.setStyleSheet("font-size: 18px; color: red; border: none")
                    btn.clicked.connect(lambda _, r=i: self.remove_cart_item(table, r))

                    cell_widget = QWidget()
                    layout = QHBoxLayout(cell_widget)
                    layout.addWidget(btn)
                    layout.setAlignment(Qt.AlignCenter)
                    layout.setContentsMargins(0, 0, 0, 0)
                    cell_widget.setLayout(layout)

                    table.setCellWidget(i, 6, cell_widget)

            # Прячем колонку с ID корзины
            table.hideColumn(0)
            table.setStyleSheet("font-size: 16px;")

            # Устанавливаем фиксированную ширину для столбца удаления
            table.setColumnWidth(6, 50)

            # Автоматический размер для остальных столбцов
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            table.cellChanged.connect(lambda row, column: self.on_quantity_changed(row, column, table))

            clear_button = QPushButton("Очистить")
            clear_button.clicked.connect(lambda: self.clear_cart(table))

            pay_button = QPushButton("Оплата")
            pay_button.clicked.connect(self.pay_for_items)

            button_layout = QHBoxLayout()
            button_layout.addWidget(clear_button)
            button_layout.addWidget(pay_button)

            layout = QVBoxLayout()
            layout.addWidget(self.section_title_label)
            layout.addWidget(table)
            layout.addLayout(button_layout)
            container = QWidget()
            container.setLayout(layout)

            if not rows:
                clear_button.setEnabled(False)
                pay_button.setEnabled(False)
            else:
                clear_button.setEnabled(True)
                pay_button.setEnabled(True)

            self.main_splitter.replaceWidget(1, container)
            self.content_widget = container

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Не удалось загрузить данные корзины: {err}")


    def remove_cart_item(self, table, row):
        """Удаляет запись из корзины по cart_id"""
        cart_id = int(table.item(row, 0).text())  # Получаем cart_id из скрытого столбца
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cart WHERE cart_id = %s", (cart_id,))
            conn.commit()
            self.show_cart_table()  # Обновляем таблицу
        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Ошибка удаления: {err}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def clear_cart(self, table):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cart")
            conn.commit()
            self.show_cart_table()
        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Ошибка очистки: {err}")

    def on_quantity_changed(self, row, column, table):
        """Обновляет количество товара в корзине при изменении значения в таблице"""
        try:
            if column != 3:  # Проверяем, что изменяется именно столбец "Количество"
                return

            cart_id = int(table.item(row, 0).text())  # ID корзины
            new_quantity = int(table.item(row, 3).text())  # Новое количество
            tov_id = int(table.item(row, 1).text())  # ID товара

            conn = get_db_connection()
            cursor = conn.cursor()

            # Получаем доступное количество товара в каталоге
            cursor.execute("SELECT col FROM catalog WHERE id_tov = %s", (tov_id,))
            available_quantity = cursor.fetchone()[0]

            if new_quantity > available_quantity:
                self.show_message("Ошибка", f"Недостаточно товара в каталоге. Доступно: {available_quantity}")
                table.item(row, 3).setText(str(available_quantity))  # Устанавливаем максимальное доступное количество
                return

            # Обновляем количество в корзине
            cursor.execute("UPDATE cart SET quantity = %s WHERE cart_id = %s", (new_quantity, cart_id))
            conn.commit()

            cursor.close()
            conn.close()

        except ValueError as e:
            self.show_message("Ошибка", f"Некорректное значение количества: {e}")
        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Не удалось обновить количество товара: {err}")
        except Exception as e:
            self.show_message("Ошибка", f"Неизвестная ошибка: {e}")

    def add_to_cart_from_table(self, table):
        """Добавляет выбранные товары в корзину с количеством 0"""

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            for row in range(table.rowCount()):
                checkbox_item = table.item(row, 0)
                if checkbox_item.checkState() == Qt.Checked:  # Если флажок установлен
                    tov_id = int(table.item(row, 1).text())  # Получаем ID товара
                    shop_id = int(table.item(row, 6).text())  # Получаем ID магазина

                    # Проверка, есть ли товар уже в корзине
                    cursor.execute("SELECT cart_id FROM cart WHERE tov_id = %s AND shop_id = %s", (tov_id, shop_id))
                    if not cursor.fetchone():
                        cursor.execute("INSERT INTO cart (tov_id, quantity, shop_id) VALUES (%s, %s, %s)",
                                       (tov_id, 0, shop_id))
                        conn.commit()

            cursor.close()
            conn.close()

            self.show_cart_table()
        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Не удалось добавить товар в корзину: {err}")

    def pay_for_items(self):
        """Проводит оплату товаров в корзине и переносит их в раздел продаж"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Получение данных корзины
            cursor.execute("""
                SELECT c.tov_id, c.quantity, k.name, k.cena, c.shop_id
                FROM cart AS c
                JOIN catalog AS k ON c.tov_id = k.id_tov AND c.shop_id = k.shop
            """)
            rows = cursor.fetchall()

            for row in rows:
                tov_id, quantity, name, cena, shop_id = row

                # Проверка доступного количества товара в каталоге
                cursor.execute("SELECT col FROM catalog WHERE id_tov = %s AND shop = %s", (tov_id, shop_id))
                available_quantity = cursor.fetchone()[0]

                if quantity > available_quantity:
                    self.show_message("Ошибка",
                                      f"Недостаточно товара в каталоге для {name}. Доступно: {available_quantity}")
                    return

                # Проверка количества
                if quantity <= 0:
                    self.show_message("Ошибка", f"Некорректное количество для товара: {name}.")
                    return

                # Вычитание из каталога
                cursor.execute("""
                    UPDATE catalog SET col = col - %s 
                    WHERE id_tov = %s AND shop = %s
                """, (quantity, tov_id, shop_id))

                # Перенос в продажи с сохранением seller_id
                cursor.execute("""
                    INSERT INTO sale (tov_id, quantity, cena, sale_date, shop_id, seller_id)
                    VALUES (%s, %s, %s, NOW(), %s, %s)
                """, (tov_id, quantity, cena * quantity, shop_id, self.seller_id))

            # Очистка корзины
            cursor.execute("DELETE FROM cart")
            conn.commit()

            # После оплаты переходим в раздел "Продажи"
            self.show_sales_table()
            self.section_title_label.setText("Продажи")

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            self.show_message("Ошибка БД", f"Ошибка: {err}")

            if conn.is_connected():
                conn.rollback()

        except Exception as e:
            self.show_message("Ошибка", f"Неизвестная ошибка: {e}")

        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def on_quantity_changed(self, row, column, table):
        """Обновляет количество товара в корзине при изменении значения в таблице"""
        try:
            # Проверяем, что изменяется именно столбец "Количество" (столбец 3)
            if column != 3:
                return

            cart_id = int(table.item(row, 0).text())
            quantity = int(table.item(row, 3).text())
            tov_id = int(table.item(row, 1).text())  # ID товара

            conn = get_db_connection()
            cursor = conn.cursor()

            # Получаем доступное количество товара в каталоге
            cursor.execute("SELECT col FROM catalog WHERE id_tov = %s", (tov_id,))
            available_quantity = cursor.fetchone()[0]

            if quantity > available_quantity:
                self.show_message("Ошибка", f"Недостаточно товара в каталоге. Доступно: {available_quantity}")
                table.item(row, 3).setText(str(available_quantity))  # Устанавливаем максимальное доступное количество
                return

            # Обновляем количество в корзине
            cursor.execute("UPDATE cart SET quantity = %s WHERE cart_id = %s", (quantity, cart_id))
            conn.commit()

            cursor.close()
            conn.close()

        except ValueError as e:
            self.show_message("Ошибка", f"Некорректное значение количества: {e}")
        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Не удалось обновить количество товара: {err}")
        except Exception as e:
            self.show_message("Ошибка", f"Неизвестная ошибка: {e}")


    def show_management_table(self):
        """Отображает таблицу управления магазинами"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            self.section_title_label.setText("Магазин")
            cursor.execute("SELECT name_m, adres_m, id_shopa, tel_m, dat_sozd FROM shop")
            rows = cursor.fetchall()

            table = QTableWidget()
            table.setColumnCount(6)  # Добавляем столбец для флажков
            table.setHorizontalHeaderLabels([
                "", "Название", "Адрес", "№ Магазина", "Телефон", "Дата добавления"
            ])
            table.setRowCount(len(rows))

            for i, row in enumerate(rows):
                # Добавляем флажок
                checkbox_item = QTableWidgetItem()
                checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                checkbox_item.setCheckState(Qt.Unchecked)
                table.setItem(i, 0, checkbox_item)

                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Только для чтения по умолчанию
                    table.setItem(i, j + 1, item)  # Сдвигаем на один столбец из-за флажков

            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            #table.setStyleSheet("font-size: 16px;")

            # Кнопки для управления
            button_layout = QHBoxLayout()

            add_button = QPushButton("Добавить")
            add_button.clicked.connect(self.add_shop_record)
            button_layout.addWidget(add_button)

            edit_button = QPushButton("Редактировать")
            edit_button.clicked.connect(lambda: self.enable_shop_editing(table))
            button_layout.addWidget(edit_button)

            save_button = QPushButton("Сохранить")
            save_button.clicked.connect(lambda: self.save_shop_changes(table))
            button_layout.addWidget(save_button)

            delete_button = QPushButton("Удалить")
            delete_button.clicked.connect(lambda: self.delete_shop_record(table))
            button_layout.addWidget(delete_button)

            # Показываем кнопки только для администратора
            if self.actor != 'администратор':
                add_button.setVisible(False)
                edit_button.setVisible(False)
                save_button.setVisible(False)
                delete_button.setVisible(False)

            layout = QVBoxLayout()
            layout.addWidget(self.section_title_label)
            layout.addWidget(table)
            layout.addLayout(button_layout)
            container = QWidget()
            container.setLayout(layout)

            self.main_splitter.replaceWidget(1, container)
            self.content_widget = container

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Не удалось загрузить данные магазинов: {err}")


    def add_shop_record(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            next_id = get_next_id("shop", "id_shopa")
            cursor.execute("""
                    INSERT INTO shop (id_shopa, name_m, adres_m, tel_m, dat_sozd)
                    VALUES (%s, %s, %s, %s, CURDATE())
                """, (next_id, "Новый магазин", "Новый адрес", "+0 (000)-000-0000"))

            conn.commit()
            cursor.close()
            conn.close()

            self.show_management_table()  # Обновляем таблицу
            #self.show_message("Успех", "Магазин добавлен!")

        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Не удалось добавить магазин: {err}")

    def enable_shop_editing(self, table):
        for row in range(table.rowCount()):
            checkbox_item = table.item(row, 0)
            if checkbox_item.checkState() == Qt.Checked:
                for col in range(1, table.columnCount()):
                    if col == 4:  # Столбец телефона
                        line_edit = QLineEdit()
                        line_edit.setInputMask("+0 (000)-000-0000")
                        line_edit.setText(table.item(row, col).text())
                        table.setCellWidget(row, col, line_edit)
                    elif col == 3:  # Столбец с ID магазина
                        item = table.item(row, col)
                        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Запрещаем редактирование
                    else:
                        item = table.item(row, col)
                        item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)

    def save_shop_changes(self, table):
        """Сохраняет изменения в отмеченных строках."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Проверка на наличие отмеченных флажков
            has_checked = False
            for row in range(table.rowCount()):
                checkbox = table.item(row, 0)
                if checkbox.checkState() == Qt.Checked:
                    has_checked = True
                    break

            #if not has_checked:
                #self.show_message("Ошибка", "Не выбрано ни одной записи для сохранения.")
                #return

            for row in range(table.rowCount()):
                checkbox = table.item(row, 0)
                if checkbox.checkState() == Qt.Checked:  # Если флажок установлен
                    # Считываем значения из строки
                    name_m = table.item(row, 1).text()  # Название (без преобразования в нижний регистр)
                    adres_m = table.item(row, 2).text()  # Адрес (без преобразования в нижний регистр)
                    id_shopa = table.item(row, 3).text()  # ID магазина (число)
                    tel_m = table.cellWidget(row, 4).text()  # Телефон (из QLineEdit)

                    # Проверка формата телефона
                    if not self.validate_phone_number(tel_m):
                        self.show_message("Ошибка", "Введите номер телефона в формате: +0 (000)-000-0000.")
                        return

                    # Обновляем запись в базе данных
                    cursor.execute(f"""
                           UPDATE shop
                           SET name_m=%s, adres_m=%s, tel_m=%s
                           WHERE id_shopa=%s
                       """, (name_m, adres_m, tel_m, id_shopa))

                    # Снимаем флажок после сохранения
                    checkbox.setCheckState(Qt.Unchecked)

            conn.commit()
            self.show_management_table()  # Обновить таблицу

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Не удалось сохранить изменения: {err}")


    def delete_shop_record(self, table):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            for row in range(table.rowCount()):
                checkbox = table.item(row, 0)
                if checkbox.checkState() == Qt.Checked:
                    shop_id = table.item(row, 3).text()
                    cursor.execute("DELETE FROM shop WHERE id_shopa=%s", (shop_id,))
            conn.commit()
            self.show_management_table()
        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Ошибка удаления: {err}")

    def show_catalog_table(self):
        """Отображает таблицу каталога с флажками для выбора записей."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            self.section_title_label.setText("Каталог")
            # Если пользователь - продавец, фильтруем товары по его магазину
            if self.actor == 'продавец':
                # Получаем shop_id продавца из таблицы продавец
                cursor.execute("SELECT id_mg FROM seller WHERE id_pdv = %s", (self.seller_id,))
                shop_id = cursor.fetchone()[0]  # Получаем shop_id продавца

                # Фильтруем товары по shop_id
                cursor.execute("SELECT id_tov, name, article, cena, col, shop FROM catalog WHERE shop = %s", (shop_id,))

            else:
                cursor.execute("SELECT id_tov, name, article, cena, col, shop FROM catalog")
            rows = cursor.fetchall()

            table = QTableWidget()
            table.setColumnCount(7)  # Дополнительный столбец для флажков
            table.setHorizontalHeaderLabels([
                "", "№ Товара", "Наименование", "Артикул", "Цена", "Количество", "№ Магазина"
            ])
            table.setRowCount(len(rows))

            # Заполнение таблицы данными с флажками
            for i, row in enumerate(rows):
                # Добавляем флажок
                checkbox_item = QTableWidgetItem()
                checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                checkbox_item.setCheckState(Qt.Unchecked)
                table.setItem(i, 0, checkbox_item)

                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Только для чтения по умолчанию
                    table.setItem(i, j + 1, item)  # Сдвигаем на один столбец из-за флажков

            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            table.setStyleSheet("font-size: 16px;")
            table.itemChanged.connect(lambda item: self.disable_editing(item, table))
            # table.hideColumn(1)  # Скрывает столбец с ID товара (второй столбец)

            self.section_title_label.setText("Каталог")
            # Создаем кнопки для управления
            button_layout = QHBoxLayout()

            # Кнопка добавления
            add_button = QPushButton("Добавить")
            add_button.clicked.connect(lambda: self.add_record("catalog", table))
            button_layout.addWidget(add_button)

            # Кнопка редактирования
            edit_button = QPushButton("Редактировать")
            edit_button.clicked.connect(lambda: self.enable_editing(table))
            button_layout.addWidget(edit_button)

            # Кнопка сохранения изменений
            save_button = QPushButton("Сохранить")
            save_button.clicked.connect(lambda: self.save_changes("каталог", table))
            button_layout.addWidget(save_button)

            # Кнопка удаления
            delete_button = QPushButton("Удалить")
            delete_button.clicked.connect(lambda: self.delete_record("каталог", table))
            button_layout.addWidget(delete_button)
            # в корзину
            add_to_cart_button = QPushButton("В корзину")
            add_to_cart_button.clicked.connect(lambda: self.add_to_cart_from_table(table))
            button_layout.addWidget(add_to_cart_button)

            # Показываем кнопки только для администратора
            if self.actor != 'администратор':
                add_button.setVisible(False)
                edit_button.setVisible(False)
                save_button.setVisible(False)
                delete_button.setVisible(False)

            if self.actor != 'продавец':
                add_to_cart_button.setVisible(False)
                # Добавляем кнопку "В корзину" для продавца

            layout = QVBoxLayout()
            layout.addWidget(self.section_title_label)
            layout.addWidget(table)
            layout.addLayout(button_layout)

            container = QWidget()
            container.setLayout(layout)
            self.main_splitter.replaceWidget(1, container)

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Не удалось загрузить данные каталога: {err}")

    def disable_editing(self, item, table):
        """Отключает редактирование при снятии флажка"""
        if item.column() == 0:  # Если изменен флажок
            row = item.row()
            checkbox_item = table.item(row, 0)
            if checkbox_item.checkState() == Qt.Unchecked:  # Если флажок снят
                for col in range(1, table.columnCount()):  # Отключаем редактирование
                    item = table.item(row, col)
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    def enable_editing(self, table):
        """Включает редактирование отмеченных строк."""
        for row in range(table.rowCount()):
            checkbox_item = table.item(row, 0)
            if checkbox_item.checkState() == Qt.Checked:  # Если флажок установлен
                for col in range(1, table.columnCount()):  # Разрешаем редактирование со 2-го столбца
                    item = table.item(row, col)
                    item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)

    def add_record(self, table_name, table):
        """Добавление новой записи в таблицу"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Проверка существования магазина по умолчанию
            cursor.execute("SELECT id_shopa FROM shop WHERE id_shopa = 1")
            if not cursor.fetchone():
                self.show_message("Ошибка", "Сначала создайте магазин!")
                return

            # Получаем следующий ID для товара
            next_id = get_next_id("catalog", "id_tov")
            # Пример: добавление пустой строки с заполнением через форму
            cursor.execute(f"INSERT INTO {table_name} (id_tov, name, article, cena, col, shop) VALUES (%s,%s, %s, %s, %s, %s)",
                           (next_id,"Новый товар", "0000", 0.00, 0, 1))
            conn.commit()

            #self.show_message("Успех", "Новая запись добавлена.")
            self.show_catalog_table()  # Обновить таблицу

            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Не удалось добавить запись: {err}")

    def validate_quantity(self, table):
        """Проверяет количество товара перед сохранением"""
        for row in range(table.rowCount()):
            quantity_item = table.item(row, 3)  # Количество товара
            if quantity_item is None or quantity_item.text().strip() == "":
                self.show_message("Ошибка", "Не должно быть пустых ячеек!")
                return False
            try:
                quantity = int(quantity_item.text())
                if quantity < 0:
                    self.show_message("Ошибка", "Введено отрицательное количество товара!")
                    return False
            except ValueError:
                self.show_message("Ошибка", "Некорректное значение количества!")
                return False
        return True

    def validate_not_empty(self, table):
        """Проверяет, чтобы в таблице не было пустых значений перед сохранением"""
        for row in range(table.rowCount()):
            for col in range(1, table.columnCount()):  # Пропускаем флажки
                item = table.item(row, col)
                if item is None or item.text().strip() == "":
                    self.show_message("Ошибка", "Не должно быть пустых ячеек!")
                    return False
        return True

    def validate_phone_number(self, phone):
        """Проверяет, соответствует ли номер телефона маске +0(000)-000-0000."""
        pattern = r"^\+\d\ \(\d{3}\)-\d{3}-\d{4}$"
        return re.match(pattern, phone) is not None

    def validate_shop_exists(self, shop_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id_shopa FROM shop WHERE id_shopa = %s", (shop_id,))
            return cursor.fetchone() is not None
        except mysql.connector.Error as err:
            return False
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def validate_unique_login(self, login):
        """Проверяет, чтобы логин продавца был уникальным"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM seller WHERE login = %s", (login,))
        if cursor.fetchone():
            self.show_message("Ошибка", "Продавец с таким логином уже существует!")
            cursor.close()
            conn.close()
            return False

        cursor.close()
        conn.close()
        return True


    def validate_date(value):
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def save_changes(self, section_name, table):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Проверка на наличие отмеченных флажков
            has_checked = False
            for row in range(table.rowCount()):
                if table.item(row, 0).checkState() == Qt.Checked:
                    has_checked = True
                    break

            #if not has_checked:
                #self.show_message("Ошибка", "Не выбрано ни одной записи для сохранения.")
                #return

            # Проверка на пустые значения в ячейках
            if not self.validate_not_empty(table):
                return

            # Проверка на корректность данных
            for row in range(table.rowCount()):
                if table.item(row, 0).checkState() == Qt.Checked:
                    # Проверка на целые числа
                    if not validate_int(table.item(row, 1).text()):  # ID товара
                        self.show_message("Ошибка", "Номер товара должно быть целым числом.")
                        return
                    if not validate_int(table.item(row, 5).text()):  # Количество
                        self.show_message("Ошибка", "Количество должно быть целым числом.")
                        return
                    if not validate_int(table.item(row, 6).text()):  # Магазин
                        self.show_message("Ошибка", "Номер магазина должно быть целым числом.")
                        return
                    if not validate_int(table.item(row, 3).text()):  # Магазин
                        self.show_message("Ошибка", "Артикул должен быть целым числом.")
                        return
                    # Проверка на десятичные числа
                    if not validate_decimal(table.item(row, 4).text()):  # Цена
                        self.show_message("Ошибка", "Используйте точку чтобы написать десятичное число.")
                        return
                    # Проверка существования магазина
                    def validate_shop_exists(shop_id):
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("SELECT id_shopa FROM shop WHERE id_shopa = %s", (shop_id,))
                            return cursor.fetchone() is not None
                        except mysql.connector.Error as err:
                            return False
                        finally:
                            if conn.is_connected():
                                cursor.close()
                                conn.close()

                    shop_id = int(table.item(row, 6).text())
                    if not validate_shop_exists(shop_id):
                        self.show_message("Ошибка", f"Магазин с номером {shop_id} не существует.")
                        return
                    # Обновляем запись
                    record_id = table.item(row, 1).text()
                    name = table.item(row, 2).text()
                    article = table.item(row, 3).text()
                    cena = float(table.item(row, 4).text())
                    col = int(table.item(row, 5).text())
                    shop = int(table.item(row, 6).text())

                    cursor.execute("""
                        UPDATE catalog
                        SET name=%s, article=%s, cena=%s, col=%s, shop=%s
                        WHERE id_tov=%s
                    """, (name, article, cena, col, shop, record_id))

                    # Снимаем флажок после сохранения
                    table.item(row, 0).setCheckState(Qt.Unchecked)

            conn.commit()
            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Ошибка сохранения: {err}")

    def show_sales_table(self):
        """Отображает таблицу продаж"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Запрос данных из таблицы "продажи" с дополнительными полями
            if self.actor == 'продавец':
                # Получаем shop_id продавца
                cursor.execute("SELECT id_mg FROM seller WHERE id_pdv = %s", (self.seller_id,))
                shop_id = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT p.sale_id, p.tov_id, k.name, p.quantity, p.cena, p.sale_date, m.id_shopa, s.famio
                    FROM sale AS p
                    JOIN catalog AS k ON p.tov_id = k.id_tov
                    JOIN shop AS m ON p.shop_id = m.id_shopa
                    JOIN seller AS s ON p.seller_id = s.id_pdv
                    WHERE p.shop_id = %s
                    ORDER BY p.sale_date ASC
                """, (shop_id,))
            else:
                cursor.execute("""
                    SELECT p.sale_id, p.tov_id, k.name, p.quantity, p.cena, p.sale_date, m.id_shopa, s.famio
                    FROM sale AS p
                    JOIN catalog AS k ON p.tov_id = k.id_tov
                    JOIN shop AS m ON p.shop_id = m.id_shopa
                    JOIN seller AS s ON p.seller_id = s.id_pdv
                    ORDER BY p.sale_date ASC
                """)

            rows = cursor.fetchall()

            # Создание таблицы
            table = QTableWidget()
            table.setColumnCount(8)  # Увеличиваем количество столбцов
            table.setHorizontalHeaderLabels([
                "Продажа", "Товар", "Наименование", "Количество", "Цена", "Дата оформления", "№ Магазина", "Продавец"
            ])
            table.setRowCount(len(rows))

            # Заполнение таблицы данными
            for i, row in enumerate(rows):
                table.setItem(i, 0, QTableWidgetItem(str(row[0])))  # Продажа ID
                table.setItem(i, 1, QTableWidgetItem(str(row[1])))  # Товар ID
                table.setItem(i, 2, QTableWidgetItem(row[2]))  # Наименование товара
                table.setItem(i, 3, QTableWidgetItem(str(row[3])))  # Количество
                table.setItem(i, 4, QTableWidgetItem(str(row[4])))  # Цена
                table.setItem(i, 5, QTableWidgetItem(str(row[5])))  # Дата
                table.setItem(i, 6, QTableWidgetItem(str(row[6])))  # Номер магазина
                table.setItem(i, 7, QTableWidgetItem(row[7]))  # ФИО продавца

            table.hideColumn(0)  # Скрываем столбец с ID продажи
            table.setStyleSheet("font-size: 16px;")
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            table.setEditTriggers(QTableWidget.NoEditTriggers)  # Блокирует редактирование

            if self.content_widget:
                self.content_widget.deleteLater()
            layout = QVBoxLayout()
            layout.addWidget(self.section_title_label)
            layout.addWidget(table)
            container = QWidget()
            container.setLayout(layout)

            self.main_splitter.replaceWidget(1, container)
            self.content_widget = container

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            self.show_message("Ошибка БД", f"Ошибка: {err}")


    def delete_record(self, table_name, table):
        """Удаляет отмеченные записи из таблицы и базы данных."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            for row in range(table.rowCount()):
                checkbox_item = table.item(row, 0)
                if checkbox_item.checkState() == Qt.Checked:  # Если флажок установлен
                    record_id = table.item(row, 1).text()  # ID товара
                    cursor.execute(f"DELETE FROM catalog WHERE id_tov = %s", (record_id,))

            conn.commit()
            self.show_catalog_table()  # Обновить таблицу

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Не удалось удалить записи: {err}")

    def show_report_section(self):
        main_layout = QVBoxLayout()

        # Заголовок
        self.section_title_label = QLabel("Отчет по доходам")
        self.section_title_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #333;")
        self.section_title_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Флажки для выбора отчета
        self.radio_group = QButtonGroup(self)
        self.income_radio = QRadioButton("Доход")
        self.expense_radio = QRadioButton("Расход")
        self.radio_group.addButton(self.income_radio)
        self.radio_group.addButton(self.expense_radio)
        self.income_radio.setChecked(True)

        self.income_radio.toggled.connect(self.update_report_table)
        self.expense_radio.toggled.connect(self.update_report_table)

        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.income_radio)
        radio_layout.addWidget(self.expense_radio)

        # Таблица
        self.report_table = QTableWidget()
        self.load_sales_data()  # Загружаем данные продаж по умолчанию

        # Кнопка сохранения
        save_btn = QPushButton("Сохранить в PDF")
        save_btn.clicked.connect(self.save_report_to_pdf)

        main_layout.addLayout(radio_layout)
        main_layout.addWidget(self.section_title_label)
        main_layout.addWidget(self.report_table)
        main_layout.addWidget(save_btn)

        container = QWidget()
        container.setLayout(main_layout)
        # Заменяем только содержимое правой части сплиттера
        self.main_splitter.replaceWidget(1, container)
        self.content_widget = container
        # self.setCentralWidget(container)

    def load_sales_data(self):
        """Загружает данные из таблицы продаж."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""SELECT p.tov_id, k.name, p.quantity, p.cena, p.sale_date, m.name_m, s.famio
                 FROM sale AS p
                 JOIN catalog AS k ON p.tov_id = k.id_tov
                 JOIN shop AS m ON p.shop_id = m.id_shopa
                 JOIN seller AS s ON p.seller_id = s.id_pdv
            """)
            rows = cursor.fetchall()

            self.update_table(rows,
                              ["№Товара", "Наименование", "Количество", "Сумма", "Дата продажи", "Магазин",
                               "Продавец"])
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Ошибка загрузки данных: {err}")

    def load_supply_data(self):
        """Загружает данные из таблицы поставок."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT tov_id, quantity, cena, supply_date FROM supply")
            rows = cursor.fetchall()

            self.update_table(rows, ["№Товара", "Количество", "Сумма", "Дата поставки"])
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Ошибка загрузки данных: {err}")

    def update_report_table(self):
        """Обновляет таблицу в зависимости от выбора флажка."""
        if self.income_radio.isChecked():
            self.section_title_label.setText("Отчет по доходам")
            self.load_sales_data()
        else:
            self.section_title_label.setText("Отчет по расходам")
            self.load_supply_data()

    def update_table(self, rows, headers):
        """Обновляет таблицу данными."""
        self.report_table.setColumnCount(len(headers))
        self.report_table.setHorizontalHeaderLabels(headers)
        self.report_table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                self.report_table.setItem(i, j, QTableWidgetItem(str(value)))

        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)


    def save_report_to_pdf(self):
        """Сохраняет отчет в PDF."""
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)

            headers = [self.report_table.horizontalHeaderItem(i).text() for i in range(self.report_table.columnCount())]
            data = [[self.report_table.item(row, col).text() if self.report_table.item(row, col) else "" for col in
                     range(self.report_table.columnCount())] for row in range(self.report_table.rowCount())]
            filename = "Отчет_доход.pdf" if self.income_radio.isChecked() else "Отчет_расход.pdf"

            pdf.set_font('DejaVu', '', 12)
            for header in headers:
                pdf.cell(40, 10, header, border=1, align='C')
            pdf.ln()

            pdf.set_font('DejaVu', '', 10)
            for row in data:
                for value in row:
                    pdf.cell(40, 10, value, border=1)
                pdf.ln()

            pdf.output(filename)
            self.show_message("Успех", f"Файл {filename} сохранен!")

        except Exception as e:
            self.show_message("Ошибка", f"Ошибка генерации PDF: {str(e)}")

    def show_suppliers_table(self):
        """Отображает таблицу поставщиков"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            self.section_title_label.setText("Поставщики")
            cursor.execute("SELECT org, FIO, id_post, tel FROM supplier")
            rows = cursor.fetchall()

            table = QTableWidget()
            table.setColumnCount(5)  # Добавляем столбец для флажков
            table.setHorizontalHeaderLabels([
                "", "Организация", "ФИО", "№ Поставщика", "Телефон"
            ])
            table.setRowCount(len(rows))

            for i, row in enumerate(rows):
                # Добавляем флажок
                checkbox_item = QTableWidgetItem()
                checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                checkbox_item.setCheckState(Qt.Unchecked)
                table.setItem(i, 0, checkbox_item)

                for j, value in enumerate(row):
                        item = QTableWidgetItem(str(value))
                        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # Только для чтения по умолчанию
                        table.setItem(i, j + 1, item)  # Сдвигаем на один столбец из-за флажков

            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            table.setStyleSheet("font-size: 16px;")
            # Кнопки для управления
            button_layout = QHBoxLayout()

            add_button = QPushButton("Добавить")
            add_button.clicked.connect(lambda: self.add_supplier_record("поставщик", table))
            button_layout.addWidget(add_button)

            edit_button = QPushButton("Редактировать")
            edit_button.clicked.connect(lambda: self.enable_sup_editing(table))
            button_layout.addWidget(edit_button)

            save_button = QPushButton("Сохранить")
            save_button.clicked.connect(lambda: self.save_supplier_changes(table))
            button_layout.addWidget(save_button)

            delete_button = QPushButton("Удалить")
            delete_button.clicked.connect(lambda: self.delete_supplier_record(table))
            button_layout.addWidget(delete_button)

            # Показываем кнопки только для администратора
            if self.actor != 'администратор':
                add_button.setVisible(False)
                edit_button.setVisible(False)
                save_button.setVisible(False)
                delete_button.setVisible(False)

            layout = QVBoxLayout()
            layout.addWidget(self.section_title_label)
            layout.addWidget(table)
            layout.addLayout(button_layout)
            container = QWidget()
            container.setLayout(layout)

            self.main_splitter.replaceWidget(1, container)
            self.content_widget = container

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Не удалось загрузить данные поставщиков: {err}")


    def add_supplier_record(self, table_name, table):
        """Добавляет новую запись поставщика в базу данных."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Получаем следующий ID для поставщика
            next_id = get_next_id("supplier", "id_post")
            # Добавляем запись с дефолтными значениями
            cursor.execute("""
                INSERT INTO supplier (id_post, org, FIO, tel)
                VALUES (%s, %s, %s, %s)
            """, (next_id, "Новая организация", "ФИО", "+0 (000)-000-0000"))

            conn.commit()  # Сохраняем изменения в базе данных

            # Обновляем таблицу после добавления записи
            self.show_suppliers_table()

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Ошибка добавления: {err}")

    def enable_sup_editing(self, table):
        """Разрешает редактирование всех столбцов, кроме ID поставщика."""
        for row in range(table.rowCount()):
            checkbox_item = table.item(row, 0)
            if checkbox_item.checkState() == Qt.Checked:
                # Разрешаем редактирование для всех столбцов, кроме ID поставщика
                for col in range(1, table.columnCount()):  # Пропускаем флажки
                    if col == 4:  # Столбец телефона
                        line_edit = QLineEdit()
                        line_edit.setInputMask("+0 (000)-000-0000")
                        line_edit.setText(table.item(row, col).text())
                        table.setCellWidget(row, col, line_edit)
                    else:
                        item = table.item(row, col)
                        if col == 3:  # Запрещаем редактирование ID поставщика
                            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                        else:
                            item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)
                            # Разрешаем ввод заглавных букв
                            if col == 1:  # Организация
                                item.setText(item.text().upper())
                            elif col == 2:  # ФИО
                                item.setText(item.text().upper())

    def save_supplier_changes(self, table):
        """Сохраняет изменения в отмеченных строках."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Проверка на наличие отмеченных флажков
            has_checked = False
            for row in range(table.rowCount()):
                checkbox_item = table.item(row, 0)
                if checkbox_item.checkState() == Qt.Checked:
                    has_checked = True
                    break

            #if not has_checked:
                #self.show_message("Ошибка", "Не выбрано ни одной записи для сохранения.")
                #return

            for row in range(table.rowCount()):
                checkbox_item = table.item(row, 0)
                if checkbox_item.checkState() == Qt.Checked:  # Если флажок установлен
                    supplier_id = table.item(row, 3).text()  # id_post
                    org = table.item(row, 1).text()  # Организация (строчные буквы)
                    fio = table.item(row, 2).text()  # ФИО (строчные буквы)
                    tel = table.cellWidget(row, 4).text()  # Телефон (из QLineEdit)

                    # Проверка формата телефона
                    if not self.validate_phone_number(tel):
                        self.show_message("Ошибка", "Введите номер телефона в формате: +0 (000)-000-0000.")
                        return

                    # Обновляем запись в базе данных
                    cursor.execute("""
                        UPDATE supplier 
                        SET org=%s, FIO=%s, tel=%s 
                        WHERE id_post=%s
                    """, (org, fio, tel, supplier_id))

                    # Снимаем флажок после сохранения
                    checkbox_item.setCheckState(Qt.Unchecked)

            conn.commit()
            self.show_suppliers_table()  # Обновить таблицу

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Не удалось сохранить изменения: {err}")


    def delete_supplier_record(self, table):
        """Удаляет отмеченные записи из таблицы и базы данных."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            for row in range(table.rowCount()):
                checkbox_item = table.item(row, 0)
                if checkbox_item.checkState() == Qt.Checked:
                    supplier_id = table.item(row, 3).text()  # id_post
                    cursor.execute("DELETE FROM supplier WHERE id_post = %s", (supplier_id,))

            conn.commit()
            self.show_suppliers_table()  # Обновить таблицу
            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Не удалось удалить записи: {err}")

    def create_supply_from_table(self, table):
        """Создает новую поставку на основе выбранного товара"""
        selected_items = table.selectionModel().selectedRows()
        if not selected_items:
            self.show_message("Ошибка", "Выберите товар для создания поставки.")
            return

        row = selected_items[0].row()
        tov_id = int(table.item(row, 0).text())  # Получаем ID товара
        shop_id = int(table.item(row, 5).text())  # Получаем ID магазина

        try:
            # Подключение к базе данных MySQL
            conn = get_db_connection()
            cursor = conn.cursor()

            # Получаем данные о товаре
            cursor.execute("SELECT name, article, cena FROM catalog WHERE id_tov = %s", (tov_id,))
            tov_data = cursor.fetchone()

            if not tov_data:
                self.show_message("Ошибка", "Товар не найден в каталоге.")
                return

            name, article, cena = tov_data

            # Получаем данные о поставщике (предположим, что поставщик выбирается вручную или автоматически)
            cursor.execute("SELECT id_post FROM supplier LIMIT 1")  # Пример: берем первого поставщика
            supplier_data = cursor.fetchone()

            if not supplier_data:
                self.show_message("Ошибка", "Нет доступных поставщиков.")
                return

            supplier_id = supplier_data[0]

            # Создаем новую поставку
            cursor.execute("""
                INSERT INTO supply (tov_id, supplier_id, shop_id, quantity, cena)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                tov_id, supplier_id, shop_id, 0, cena))  # Количество можно установить в 0 или запросить у пользователя

            conn.commit()

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Не удалось создать поставку: {err}")

    def show_post_table(self):
        """Отображает таблицу поставок с возможностью редактирования выбранных записей"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            self.section_title_label.setText("Поставки")
            cursor.execute("SELECT supply_id, tov_id, quantity, cena, shop_id, supply_date, supplier_id FROM supply")
            rows = cursor.fetchall()

            self.table = QTableWidget()
            self.table.setColumnCount(8)  # 7 полей + флажок
            self.table.setHorizontalHeaderLabels([
                "", "№ Поставки", "Товар", "Количество", "Цена", "Магазин", "Дата", "Поставщик"
            ])
            self.table.setRowCount(len(rows))

            for i, row in enumerate(rows):
                checkbox = QTableWidgetItem()
                checkbox.setCheckState(Qt.Unchecked)
                self.table.setItem(i, 0, checkbox)

                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    # Все ячейки изначально заблокированы для редактирования
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.table.setItem(i, j + 1, item)
            self.table.hideColumn(1)
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.table.setStyleSheet("font-size: 16px;")
            self.post_table = self.table  # Сохраняем таблицу для других методов

            # Добавляем кнопки
            btn_layout = QHBoxLayout()
            add_button = QPushButton("Добавить")
            add_button.clicked.connect(self.add_supply)

            edit_button = QPushButton("Редактировать")
            edit_button.clicked.connect(self.enable_p_editing)

            save_button = QPushButton("Сохранить")
            save_button.clicked.connect(lambda: self.save_supply_changes(self.table))

            delete_button = QPushButton("Удалить")
            delete_button.clicked.connect(self.delete_supply_records)

            btn_layout.addWidget(add_button)
            btn_layout.addWidget(edit_button)
            btn_layout.addWidget(save_button)
            btn_layout.addWidget(delete_button)

            main_layout = QVBoxLayout()
            main_layout.addWidget(self.section_title_label)
            main_layout.addWidget(self.table)
            main_layout.addLayout(btn_layout)

            container = QWidget()
            container.setLayout(main_layout)

            if self.content_widget:
                self.content_widget.deleteLater()

            self.main_splitter.replaceWidget(1, container)
            self.content_widget = container

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Ошибка загрузки: {err}")

    def add_supply(self):
        """Добавляет новую поставку с минимальным существующим id_tov и его shop_id."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Получаем следующий ID для поставки
            next_id = get_next_id("supply", "supply_id")

            # Находим минимальный существующий id_tov и его shop_id из таблицы catalog
            cursor.execute("""
                SELECT id_tov, shop 
                FROM catalog 
                ORDER BY id_tov ASC 
                LIMIT 1
            """)
            result = cursor.fetchone()

            if not result:
                self.show_message("Ошибка", "В каталоге нет товаров. Сначала добавьте товары.")
                return

            tov_id, shop_id = result  # Минимальный id_tov и его shop_id

            # Добавляем новую запись с минимальным id_tov и его shop_id
            cursor.execute("""
                INSERT INTO supply (supply_id, tov_id, quantity, cena, shop_id, supply_date, supplier_id)
                VALUES (%s, %s, 0, 0.00, %s, NOW(), 1)
            """, (next_id, tov_id, shop_id))

            conn.commit()
            self.show_post_table()  # Обновляем таблицу

        except mysql.connector.Error as err:
            self.show_message("Ошибка БД", f"Ошибка: {err}")
            if conn.is_connected():
                conn.rollback()
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def enable_supply_editing(self):
        """Разрешает редактирование только для отмеченных записей"""
        for row in range(self.post_table.rowCount()):
            checkbox = self.post_table.item(row, 0)
            if checkbox.checkState() == Qt.Checked:
                # Разрешаем редактировать только нужные столбцы
                for col in [3, 4, 6]:  # Количество, Цена, Поставщик
                    item = self.post_table.item(row, col)
                    item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)

    def save_supply_changes(self, table):
        """Сохраняет изменения в таблице поставок, обновляет каталог с учетом всех поставок этого товара"""
        try:
            if not table:
                raise ValueError("Ошибка: table передаётся как None или False!")

            # Проверка на наличие отмеченных флажков
            has_checked = False
            for row in range(table.rowCount()):
                checkbox_item = table.item(row, 0)
                if checkbox_item and checkbox_item.checkState() == Qt.Checked:
                    has_checked = True
                    break

            #if not has_checked:
                #self.show_message("Ошибка", "Не выбрано ни одной записи для сохранения.")
                #return

            # Проверка на пустые ячейки и корректность данных
            for row in range(table.rowCount()):
                checkbox_item = table.item(row, 0)
                if checkbox_item and checkbox_item.checkState() == Qt.Checked:
                    # Проверка на пустые ячейки
                    for col in range(1, table.columnCount()):  # Пропускаем флажки
                        item = table.item(row, col)
                        if item is None or item.text().strip() == "":
                            self.show_message("Ошибка", "Не должно быть пустых ячеек!")
                            return
                        # Проверка формата даты
                        date_item = table.item(row, 6)  # Дата поставки
                        if date_item is None or date_item.text().strip() == "":
                            self.show_message("Ошибка", "Дата поставки не может быть пустой!")
                            return
                        if not validate_datetime(date_item.text()):
                            self.show_message("Ошибка",
                                              "Некорректный вид даты. Используйте формат: ГГГГ-ММ-ДД ЧЧ:ММ:СС")
                            return
                    # Проверка на корректность количества
                    quantity_item = table.item(row, 3)  # Количество товара
                    if quantity_item is None or quantity_item.text().strip() == "":
                        self.show_message("Ошибка", "Количество товара не может быть пустым!")
                        return
                    try:
                        quantity = int(quantity_item.text())
                        if quantity < 0:
                            self.show_message("Ошибка", "Количество товара должно быть неотрицательным!")
                            return
                    except ValueError:
                        self.show_message("Ошибка", "Некорректное значение количества!")
                        return

                    # Проверка на корректность цены
                    price_item = table.item(row, 4)  # Цена поставки
                    if price_item is None or price_item.text().strip() == "":
                        self.show_message("Ошибка", "Цена поставки не может быть пустой!")
                        return
                    try:
                        price = float(price_item.text())  # Проверяем, что цена является десятичным числом
                        if price < 0:
                            self.show_message("Ошибка", "Цена поставки должна быть неотрицательной!")
                            return
                    except ValueError:
                        self.show_message("Ошибка", "Некорректное значение цены! Цена должна быть числом.")
                        return

            conn = get_db_connection()
            cursor = conn.cursor()

            for row in range(table.rowCount()):
                checkbox_item = table.item(row, 0)
                if checkbox_item and checkbox_item.checkState() == Qt.Checked:
                    supply_id = int(table.item(row, 1).text())  # ID поставки
                    tov_id = int(table.item(row, 2).text())  # ID товара
                    new_quantity = int(table.item(row, 3).text())  # Новое количество
                    price = float(table.item(row, 4).text())  # Цена поставки (вводится пользователем)
                    shop_id = int(table.item(row, 5).text())  # Магазин
                    supplier_id = int(table.item(row, 7).text())  # Поставщик
                    supply_date = table.item(row, 6).text()  # Дата поставки

                    # Проверка, что товар существует в указанном магазине
                    cursor.execute("""
                        SELECT id_tov FROM catalog 
                        WHERE id_tov = %s AND shop = %s
                    """, (tov_id, shop_id))
                    if not cursor.fetchone():
                        self.show_message("Ошибка", f"Товара с номером {tov_id} нет в магазине {shop_id}.")
                        return

                    # Проверка, что поставщик существует
                    cursor.execute("SELECT id_post FROM supplier WHERE id_post = %s", (supplier_id,))
                    if not cursor.fetchone():
                        self.show_message("Ошибка", f"Поставщика с номером {supplier_id} не существует.")
                        return

                    # Получаем старое количество из поставки (если это изменение существующей поставки)
                    old_quantity = 0
                    if supply_id:  # Если это не новая поставка
                        cursor.execute("SELECT quantity FROM supply WHERE supply_id = %s", (supply_id,))
                        result = cursor.fetchone()
                        if result:
                            old_quantity = result[0]

                    # Обновляем запись в базе данных
                    cursor.execute("""
                        UPDATE supply
                        SET tov_id = %s, quantity = %s, cena = %s, shop_id = %s, supplier_id = %s, supply_date = %s
                        WHERE supply_id = %s
                    """, (tov_id, new_quantity, price, shop_id, supplier_id, supply_date, supply_id))

                    # Обновляем количество товара в каталоге
                    # 1. Вычитаем старое количество из каталога (если это изменение существующей поставки)
                    if old_quantity > 0:
                        cursor.execute("""
                            UPDATE catalog 
                            SET col = col - %s 
                            WHERE id_tov = %s AND shop = %s
                        """, (old_quantity, tov_id, shop_id))

                    # 2. Добавляем новое количество в каталог
                    cursor.execute("""
                        UPDATE catalog 
                        SET col = col + %s 
                        WHERE id_tov = %s AND shop = %s
                    """, (new_quantity, tov_id, shop_id))

            conn.commit()

            # После сохранения обновляем и каталог, и таблицу поставок
            self.show_post_table()
            self.show_catalog_table()

        except Exception as e:
            self.show_message("Ошибка", f"Ошибка: {e}")

        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def delete_supply_records(self):
        """Удаляет выбранные поставки"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            for row in range(self.post_table.rowCount()):
                checkbox = self.post_table.item(row, 0)
                if checkbox.checkState() == Qt.Checked:
                    supply_id = self.post_table.item(row, 1).text()
                    cursor.execute("DELETE FROM supply WHERE supply_id = %s", (supply_id,))

            conn.commit()
            self.show_post_table()

        except mysql.connector.Error as err:
            self.show_message("Ошибка БД", f"Ошибка: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def remove_from_cart(self, table):
        """Удаляет товар из корзины и переключает пользователя на каталог"""
        selected_items = table.selectionModel().selectedRows()
        row = selected_items[0].row()
        cart_id = int(table.item(row, 0).text())

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cart WHERE cart_id = %s", (cart_id,))
            conn.commit()

            self.show_section("Каталог", self.catalog_button)  # Переключаемся на каталог

            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Не удалось удалить товар из корзины: {err}")

    def enable_p_editing(self):
        """Разрешает редактирование только для отмеченных строк и определённых столбцов"""
        for row in range(self.post_table.rowCount()):
            checkbox = self.post_table.item(row, 0)
            if checkbox.checkState() == Qt.Checked:
                # Разрешаем редактирование для определённых столбцов
                for col in [2, 3, 4,5, 6, 7]:  # Товар, Количество, Цена, Поставщик
                    item = self.post_table.item(row, col)
                    item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)

    def show_clients_table(self):
        """Отображает таблицу продавцов (исправленная версия)"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            self.section_title_label.setText("Продавцы")
            cursor.execute("SELECT id_pdv, famio, login, password, id_mg, actor FROM seller")
            rows = cursor.fetchall()

            table = QTableWidget()
            table.setColumnCount(7)  # Флажок + 6 столбцов
            table.setHorizontalHeaderLabels([
                "", "№ Продавца", "ФИО", "Логин", "Пароль", "№ Магазина", "Должность"
            ])
            table.setRowCount(len(rows))

            for i, row in enumerate(rows):
                # Флажок
                chk_item = QTableWidgetItem()
                chk_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                chk_item.setCheckState(Qt.Unchecked)
                table.setItem(i, 0, chk_item)

                # Данные
                for j in range(1, 7):  # Столбцы с 1 по 6 (№ Продавца, ФИО, Логин, Пароль, № Магазина, Должность)
                    item = QTableWidgetItem(str(row[j - 1]))
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    table.setItem(i, j, item)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            # Кнопки
            self.add_seller_btn = QPushButton("Добавить")
            self.add_seller_btn.clicked.connect(self.add_seller)

            self.edit_seller_btn = QPushButton("Редактировать")
            self.edit_seller_btn.clicked.connect(lambda: self.enable_seller_editing(table))

            self.save_seller_btn = QPushButton("Сохранить")
            self.save_seller_btn.clicked.connect(lambda: self.save_seller_changes(table))

            self.delete_seller_btn = QPushButton("Удалить")
            self.delete_seller_btn.clicked.connect(lambda: self.delete_seller_records(table))

            # Расположение элементов
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(self.add_seller_btn)
            btn_layout.addWidget(self.edit_seller_btn)
            btn_layout.addWidget(self.save_seller_btn)
            btn_layout.addWidget(self.delete_seller_btn)

            layout = QVBoxLayout()
            layout.addWidget(self.section_title_label)
            layout.addWidget(table)
            layout.addLayout(btn_layout)

            container = QWidget()
            container.setLayout(layout)

            # Важно! Обновляем контент
            if self.content_widget:
                self.content_widget.deleteLater()
            self.main_splitter.replaceWidget(1, container)
            self.content_widget = container

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Ошибка загрузки: {err}")

    def add_seller(self):
        """Добавление нового продавца с проверкой магазина"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Проверка существования магазина по умолчанию
            cursor.execute("SELECT id_shopa FROM shop WHERE id_shopa = 1")
            if not cursor.fetchone():
                self.show_message("Ошибка", "Сначала создайте магазин!")
                return
            # Получаем следующий ID для продавца
            next_id = get_next_id("seller", "id_pdv")

            cursor.execute("""
                INSERT INTO seller (id_pdv, famio, login, password, id_mg, actor)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (next_id, "Новый продавец", "логин", "пароль", 1, "Продавец"))


            conn.commit()
            self.show_clients_table()

        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Ошибка добавления: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def enable_seller_editing(self, table):
        """Включает редактирование для выбранных записей и добавляет выпадающий список для роли"""
        for row in range(table.rowCount()):
            if table.item(row, 0).checkState() == Qt.Checked:
                # Разрешаем редактирование для всех столбцов, кроме ID
                for col in [2, 3, 4, 5]:  # Столбцы: ФИО, Логин, Пароль, ID Магазина
                    item = table.item(row, col)
                    item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)

                # Добавляем выпадающий список для роли
                combo_box = QComboBox()
                combo_box.addItems(["Продавец", "Администратор"])
                combo_box.setCurrentText(table.item(row, 6).text())  # Устанавливаем текущее значение роли
                table.setCellWidget(row, 6, combo_box)

    def save_seller_changes(self, table):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Проверка на наличие отмеченных флажков
            has_checked = False
            for row in range(table.rowCount()):
                if table.item(row, 0).checkState() == Qt.Checked:
                    has_checked = True
                    break

            #if not has_checked:
                #self.show_message("Ошибка", "Не выбрано ни одной записи для сохранения.")
                #return

            for row in range(table.rowCount()):
                if table.item(row, 0).checkState() == Qt.Checked:
                    seller_id = table.item(row, 1).text()
                    famio = table.item(row, 2).text()
                    login = table.item(row, 3).text()
                    password = table.item(row, 4).text()
                    id_mg = table.item(row, 5).text()
                    actor = table.cellWidget(row, 6).currentText()

                    # Проверка на длину строки
                    if not validate_string(famio, 255):  # ФИО
                        self.show_message("Ошибка", "ФИО должно быть строкой не длиннее 255 символов.")
                        return
                    if not validate_string(login, 45):  # Логин
                        self.show_message("Ошибка", "Логин должен быть строкой не длиннее 45 символов.")
                        return
                    if not validate_string(password, 10):  # Пароль
                        self.show_message("Ошибка", "Пароль должен быть строкой не длиннее 10 символов.")
                        return

                    # Обновляем запись
                    cursor.execute("""
                        UPDATE seller 
                        SET famio=%s, login=%s, password=%s, id_mg=%s, actor=%s
                        WHERE id_pdv=%s
                    """, (famio, login, password, id_mg, actor, seller_id))

                    # Снимаем флажок после сохранения
                    table.item(row, 0).setCheckState(Qt.Unchecked)

            conn.commit()
            self.show_clients_table()

        except Exception as e:
            self.show_message("Ошибка", f"Ошибка сохранения: {str(e)}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()


    def delete_seller_records(self, table):
        """Удаление выбранных продавцов"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            for row in range(table.rowCount()):
                if table.item(row, 0).checkState() == Qt.Checked:
                    seller_id = table.item(row, 1).text()
                    cursor.execute("DELETE FROM seller WHERE id_pdv = %s", (seller_id,))

            conn.commit()
            self.show_clients_table()

        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Ошибка удаления: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def clear_cart_item(self, table):
        """Удаляет выбранный товар из корзины"""
        try:
            selected_rows = table.selectionModel().selectedRows()

            row = selected_rows[0].row()
            cart_id = int(table.item(row, 0).text())

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM cart WHERE cart_id = %s", (cart_id,))
            conn.commit()


            self.show_cart_table()
            self.remove_from_cart(table)

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            self.show_message("Ошибка", f"Не удалось удалить товар из корзины: {err}")

    def show_message(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def closeEvent(self, event):
        """Гарантированное завершение программы при выходе"""
        sys.exit(0)

# Запуск приложения
if __name__ == '__main__':
    app = QApplication([])
    window = FlowerShop()
    if window.actor is not None:
        window.show()
    else:
        sys.exit(0)  # Завершаем приложение, если роль не определена
    sys.exit(app.exec_())