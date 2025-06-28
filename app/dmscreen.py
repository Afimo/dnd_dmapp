from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QProgressBar, QStyleFactory, QSpacerItem,
    QRadioButton, QPushButton, QLineEdit, QHBoxLayout, QButtonGroup, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QObject
from PySide6.QtGui import QMovie

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QListWidget, QListWidgetItem

class HeroConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Who are the heroes of this story?')
        self.heroes = {}

        self.layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Name')
        self.health_input = QLineEdit()
        self.health_input.setPlaceholderText('Max health')

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.health_input)

        self.add_button = QPushButton('Add Hero')
        self.add_button.clicked.connect(self.add_hero)

        self.hero_list = QListWidget()

        self.done_button = QPushButton('Let the story unfold...')
        self.done_button.clicked.connect(self.accept)

        self.layout.addLayout(input_layout)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.hero_list)
        self.layout.addWidget(self.done_button)

        self.setLayout(self.layout)

class PlayerCharacters(): #TODO: Use class or db
    def init(self, hero_config):
        super().__init__()

        self.init_heroes = hero_config
        self.pc_map: list[dict] = []
    
    def get_pc_map(self) -> dict:
        return self.pc_map
    

    def add_hero(self):
        name = self.name_input.text().strip()
        health_text = self.health_input.text().strip()
        if name and health_text.isdigit():
            health = int(health_text)
            self.heroes[name] = health
            self.hero_list.addItem(f'{name}: {health}')
            self.name_input.clear()
            self.health_input.clear()

    def get_heroes(self):
        return self.heroes



class CharacterWindow(QWidget):
    def __init__(self, pcs):
        super().__init__()
        self.setWindowTitle('Characters and Health')
        self.pc_health_bars = {}  
        self.npc_labels = {}  
        self.max_health = {}  
        self.deathscreen_widget = None

        self.layout = QVBoxLayout()
        self.npc_layout = QHBoxLayout()
        self.npc_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.pcs = pcs
        
        self.npcs = {
            # "one": 10,
        }
        self.create_health_bars()

        self.layout.addLayout(self.npc_layout)
        self.setLayout(self.layout)
        self.adjustSize()
    
    def create_health_bars(self):
        if self.pcs:
            for name, health in self.pcs.items():
                self.add_health_bar(name, health, is_pc=True)
        
        if self.npcs:
            for name, health in self.npcs.items():
                self.add_health_bar(name, health, is_pc=False)

    def add_health_bar(self, name, health, is_pc):
        h_layout = QHBoxLayout()

        if is_pc:
            pc_label = QLabel(f"{name}")
            pc_label.setStyleSheet('color : orange; font-size: 20pt;')
            health_bar = QProgressBar()
            health_bar.setMaximum(health)  
            health_bar.setValue(health)
            health_bar.setAlignment(Qt.AlignCenter)
            health_bar.setTextVisible(False)

            h_layout.addWidget(pc_label)
            h_layout.addWidget(health_bar)
            self.pc_health_bars[name] = health_bar  
        else:
            npc_label = QLabel(name)
            npc_label.setAlignment(Qt.AlignCenter)
            self.npc_labels[name] = npc_label  
            self.npc_layout.addWidget(npc_label)

        self.layout.addLayout(h_layout)
        self.layout.update()

        self.max_health[name] = health
        
        self.update_health_color(name, health)

    def update_npc_health(self, npc_name, npc_health):
        self.update_health_color(npc_name, npc_health)

        if npc_health == 0:
            self.remove_npc(npc_name)

    def update_pc_health(self, pc_name, pc_health):
        health_bar = self.pc_health_bars[pc_name]
        health_bar.setValue(pc_health)
        self.update_health_color(pc_name, pc_health)

    def update_health_color(self, name, health):
        max_health = self.max_health[name]
        percent_health = (health / max_health) * 100
        
        if percent_health < 30:
            color = "red"
            npc_color = 'red'
        elif percent_health < 70:
            color = "orange"
            npc_color = 'green'
        else:
            color = "green"
            npc_color = 'green'
        
        if name in self.pc_health_bars:
            health_bar = self.pc_health_bars[name]
            health_bar.setStyleSheet(f"QProgressBar::chunk {{background-color: {color};}}")
        else:
            npc_label = self.npc_labels[name]
            npc_label.setStyleSheet(f"color: {npc_color}; font-size: 15pt;")

    def add_npc(self, name, health):
        if name not in self.npcs:
            self.npcs[name] = int(health)
            self.add_health_bar(name, int(health), is_pc=False)

    def remove_npc(self, name):
        if name in self.npcs:
            self.npcs.pop(name)  
            self.max_health.pop(name)  
            if name in self.npc_labels:
                npc_label = self.npc_labels.pop(name)
                for i in range(self.layout.count()):
                    item = self.layout.itemAt(i)
                    if item and item.layout():
                        sub_layout = item.layout()
                        for j in range(sub_layout.count()):
                            widget = sub_layout.itemAt(j).widget()
                            if widget == npc_label:
                                sub_layout.removeWidget(widget)
                                widget.deleteLater()
                                break
                self.update()  

    def init_deathscreen(self, init: bool):
        if init:
            if not self.deathscreen_widget:  
                self.deathscreen_widget = QLabel()
                movie = QMovie('resources/im-waiting.gif')
                self.deathscreen_widget.setMovie(movie)
                movie.start()
                self.layout.addWidget(self.deathscreen_widget)
        else:
            if self.deathscreen_widget: 
                self.layout.removeWidget(self.deathscreen_widget)
                self.deathscreen_widget.deleteLater()  
                self.deathscreen_widget = None
        self.update()  


class ControlWindow(QWidget):
    def __init__(self, character_window, edit_window):
        super().__init__()
        self.setWindowTitle('Control Panel')
        self.character_window = character_window
        
        layout = QGridLayout()

        self.npc_name = QLineEdit()
        self.npc_name.setPlaceholderText('Enter new NPC name')
        layout.addWidget(self.npc_name, 0, 0)

        self.npc_health = QLineEdit()
        self.npc_health.setPlaceholderText('Enter NPC health')
        layout.addWidget(self.npc_health, 1, 0)
        
        self.add_npc_button = QPushButton('Add NPC')
        self.add_npc_button.clicked.connect(self.add_npc)
        layout.addWidget(self.add_npc_button, 2, 0)

        self.remove_npc_button = QPushButton('Remove NPC')
        self.remove_npc_button.clicked.connect(self.remove_npc)
        layout.addWidget(self.remove_npc_button, 0, 7)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('Enter health change')
        self.input_field.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        layout.addWidget(self.input_field, 0, 3, 1, 3)

        self.damage_button = QPushButton('Damage')
        self.damage_button.clicked.connect(self.apply_damage)
        layout.addWidget(self.damage_button, 1, 3)
        
        self.heal_button = QPushButton('Heal')
        self.heal_button.clicked.connect(self.apply_heal)
        layout.addWidget(self.heal_button, 1, 4)
        self.character_buttons = {}
        self.button_group = QButtonGroup(self)

        self.edit_button = QPushButton(text = 'Edit Players')
        layout.addWidget(self.edit_button, 0, 1)
        self.edit_button.clicked.connect(self.open_edit_window) # EDIT
        
        layout.addWidget(QLabel('Player Characters'), 1, 1)
        self.pc_row = 2
        for name in self.character_window.pcs.keys():
            radio_button = QRadioButton(f'{name} (PC)')
            radio_button.setStyleSheet('color: orange')
            layout.addWidget(radio_button, self.pc_row, 1)
            self.character_buttons[name] = radio_button
            self.button_group.addButton(radio_button)
            self.pc_row += 1
        
        layout.addWidget(QLabel('NPCs'), 0, 6)
        self.next_npc_row = 1 
        self.free_npc_rows = [] 
        self.npc_row_map = {}  

        for name in self.character_window.npcs.keys():
            radio_button = QRadioButton(name)
            layout.addWidget(radio_button, self.next_npc_row, 6)
            self.character_buttons[name] = radio_button
            self.button_group.addButton(radio_button)
            self.next_npc_row += 1 
        

        self.setLayout(layout)

    def open_edit_window(self) -> None:
        if edit_window.exec() == QDialog.Accepted:
            edit_window.destroy()

    def get_selected_character(self):
        for name, button in self.character_buttons.items():
            if button.isChecked():
                return name
        return None

    def add_npc(self):
        name = self.npc_name.text().strip()
        health = self.npc_health.text().strip()
        
        if name and health.isdigit() and name not in self.character_buttons:
            self.character_window.add_npc(name, int(health))

            # Pick a row: reuse or assign new
            if self.free_npc_rows:
                row = self.free_npc_rows.pop(0)
            else:
                row = self.next_npc_row
                self.next_npc_row += 1

            radio_button = QRadioButton(f'{name} -- {self.get_character_health(name)}')
            self.layout().addWidget(radio_button, row, 6)

            self.character_buttons[name] = radio_button
            self.npc_row_map[name] = row
            self.button_group.addButton(radio_button)

            self.npc_name.clear()
            self.npc_health.clear()


    def remove_npc(self, name=False):
        if name:
            selected_character = name
        else:
            selected_character = self.get_selected_character()

        if selected_character and selected_character in self.character_window.npcs:
            self.character_window.remove_npc(selected_character)

            radio_button = self.character_buttons.pop(selected_character, None)
            self.free_npc_rows.append(self.npc_row_map.pop(selected_character, None))
            self.free_npc_rows.sort()
                
            if radio_button:
                self.layout().removeWidget(radio_button)  
                radio_button.deleteLater()
                
        self.input_field.clear()
        self.npc_name.clear()
        self.npc_health.clear()
        
        self.update()

    
    def apply_damage(self):
        if not self.input_field.text().isdigit():
            return  # Prevent crashes

        selected_character = self.get_selected_character()
        if selected_character:
            damage = int(self.input_field.text())
            current_health = self.get_character_health(selected_character)
            new_health = max(0, current_health - damage)

            if new_health <= 0:
                self.remove_npc(selected_character)
                self.update_character_health(selected_character, new_health)
                if selected_character in self.character_window.pcs.keys():
                    self.character_window.init_deathscreen(True)
            else:
                self.update_character_health(selected_character, new_health)
                
        self.input_field.clear()
        self.npc_name.clear()
        self.npc_health.clear()
        
        if selected_character in self.character_window.npcs:
            old_radio_button = self.character_buttons.pop(selected_character, None)
            old_radio_button.deleteLater()
            
            new_radio_button = QRadioButton(f'{selected_character} -- {new_health}')
            self.layout().addWidget(new_radio_button, self.npc_row_map[selected_character], 5)
            self.character_buttons[selected_character] = new_radio_button



    def apply_heal(self):
        if not self.input_field.text().isdigit():
            return  # Prevent crashes

        selected_character = self.get_selected_character()
        if selected_character:
            heal = int(self.input_field.text())
            current_health = self.get_character_health(selected_character)
            max_health = self.character_window.max_health[selected_character]
            new_health = min(max_health, current_health + heal)
            self.update_character_health(selected_character, new_health)

            if current_health <= 0:
                self.character_window.init_deathscreen(False)
                
        self.input_field.clear()
        self.npc_name.clear()
        self.npc_health.clear()

        if selected_character in self.character_window.npcs:
            old_radio_button = self.character_buttons.pop(selected_character, None)
            old_radio_button.deleteLater()
            
            new_radio_button = QRadioButton(f'{selected_character} -- {new_health}')
            self.layout().addWidget(new_radio_button, self.npc_row_map[selected_character], 5)
            self.character_buttons[selected_character] = new_radio_button


    def get_character_health(self, name):
        if name in self.character_window.pcs:
            return self.character_window.pcs[name]
        else:
            return self.character_window.npcs[name]

    def update_character_health(self, name, new_health):
        if name in self.character_window.pcs:
            self.character_window.pcs[name] = new_health
            self.character_window.update_pc_health(name, new_health)
        else:
            self.character_window.npcs[name] = new_health
            self.character_window.update_npc_health(name, new_health)


class EditWindow(QDialog):
    def __init__(self, pcs):
        super().__init__()
        self.setWindowTitle('Edit Heroes')
        self.heroes = pcs

        self.layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Name')
        self.health_input = QLineEdit()
        self.health_input.setPlaceholderText('Max health')

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.health_input)

        self.add_button = QPushButton('Add Hero')
        self.add_button.clicked.connect(self.add_hero)

        self.hero_list = QListWidget()
        for name,health in self.heroes.items():
            self.hero_list.addItem(f'{name} : {health}')

        self.done_button = QPushButton('Let the story continue...')
        self.done_button.clicked.connect(self.accept)

        self.layout.addLayout(input_layout)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.hero_list)
        self.layout.addWidget(self.done_button)

        self.setLayout(self.layout)
        
    def add_hero(self):
        name = self.name_input.text().strip()
        health_text = self.health_input.text().strip()
        if name and health_text.isdigit():
            health = int(health_text)
            self.heroes[name] = health
            self.hero_list.addItem(f'{name}: {health}')
            self.name_input.clear()
            self.health_input.clear()

    def get_heroes(self):
        return self.heroes

if __name__ == "__main__":
    app = QApplication([])
    app.setStyle(QStyleFactory.create('fusion'))

    config_dialog = HeroConfigDialog()
    if config_dialog.exec() == QDialog.Accepted:
        hero_config = config_dialog.get_heroes()
        #TODO: Add Save option and editing of characters!
        if not hero_config:
            raise RuntimeError('Error: No heroes created!')
            exit(1)
        
        character_window = CharacterWindow(hero_config)
        character_window.show()

        edit_window = EditWindow(hero_config)
        
        control_window = ControlWindow(character_window, edit_window)
        control_window.show()


    
    app.exec()
