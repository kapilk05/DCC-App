import sys
import requests
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QListWidget, QInputDialog, QMessageBox, QComboBox, QFormLayout, QDialog, QLineEdit
)
from PyQt5.QtCore import pyqtSignal, QObject

FLASK_URL = "http://127.0.0.1:5000"

class SignalEmitter(QObject):
    update_inventory_signal = pyqtSignal(list)
    show_message_signal = pyqtSignal(str, str)

class ItemDialog(QDialog):
    def __init__(self, title, max_qty=10, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.layout = QFormLayout(self)
        
        self.item_name = QLineEdit(self)
        self.quantity = QComboBox(self)
        self.quantity.addItems([str(i) for i in range(1, max_qty + 1)])
        
        self.layout.addRow("Item Name:", self.item_name)
        self.layout.addRow("Quantity:", self.quantity)
        
        self.buttons = QPushButton("OK", self)
        self.buttons.clicked.connect(self.accept)
        self.layout.addWidget(self.buttons)
    
    def get_values(self):
        return self.item_name.text(), int(self.quantity.currentText())

class InventoryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management")
        self.setGeometry(100, 100, 450, 350)
        
        self.layout = QVBoxLayout()
        self.item_list = QListWidget()
        self.refresh_button = QPushButton("🔄 Refresh Inventory")
        self.buy_button = QPushButton("🛒 Buy Item")
        self.return_button = QPushButton("↩️ Return Item")
        
        self.layout.addWidget(QLabel("📦 Inventory:"))
        self.layout.addWidget(self.item_list)
        self.layout.addWidget(self.refresh_button)
        self.layout.addWidget(self.buy_button)
        self.layout.addWidget(self.return_button)
        self.setLayout(self.layout)

        self.refresh_button.clicked.connect(self.fetch_inventory)
        self.buy_button.clicked.connect(self.buy_item)
        self.return_button.clicked.connect(self.return_item)

        self.signals = SignalEmitter()
        self.signals.update_inventory_signal.connect(self.update_inventory_ui)
        self.signals.show_message_signal.connect(self.show_message)

        self.inventory_data = {}
        self.fetch_inventory()

    def fetch_inventory(self):
        threading.Thread(target=self._fetch_inventory_thread, daemon=True).start()

    def _fetch_inventory_thread(self):
        try:
            response = requests.get(f"{FLASK_URL}/get-inventory")
            if response.status_code == 200:
                data = response.json()
                self.inventory_data = {item["name"]: item["quantity"] for item in data}
                self.signals.update_inventory_signal.emit(data)
            else:
                self.signals.show_message_signal.emit("Error", "Could not fetch inventory")
        except Exception as e:
            self.signals.show_message_signal.emit("Error", str(e))

    def update_inventory_ui(self, data):
        self.item_list.clear()
        for item in data:
            self.item_list.addItem(f"{item['name']} - {item['quantity']}")

    def buy_item(self):
        dialog = ItemDialog("Buy Item", 10, self)
        if dialog.exec_():
            item_name, quantity = dialog.get_values()
            if item_name:
                threading.Thread(target=self._buy_item_request, args=(item_name, quantity), daemon=True).start()

    def _buy_item_request(self, item_name, quantity):
        try:
            data = {"name": item_name, "quantity": quantity}
            response = requests.post(f"{FLASK_URL}/add-item", json=data)
            message = response.json().get("message", "Item added!")
            self.signals.show_message_signal.emit("Success", message)
            self.fetch_inventory()
        except Exception as e:
            self.signals.show_message_signal.emit("Error", str(e))

    def return_item(self):
        if not self.inventory_data:
            self.signals.show_message_signal.emit("Error", "No items in inventory")
            return
        
        dialog = ItemDialog("Return Item", 10, self)
        if dialog.exec_():
            item_name, return_qty = dialog.get_values()
            if item_name not in self.inventory_data:
                self.signals.show_message_signal.emit("Error", "Can't return item you haven't bought")
                return
            
            max_qty = self.inventory_data[item_name]
            if return_qty > max_qty:
                self.signals.show_message_signal.emit("Error", "Cannot return more than purchased")
                return
            
            threading.Thread(target=self._return_item_request, args=(item_name, return_qty), daemon=True).start()

    def _return_item_request(self, item_name, quantity):
        try:
            data = {"name": item_name, "quantity": quantity}
            response = requests.post(f"{FLASK_URL}/remove-item", json=data)
            if response.status_code == 200:
                updated_quantity = self.inventory_data.get(item_name, 0) - quantity
                if updated_quantity > 0:
                    self.inventory_data[item_name] = updated_quantity
                else:
                    del self.inventory_data[item_name]
                    self.signals.show_message_signal.emit("Info", f"{item_name} removed from inventory.")
                
                self.fetch_inventory()
            else:
                self.signals.show_message_signal.emit("Error", "Error updating item!")
        except Exception as e:
            self.signals.show_message_signal.emit("Error", str(e))

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventoryApp()
    window.show()
    sys.exit(app.exec_())
