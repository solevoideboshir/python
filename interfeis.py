import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QWidget, 
                            QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QListWidget, QLineEdit, QComboBox, QSpinBox, 
                            QTextEdit, QCalendarWidget, QMessageBox, 
                            QScrollArea, QTabWidget)
from PyQt5.QtCore import Qt, QDate

# ==================== МОДЕЛИ ДАННЫХ ====================
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
            Recipe(1, "Спагетти Карбонара", "Основное", 30,
                  [Ingredient("Спагетти", 200, "г"),
                   Ingredient("Бекон", 100, "г")],
                  ["1. Отварить спагетти", "2. Обжарить бекон"]),
            Recipe(2, "Омлет с овощами", "Завтрак", 15,
                  [Ingredient("Яйца", 3, "шт"),
                   Ingredient("Помидоры", 1, "шт")],
                  ["1. Взбить яйца", "2. Обжарить с овощами"])
        ]
        self.menu = []
    
    def get_all_recipes(self):
        return self.recipes
    
    def get_recipe_by_id(self, recipe_id):
        for recipe in self.recipes:
            if recipe.id == recipe_id:
                return recipe
        return None
    
    def add_recipe(self, recipe):
        recipe.id = max(r.id for r in self.recipes) + 1 if self.recipes else 1
        self.recipes.append(recipe)
        return recipe.id
    
    def get_weekly_menu(self):
        return self.menu
    
    def add_to_menu(self, date, meal_type, recipe):
        self.menu.append((date, meal_type, recipe))

# ==================== ЭКРАНЫ ПРИЛОЖЕНИЯ ====================
class HomeView(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Добро пожаловать в Кулинарный справочник!")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        btn_recipes = QPushButton("Мои рецепты")
        btn_recipes.clicked.connect(self.parent.show_recipes)
        btn_recipes.setStyleSheet("padding: 10px; font-size: 16px;")
        
        btn_menu = QPushButton("Планировщик меню")
        btn_menu.clicked.connect(self.parent.show_menu)
        btn_menu.setStyleSheet("padding: 10px; font-size: 16px;")
        
        layout.addWidget(btn_recipes)
        layout.addWidget(btn_menu)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        popular_widget = QWidget()
        popular_layout = QVBoxLayout()
        
        popular_title = QLabel("Популярные рецепты")
        popular_title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        popular_layout.addWidget(popular_title)
        
        repo = DataRepository.instance()
        for recipe in repo.get_all_recipes()[:3]:
            btn = QPushButton(f"{recipe.title} ({recipe.time} мин)")
            btn.clicked.connect(lambda _, r=recipe: self.parent.show_recipe_detail(r.id))
            popular_layout.addWidget(btn)
        
        popular_widget.setLayout(popular_layout)
        scroll.setWidget(popular_widget)
        layout.addWidget(scroll)
        
        self.setLayout(layout)

class RecipesView(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск рецептов...")
        search_layout.addWidget(self.search_input)
        
        self.category_filter = QComboBox()
        self.category_filter.addItems(["Все категории", "Завтраки", "Основные", "Десерты"])
        search_layout.addWidget(self.category_filter)
        
        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self.search_recipes)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        self.recipes_list = QListWidget()
        self.recipes_list.itemDoubleClicked.connect(
            lambda: self.parent.show_recipe_detail(
                self.recipes_list.currentRow() + 1))
        layout.addWidget(self.recipes_list)
        
        action_layout = QHBoxLayout()
        
        add_btn = QPushButton("Добавить рецепт")
        add_btn.clicked.connect(self.parent.show_add_recipe)
        
        back_btn = QPushButton("На главную")
        back_btn.clicked.connect(self.parent.show_home)
        
        action_layout.addWidget(add_btn)
        action_layout.addWidget(back_btn)
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
    
    def load_recipes(self):
        self.recipes_list.clear()
        repo = DataRepository.instance()
        for recipe in repo.get_all_recipes():
            self.recipes_list.addItem(f"{recipe.title} ({recipe.time} мин)")
    
    def search_recipes(self):
        search_text = self.search_input.text().lower()
        category = self.category_filter.currentText()
        
        self.recipes_list.clear()
        repo = DataRepository.instance()
        
        for recipe in repo.get_all_recipes():
            if (search_text in recipe.title.lower() or 
                any(search_text in ing.name.lower() for ing in recipe.ingredients)):
                if category == "Все категории" or recipe.category == category:
                    self.recipes_list.addItem(f"{recipe.title} ({recipe.time} мин)")

class RecipeDetailView(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.current_recipe = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        header_layout = QHBoxLayout()
        
        self.back_btn = QPushButton("← Назад")
        self.back_btn.clicked.connect(self.parent.show_recipes)
        header_layout.addWidget(self.back_btn)
        
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(self.title_label, stretch=1)
        
        layout.addLayout(header_layout)
        
        self.tabs = QTabWidget()
        
        self.ingredients_tab = QTextEdit()
        self.ingredients_tab.setReadOnly(True)
        self.tabs.addTab(self.ingredients_tab, "Ингредиенты")
        
        self.steps_tab = QTextEdit()
        self.steps_tab.setReadOnly(True)
        self.tabs.addTab(self.steps_tab, "Приготовление")
        
        layout.addWidget(self.tabs)
        
        action_layout = QHBoxLayout()
        
        self.add_to_menu_btn = QPushButton("Добавить в меню")
        self.add_to_menu_btn.clicked.connect(self.add_to_menu)
        
        action_layout.addWidget(self.add_to_menu_btn)
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
    
    def load_recipe(self, recipe_id):
        repo = DataRepository.instance()
        self.current_recipe = repo.get_recipe_by_id(recipe_id)
        
        self.title_label.setText(self.current_recipe.title)
        
        ingredients_text = ""
        for ing in self.current_recipe.ingredients:
            ingredients_text += f"- {ing.name}: {ing.amount} {ing.unit}\n"
        self.ingredients_tab.setText(ingredients_text)
        
        steps_text = ""
        for i, step in enumerate(self.current_recipe.steps, 1):
            steps_text += f"{i}. {step}\n\n"
        self.steps_tab.setText(steps_text)
    
    def add_to_menu(self):
        if self.current_recipe:
            self.parent.show_info_message("Рецепт добавлен в меню")

class AddRecipeView(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Добавление нового рецепта")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Название рецепта")
        
        self.category_input = QComboBox()
        self.category_input.addItems(["Завтрак", "Обед", "Ужин", "Десерт", "Закуска"])
        
        self.time_input = QSpinBox()
        self.time_input.setRange(1, 600)
        self.time_input.setSuffix(" мин")
        
        ingredients_label = QLabel("Ингредиенты:")
        self.ingredients_edit = QTextEdit()
        self.ingredients_edit.setPlaceholderText("Каждый ингредиент с новой строки в формате: Название, количество, единица\nНапример: Мука, 200, г")
        
        steps_label = QLabel("Шаги приготовления:")
        self.steps_edit = QTextEdit()
        self.steps_edit.setPlaceholderText("Опишите шаги приготовления, каждый с новой строки")
        
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Сохранить рецепт")
        save_btn.clicked.connect(self.save_recipe)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.parent.show_recipes)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addWidget(QLabel("Название:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Категория:"))
        layout.addWidget(self.category_input)
        layout.addWidget(QLabel("Время приготовления:"))
        layout.addWidget(self.time_input)
        layout.addWidget(ingredients_label)
        layout.addWidget(self.ingredients_edit)
        layout.addWidget(steps_label)
        layout.addWidget(self.steps_edit)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def clear_form(self):
        self.name_input.clear()
        self.category_input.setCurrentIndex(0)
        self.time_input.setValue(10)
        self.ingredients_edit.clear()
        self.steps_edit.clear()
    
    def save_recipe(self):
        if not self.name_input.text().strip():
            self.parent.show_error_message("Введите название рецепта")
            return
        
        ingredients = []
        for line in self.ingredients_edit.toPlainText().split('\n'):
            line = line.strip()
            if line:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 3:
                    name, amount, unit = parts[0], parts[1], parts[2]
                    try:
                        amount = float(amount)
                        ingredients.append(Ingredient(name, amount, unit))
                    except ValueError:
                        self.parent.show_error_message(f"Некорректное количество для ингредиента: {name}")
                        return
        
        if not ingredients:
            self.parent.show_error_message("Добавьте хотя бы один ингредиент")
            return
        
        steps = [step.strip() for step in self.steps_edit.toPlainText().split('\n') if step.strip()]
        
        if not steps:
            self.parent.show_error_message("Добавьте хотя бы один шаг приготовления")
            return
        
        recipe = Recipe(
            recipe_id=0,
            title=self.name_input.text(),
            category=self.category_input.currentText(),
            time=self.time_input.value(),
            ingredients=ingredients,
            steps=steps
        )
        
        repo = DataRepository.instance()
        recipe_id = repo.add_recipe(recipe)
        
        self.parent.show_success_message(f"Рецепт '{recipe.title}' успешно сохранён!")
        self.parent.show_recipe_detail(recipe_id)

class MenuView(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.load_day_menu)
        layout.addWidget(self.calendar)
        
        self.day_menu_label = QLabel()
        self.day_menu_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.day_menu_label)
        
        self.menu_list = QListWidget()
        layout.addWidget(self.menu_list)
        
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Добавить блюдо")
        add_btn.clicked.connect(self.add_to_menu)
        
        shopping_btn = QPushButton("Список покупок")
        shopping_btn.clicked.connect(self.generate_shopping_list)
        
        back_btn = QPushButton("На главную")
        back_btn.clicked.connect(self.parent.show_home)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(shopping_btn)
        button_layout.addWidget(back_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.load_weekly_menu()
    
    def load_weekly_menu(self):
        self.calendar.setSelectedDate(QDate.currentDate())
        self.load_day_menu()
    
    def load_day_menu(self):
        selected_date = self.calendar.selectedDate()
        self.day_menu_label.setText(f"Меню на {selected_date.toString('dd.MM.yyyy')}")
        
        repo = DataRepository.instance()
        self.menu_list.clear()
        
        for date, meal_type, recipe in repo.get_weekly_menu():
            if date == selected_date.toString("yyyy-MM-dd"):
                self.menu_list.addItem(f"{meal_type}: {recipe.title}")
    
    def add_to_menu(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.parent.show_info_message("Функция добавления в меню будет реализована в следующей версии")
    
    def generate_shopping_list(self):
        self.parent.show_info_message("Список покупок сгенерирован и сохранён")

class ProfileView(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Мой профиль")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ваше имя")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        
        settings_label = QLabel("Настройки:")
        settings_label.setStyleSheet("font-weight: bold;")
        
        self.notifications_check = QCheckBox("Получать уведомления")
        self.notifications_check.setChecked(True)
        
        save_btn = QPushButton("Сохранить изменения")
        save_btn.clicked.connect(self.save_profile)
        
        logout_btn = QPushButton("Выйти из аккаунта")
        logout_btn.clicked.connect(self.logout)
        
        back_btn = QPushButton("На главную")
        back_btn.clicked.connect(self.parent.show_home)
        
        layout.addWidget(QLabel("Имя:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)
        layout.addWidget(settings_label)
        layout.addWidget(self.notifications_check)
        layout.addWidget(save_btn)
        layout.addWidget(logout_btn)
        layout.addWidget(back_btn)
        
        self.setLayout(layout)
    
    def save_profile(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        
        if not name:
            self.parent.show_error_message("Введите ваше имя")
            return
        
        self.parent.show_success_message("Профиль успешно сохранён")
    
    def logout(self):
        reply = QMessageBox.question(
            self, 'Выход', 
            'Вы уверены, что хотите выйти из аккаунта?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.parent.show_home()
            self.parent.show_info_message("Вы успешно вышли из аккаунта")

# ==================== ГЛАВНОЕ ОКНО ====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Кулинарный справочник")
        self.setGeometry(100, 100, 1024, 768)
        
        self.stack = QStackedWidget()
        
        self.home_view = HomeView(self)
        self.recipes_view = RecipesView(self)
        self.menu_view = MenuView(self)
        self.profile_view = ProfileView(self)
        self.recipe_detail_view = RecipeDetailView(self)
        self.add_recipe_view = AddRecipeView(self)
        
        self.stack.addWidget(self.home_view)
        self.stack.addWidget(self.recipes_view)
        self.stack.addWidget(self.menu_view)
        self.stack.addWidget(self.profile_view)
        self.stack.addWidget(self.recipe_detail_view)
        self.stack.addWidget(self.add_recipe_view)
        
        self.setCentralWidget(self.stack)
        self.show_home()
    
    def show_home(self):
        self.stack.setCurrentWidget(self.home_view)
    
    def show_recipes(self):
        self.recipes_view.load_recipes()
        self.stack.setCurrentWidget(self.recipes_view)
    
    def show_menu(self):
        self.menu_view.load_weekly_menu()
        self.stack.setCurrentWidget(self.menu_view)
    
    def show_profile(self):
        self.stack.setCurrentWidget(self.profile_view)
    
    def show_recipe_detail(self, recipe_id):
        self.recipe_detail_view.load_recipe(recipe_id)
        self.stack.setCurrentWidget(self.recipe_detail_view)
    
    def show_add_recipe(self):
        self.add_recipe_view.clear_form()
        self.stack.setCurrentWidget(self.add_recipe_view)
    
    def show_error_message(self, message):
        QMessageBox.critical(self, "Ошибка", message)
    
    def show_success_message(self, message):
        QMessageBox.information(self, "Успешно", message)
    
    def show_info_message(self, message):
        QMessageBox.information(self, "Информация", message)
    
    def show_confirm_dialog(self, title, message):
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply == QMessageBox.Yes

# ==================== ЗАПУСК ПРИЛОЖЕНИЯ ====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Установка стиля для всего приложения
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())