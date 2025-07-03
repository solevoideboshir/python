import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QListWidget, 
                            QLineEdit, QComboBox, QSpinBox, QTextEdit, 
                            QCalendarWidget, QMessageBox, QScrollArea, 
                            QTabWidget, QCheckBox, QGroupBox, QFrame,
                            QStackedWidget, QDialog, QDialogButtonBox, 
                            QListWidgetItem)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette

class Ingredient:
    def __init__(self, name, amount, unit):
        self.name = name
        self.amount = amount
        self.unit = unit

class Recipe:
    def __init__(self, recipe_id, title, category, time, ingredients, steps, image=None):
        self.id = recipe_id
        self.title = title
        self.category = category
        self.time = time
        self.ingredients = ingredients
        self.steps = steps
        self.image = image

class DataRepository:
    _instance = None
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = DataRepository()
        return cls._instance
    
    def __init__(self):
        self.recipes = [
            Recipe(1, "Омлет с овощами", "Завтрак", 15,
                  [Ingredient("Яйца", 3, "шт"), Ingredient("Помидоры", 1, "шт"), Ingredient("Лук", 0.5, "шт"), Ingredient("Масло растительное", 1, "ст.л")],
                  ["1. Взбить яйца", 
                   "2. Нарезать овощи мелкими кубиками", 
                   "3. Взбить яйца с солью и перцем", 
                   "4. Обжарить лук до прозрачности",
                   "5. Добавить помидоры, обжарить 2 минуты",]),
            Recipe(2, "Салат Цезарь", "Обед", 20,
                  [Ingredient("Куриная грудка", 200, "г"), Ingredient("Салат Айсберг", 100, "г"), Ingredient("Сухарики", 50, "г"), Ingredient("Сыр Пармезан", 30, "г"), Ingredient("Соус Цезарь", 2, "ст.л")],
                  ["1. Обжарить куриную грудку до готовности",
                    "2. Порвать салат руками на крупные куски",
                    "3. Нарезать курицу ломтиками",
                    "4. Смешать все ингредиенты в большой миске",
                    "5. Заправить соусом и посыпать пармезаном"]),
            Recipe(3, "Паста Карбонара", "Ужин", 30,
                  [Ingredient("Спагетти", 200, "г"), Ingredient("Бекон", 150, "г"), Ingredient("Яйца", 2, "шт"), Ingredient("Сыр Пармезан", 50, "г"), Ingredient("Чеснок", 2, "зубчика"),],
                  ["1. Отварить пасту согласно инструкции на упаковке",
                    "2. Обжарить бекон до хрустящей корочки",
                    "3. Взбить яйца с тертым пармезаном и черным перцем",
                    "4. Добавить к яйцам горячую пасту и бекон, быстро перемешать",
                    "5. Подавать сразу же, посыпав дополнительно пармезаном"])
        ]
        self.menu = {}
        self.user_preferences = {
            'name': 'Пользователь',
            'diet': 'Нет',
            'notifications': True
        }
    
    def get_all_recipes(self):
        return self.recipes
    
    def get_recipes_by_category(self, category):
        return [r for r in self.recipes if r.category == category]
    
    def get_recipe_by_id(self, recipe_id):
        for recipe in self.recipes:
            if recipe.id == recipe_id:
                return recipe
        return None
    
    def add_recipe(self, recipe):
        recipe.id = max(r.id for r in self.recipes) + 1 if self.recipes else 1
        self.recipes.append(recipe)
        return recipe.id
    
    def get_menu_for_date(self, date):
        return self.menu.get(date, {"Завтрак": None, "Обед": None, "Ужин": None})
    
    def add_to_menu(self, date, meal_type, recipe):
        if date not in self.menu:
            self.menu[date] = {"Завтрак": None, "Обед": None, "Ужин": None}
        self.menu[date][meal_type] = recipe
    
    def update_user_preferences(self, name, diet, notifications):
        self.user_preferences = {
            'name': name,
            'diet': diet,
            'notifications': notifications
        }

class RecipeDetailDialog(QDialog):
    def __init__(self, recipe, parent=None):
        super().__init__(parent)
        self.setWindowTitle(recipe.title)
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(recipe.title)
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        title_label.setStyleSheet("color: #C71585;")
        layout.addWidget(title_label)

        details_layout = QHBoxLayout()
        details_layout.addWidget(QLabel(f"Категория: {recipe.category}"))
        details_layout.addWidget(QLabel(f"Время приготовления: {recipe.time} мин"))
        layout.addLayout(details_layout)

        ingredients_group = QGroupBox("Ингредиенты")
        ingredients_layout = QVBoxLayout()
        
        for ingredient in recipe.ingredients:
            ingredient_label = QLabel(
                f"• {ingredient.name}: {ingredient.amount} {ingredient.unit}"
            )
            ingredients_layout.addWidget(ingredient_label)
        
        ingredients_group.setLayout(ingredients_layout)
        layout.addWidget(ingredients_group)

        steps_group = QGroupBox("Шаги приготовления")
        steps_layout = QVBoxLayout()
        
        steps_text = QTextEdit()
        steps_text.setReadOnly(True)
        steps_text.setPlainText("\n".join(recipe.steps))
        steps_layout.addWidget(steps_text)
        
        steps_group.setLayout(steps_layout)
        layout.addWidget(steps_group)

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFF0F5;
            }
            QGroupBox {
                border: 1px solid #FFB6C1;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                color: #C71585;
                font-weight: bold;
            }
            QTextEdit {
                background-color: #FFF0F5;
                border: 1px solid #FFB6C1;
                border-radius: 5px;
            }
        """)

class BaseScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        self.header = QHBoxLayout()
        
        self.logo = QLabel("🍳 Кулинарный справочник")
        self.logo.setFont(QFont('Arial', 14, QFont.Bold))
        self.logo.setStyleSheet("color: #FF1493;")  
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск рецептов...")
        self.search_input.setFixedWidth(300)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #FF69B4;
                border-radius: 10px;
                padding: 5px;
                background: #FFF0F5;
            }
        """)
        
        self.profile_btn = QPushButton("👤")
        self.profile_btn.setFixedSize(40, 40)
        self.profile_btn.clicked.connect(self.parent.show_profile)
        self.profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF69B4;
                border-radius: 20px;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #FF1493;
            }
        """)
        
        self.header.addWidget(self.logo)
        self.header.addStretch()
        self.header.addWidget(self.search_input)
        self.header.addWidget(self.profile_btn)
        
        self.nav_layout = QHBoxLayout()
        self.nav_layout.setSpacing(10)
        
        self.main_btn = QPushButton("Главная")
        self.main_btn.clicked.connect(self.parent.show_home)
        
        self.recipes_btn = QPushButton("Мои рецепты")
        self.recipes_btn.clicked.connect(self.parent.show_recipes)
        
        self.menu_btn = QPushButton("Меню")
        self.menu_btn.clicked.connect(self.parent.show_menu)
        
        for btn in [self.main_btn, self.recipes_btn, self.menu_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFB6C1;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 5px;
                    color: #8B008B;
                }
                QPushButton:hover {
                    background-color: #FF69B4;
                    color: white;
                }
            """)
        
        self.nav_layout.addWidget(self.main_btn)
        self.nav_layout.addWidget(self.recipes_btn)
        self.nav_layout.addWidget(self.menu_btn)
        
        self.content = QWidget()
        self.content_layout = QVBoxLayout()
        self.content.setLayout(self.content_layout)
        
        self.main_layout.addLayout(self.header)
        self.main_layout.addLayout(self.nav_layout)
        self.main_layout.addWidget(self.content)
        
        self.setLayout(self.main_layout)
    
    def update_nav_buttons(self, current_screen):
        buttons = {
            'home': self.main_btn,
            'recipes': self.recipes_btn,
            'menu': self.menu_btn
        }
        
        for name, btn in buttons.items():
            if name == current_screen:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #DB7093;
                        color: white;
                        border: none;
                        padding: 8px 15px;
                        border-radius: 5px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FFB6C1;
                        border: none;
                        padding: 8px 15px;
                        border-radius: 5px;
                        color: #8B008B;
                    }
                    QPushButton:hover {
                        background-color: #FF69B4;
                        color: white;
                    }
                """)

class HomeScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent)
        self.update_nav_buttons('home')
        self.init_content()
    
    def init_content(self):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        title = QLabel("Популярные рецепты")
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #C71585;")  
        self.content_layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                background: #FFF0F5;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: #FF69B4;
                min-height: 20px;
                border-radius: 4px;
            }
        """)
        
        recipes_widget = QWidget()
        recipes_layout = QVBoxLayout()
        recipes_layout.setSpacing(15)
        
        repo = DataRepository.instance()
        for recipe in repo.get_all_recipes():
            recipe_card = self.create_recipe_card(recipe)
            recipes_layout.addWidget(recipe_card)
        
        recipes_widget.setLayout(recipes_layout)
        scroll.setWidget(recipes_widget)
        self.content_layout.addWidget(scroll)
    
    def create_recipe_card(self, recipe):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setLineWidth(1)
        card.setStyleSheet("""
            QFrame {
                background-color: #FFF0F5;
                border: 1px solid #FFB6C1;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel(recipe.title)
        title.setFont(QFont('Arial', 12, QFont.Bold))
        title.setStyleSheet("color: #DB7093;")
        
        details = QLabel(f"⏱ {recipe.time} мин | 🍽 {recipe.category}")
        details.setStyleSheet("color: #8B008B;")
        
        btn = QPushButton("Посмотреть рецепт")
        btn.clicked.connect(lambda checked, rid=recipe.id: self.parent.show_recipe_detail(rid))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #FF69B4;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: #FF1493;
            }
        """)
        
        layout.addWidget(title)
        layout.addWidget(details)
        layout.addWidget(btn)
        
        card.setLayout(layout)
        return card

class RecipesScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent)
        self.update_nav_buttons('recipes')
        self.init_content()
    
    def init_content(self):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(5)
        
        categories = ["Все", "Завтрак", "Обед", "Ужин", "Десерт"]
        for category in categories:
            btn = QPushButton(category)
            btn.clicked.connect(lambda _, c=category: self.filter_recipes(c))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFB6C1;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 5px;
                    color: #8B008B;
                }
                QPushButton:hover {
                    background-color: #FF69B4;
                    color: white;
                }
            """)
            filter_layout.addWidget(btn)
        
        self.content_layout.addLayout(filter_layout)
        
        self.recipes_list = QListWidget()
        self.recipes_list.setStyleSheet("""
            QListWidget {
                background-color: #FFF0F5;
                border: 1px solid #FFB6C1;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #FFB6C1;
            }
            QListWidget::item:hover {
                background-color: #FFE4E1;
            }
        """)
        self.load_recipes("Все")
        self.recipes_list.itemDoubleClicked.connect(
            lambda item: self.parent.show_recipe_detail(item.data(Qt.UserRole)))
        
        self.content_layout.addWidget(self.recipes_list)
        
        add_btn = QPushButton("➕ Добавить рецепт")
        add_btn.clicked.connect(self.parent.show_add_recipe)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #DB7093;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF1493;
            }
        """)
        self.content_layout.addWidget(add_btn)
    
    def load_recipes(self, category):
        self.recipes_list.clear()
        repo = DataRepository.instance()
        
        if category == "Все":
            recipes = repo.get_all_recipes()
        else:
            recipes = repo.get_recipes_by_category(category)
        
        for recipe in recipes:
            item = QListWidgetItem(f"{recipe.title} ({recipe.time} мин, {recipe.category})")
            item.setData(Qt.UserRole, recipe.id)
            self.recipes_list.addItem(item)
    
    def filter_recipes(self, category):
        self.load_recipes(category)

class MenuScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent)
        self.update_nav_buttons('menu')
        self.init_content()
    
    def init_content(self):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.load_day_menu)
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #FFF0F5;
                border: 1px solid #FFB6C1;
            }
            QCalendarWidget QToolButton {
                color: #8B008B;
                font-size: 12px;
                icon-size: 20px, 20px;
            }
            QCalendarWidget QMenu {
                background-color: #FFF0F5;
                border: 1px solid #FFB6C1;
            }
            QCalendarWidget QSpinBox {
                background-color: #FFF0F5;
                color: #8B008B;
                selection-background-color: #FF69B4;
                selection-color: white;
            }
            QCalendarWidget QWidget { 
                alternate-background-color: #FFE4E1;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #8B008B;
                selection-background-color: #FF69B4;
                selection-color: white;
            }
        """)
        self.content_layout.addWidget(self.calendar)
        
        self.day_menu_group = QGroupBox()
        self.day_menu_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #FFB6C1;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                color: #C71585;
                font-weight: bold;
            }
        """)
        day_menu_layout = QVBoxLayout()
        
        self.breakfast_label = QLabel("Завтрак: не выбрано")
        self.lunch_label = QLabel("Обед: не выбрано")
        self.dinner_label = QLabel("Ужин: не выбрано")
        
        for label in [self.breakfast_label, self.lunch_label, self.dinner_label]:
            label.setStyleSheet("color: #8B008B;")
        
        day_menu_layout.addWidget(self.breakfast_label)
        day_menu_layout.addWidget(self.lunch_label)
        day_menu_layout.addWidget(self.dinner_label)
        
        add_btn = QPushButton("Добавить блюдо в меню")
        add_btn.clicked.connect(self.add_to_menu)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF69B4;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: #FF1493;
            }
        """)
        day_menu_layout.addWidget(add_btn)
        
        self.day_menu_group.setLayout(day_menu_layout)
        self.content_layout.addWidget(self.day_menu_group)
        
        self.load_day_menu()
    
    def load_day_menu(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        repo = DataRepository.instance()
        menu = repo.get_menu_for_date(selected_date)
        
        self.day_menu_group.setTitle(f"Меню на {self.calendar.selectedDate().toString('dd.MM.yyyy')}")

        self.breakfast_label.setText(
            f"Завтрак: {menu['Завтрак'].title if menu['Завтрак'] else 'не выбрано'}")
        self.lunch_label.setText(
            f"Обед: {menu['Обед'].title if menu['Обед'] else 'не выбрано'}")
        self.dinner_label.setText(
            f"Ужин: {menu['Ужин'].title if menu['Ужин'] else 'не выбрано'}")
    
    def add_to_menu(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.parent.show_select_recipe(selected_date)

class ProfileScreen(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent)
        self.update_nav_buttons('')
        self.init_content()
    
    def init_content(self):
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        user_group = QGroupBox("Мой профиль")
        user_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #FFB6C1;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                color: #C71585;
                font-weight: bold;
            }
        """)
        user_layout = QVBoxLayout()
        
        repo = DataRepository.instance()
        user_prefs = repo.user_preferences
        
        name_layout = QHBoxLayout()
        name_label = QLabel("Имя:")
        name_label.setStyleSheet("color: #8B008B;")
        self.name_input = QLineEdit(user_prefs['name'])
        self.name_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #FFB6C1;
                border-radius: 5px;
                padding: 5px;
                background: #FFF0F5;
            }
        """)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        user_layout.addLayout(name_layout)
        
        diet_layout = QHBoxLayout()
        diet_label = QLabel("Предпочтения:")
        diet_label.setStyleSheet("color: #8B008B;")
        self.diet_combo = QComboBox()
        self.diet_combo.addItems(["Нет", "Вегетарианство", "Веганство", "Без глютена"])
        self.diet_combo.setCurrentText(user_prefs['diet'])
        self.diet_combo.setStyleSheet("""
            QComboBox {
                background-color: #FFF0F5;
                border: 1px solid #FFB6C1;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        diet_layout.addWidget(diet_label)
        diet_layout.addWidget(self.diet_combo)
        user_layout.addLayout(diet_layout)
        
        user_group.setLayout(user_layout)
        self.content_layout.addWidget(user_group)
        
        settings_group = QGroupBox("Настройки")
        settings_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #FFB6C1;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                color: #C71585;
                font-weight: bold;
            }
        """)
        settings_layout = QVBoxLayout()
        
        self.notifications_check = QCheckBox("Получать уведомления")
        self.notifications_check.setChecked(user_prefs['notifications'])
        self.notifications_check.setStyleSheet("""
            QCheckBox {
                color: #8B008B;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QCheckBox::indicator:checked {
                background-color: #FF69B4;
            }
        """)
        settings_layout.addWidget(self.notifications_check)
        
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_profile)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF69B4;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: #FF1493;
            }
        """)
        settings_layout.addWidget(save_btn)
        
        settings_group.setLayout(settings_layout)
        self.content_layout.addWidget(settings_group)
        
        logout_btn = QPushButton("Выйти из аккаунта")
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFB6C1;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                color: #8B008B;
            }
            QPushButton:hover {
                background-color: #FF69B4;
                color: white;
            }
        """)
        self.content_layout.addWidget(logout_btn)
    
    def save_profile(self):
        name = self.name_input.text().strip()
        diet = self.diet_combo.currentText()
        notifications = self.notifications_check.isChecked()
        
        if not name:
            self.parent.show_error_message("Введите ваше имя")
            return
        
        repo = DataRepository.instance()
        repo.update_user_preferences(name, diet, notifications)
        
        self.parent.show_success_message("Профиль успешно сохранён")
    
    def logout(self):
        if self.parent.show_confirm_dialog(
            "Выход", 
            "Вы уверены, что хотите выйти из аккаунта?"):
            
            self.parent.show_home()
            self.parent.show_info_message("Вы успешно вышли из аккаунта")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Кулинарный справочник")
        self.setGeometry(100, 100, 800, 600)
        
        self.stack = QStackedWidget()
        
        self.home_screen = HomeScreen(self)
        self.recipes_screen = RecipesScreen(self)
        self.menu_screen = MenuScreen(self)
        self.profile_screen = ProfileScreen(self)
        
        self.stack.addWidget(self.home_screen)
        self.stack.addWidget(self.recipes_screen)
        self.stack.addWidget(self.menu_screen)
        self.stack.addWidget(self.profile_screen)
        
        self.setCentralWidget(self.stack)
        self.show_home()
    
    def show_home(self):
        self.stack.setCurrentWidget(self.home_screen)
        self.home_screen.update_nav_buttons('home')
    
    def show_recipes(self):
        self.stack.setCurrentWidget(self.recipes_screen)
        self.recipes_screen.update_nav_buttons('recipes')
    
    def show_menu(self):
        self.stack.setCurrentWidget(self.menu_screen)
        self.menu_screen.update_nav_buttons('menu')
    
    def show_profile(self):
        self.stack.setCurrentWidget(self.profile_screen)
    
    def show_recipe_detail(self, recipe_id):
        repo = DataRepository.instance()
        recipe = repo.get_recipe_by_id(recipe_id)
        
        if recipe:
            dialog = RecipeDetailDialog(recipe, self)
            dialog.exec_()
        else:
            self.show_error_message("Рецепт не найден")
    
    def show_add_recipe(self):
        self.show_info_message("Добавление нового рецепта")
    
    def show_select_recipe(self, date):
        self.show_info_message(f"Выбор рецепта для {date}")
    
    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Ошибка")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #FFF0F5;
            }
            QMessageBox QLabel {
                color: #8B008B;
            }
            QPushButton {
                background-color: #FF69B4;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: #FF1493;
            }
        """)
        msg.exec_()
    
    def show_success_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Успешно")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #FFF0F5;
            }
            QMessageBox QLabel {
                color: #8B008B;
            }
            QPushButton {
                background-color: #FF69B4;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: #FF1493;
            }
        """)
        msg.exec_()
    
    def show_info_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Информация")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #FFF0F5;
            }
            QMessageBox QLabel {
                color: #8B008B;
            }
            QPushButton {
                background-color: #FF69B4;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: #FF1493;
            }
        """)
        msg.exec_()
    
    def show_confirm_dialog(self, title, message):
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        msg_box = self.findChild(QMessageBox)
        if msg_box:
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #FFF0F5;
                }
                QMessageBox QLabel {
                    color: #8B008B;
                }
                QPushButton {
                    background-color: #FF69B4;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 5px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #FF1493;
                }
            """)
        
        return reply == QMessageBox.Yes

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setStyle("Fusion")
    
    palette = app.palette()
    palette.setColor(palette.Window, QColor(255, 240, 245))  
    palette.setColor(palette.WindowText, QColor(139, 0, 139))  
    palette.setColor(palette.Base, QColor(255, 240, 245))  
    palette.setColor(palette.AlternateBase, QColor(255, 228, 225))  
    palette.setColor(palette.ToolTipBase, Qt.white)
    palette.setColor(palette.ToolTipText, Qt.black)
    palette.setColor(palette.Text, QColor(139, 0, 139)) 
    palette.setColor(palette.Button, QColor(255, 182, 193))  
    palette.setColor(palette.ButtonText, QColor(139, 0, 139)) 
    palette.setColor(palette.BrightText, Qt.red)
    palette.setColor(palette.Link, QColor(255, 105, 180))  
    palette.setColor(palette.Highlight, QColor(255, 105, 180))  
    palette.setColor(palette.HighlightedText, Qt.white)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())