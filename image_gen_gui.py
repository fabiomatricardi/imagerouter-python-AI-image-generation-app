import sys
import json
import os
import requests
from PIL import Image
from io import BytesIO
import random
import string
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox,
                               QSpinBox, QTextEdit, QFileDialog, QMessageBox, QProgressBar)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QPixmap, QFont

def generate_random_filename():
    timestamp = int(time.time())
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"image_{timestamp}_{random_str}.png"

class ApiWorker(QThread):
    image_generated = Signal(str, str)  # filename, preview_path
    error_occurred = Signal(str)

    def __init__(self, api_key, prompt, model, size):
        super().__init__()
        self.api_key = api_key
        self.prompt = prompt
        self.model = model
        self.size = size

    def run(self):
        url = "https://api.imagerouter.io/v1/openai/images/generations"
        payload = {
            "prompt": self.prompt,
            "model": self.model,
            "quality": "auto",
            "size": self.size,
            "response_format": "url",
            "output_format": "png"
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            data = response.json()
            if 'data' in data and data['data']:
                image_url = data['data'][0]['url']
                img_resp = requests.get(image_url, timeout=30)
                img_resp.raise_for_status()
                img = Image.open(BytesIO(img_resp.content))
                filename = generate_random_filename()
                img.save(filename)
                preview_path = filename  # Temp use same for preview
                self.image_generated.emit(filename, preview_path)
            else:
                self.error_occurred.emit(json.dumps(data, indent=2))
        except Exception as e:
            self.error_occurred.emit(str(e))

class ImageGenApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_key = ""
        self.load_config()
        self.init_ui()
        if not self.api_key:
            self.show_settings_tab()

    def load_config(self):
        config_path = "config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                data = json.load(f)
                self.api_key = data.get('api_key', '')
        else:
            self.api_key = ''
            self.save_config()

    def save_config(self):
        config_path = "config.json"
        data = {'api_key': self.api_key}
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)

    def init_ui(self):
        self.setWindowTitle("ImageRouter.io Generator")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("QMainWindow { background-color: #f0f0f0; }")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        tabs = QTabWidget()
        self.main_tab = self.create_main_tab()
        self.settings_tab = self.create_settings_tab()
        tabs.addTab(self.main_tab, "Generate")
        tabs.addTab(self.settings_tab, "Settings")
        layout.addWidget(tabs)

        self.preview_label = QLabel("Generated image will appear here")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background: white;")
        layout.addWidget(self.preview_label)

    def create_main_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Enter your image prompt here...")
        self.prompt_edit.setFont(QFont("Arial", 10))
        layout.addWidget(QLabel("Prompt:"))
        layout.addWidget(self.prompt_edit)

        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_list = [
            'black-forest-labs/FLUX-2-klein-4b:free',
            'black-forest-labs/FLUX-1-schnell:free',
            'stabilityai/sdxl-turbo:free',
            'openai/gpt-image-1.5:free',
            'Tongyi-MAI/Z-Image-Turbo:free',
            'HiDream-ai/HiDream-I1-Full:free',
            'lodestones/Chroma:free',
            'qwen/qwen-image:free'
        ]
        self.model_combo.addItems(self.model_list)
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Width:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(512, 1024)
        self.width_spin.setSingleStep(64)
        self.width_spin.setValue(1024)
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(QLabel("Height:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(512, 1024)
        self.height_spin.setSingleStep(64)
        self.height_spin.setValue(640)
        size_layout.addWidget(self.height_spin)
        layout.addLayout(size_layout)

        self.generate_btn = QPushButton("Generate Image")
        self.generate_btn.clicked.connect(self.generate_image)
        self.generate_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; }")
        layout.addWidget(self.generate_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.save_btn = QPushButton("Save As...")
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setEnabled(False)
        layout.addWidget(self.save_btn)

        return tab

    def create_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(QLabel("API Key (from imagerouter.io):"))
        self.api_key_edit = QLineEdit(self.api_key)
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.api_key_edit)

        save_btn = QPushButton("Save Config")
        save_btn.clicked.connect(self.save_api_key)
        layout.addWidget(save_btn)

        status_label = QLabel("Config loaded from config.json")
        if not self.api_key:
            status_label.setText("No API key found. Add one above.")
            status_label.setStyleSheet("color: red;")
        layout.addWidget(status_label)

        return tab

    def show_settings_tab(self):
        self.centralWidget().layout().itemAt(0).widget().setCurrentIndex(1)

    def save_api_key(self):
        self.api_key = self.api_key_edit.text().strip()
        self.save_config()
        QMessageBox.information(self, "Saved", "API key saved to config.json")
        self.generate_btn.setEnabled(bool(self.api_key))

    def generate_image(self):
        if not self.api_key:
            QMessageBox.warning(self, "Error", "Set API key in Settings first.")
            return
        prompt = self.prompt_edit.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Error", "Enter a prompt.")
            return
        model = self.model_combo.currentText()
        w = self.width_spin.value()
        h = self.height_spin.value()
        size = f"{w}x{h}"

        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate

        self.worker = ApiWorker(self.api_key, prompt, model, size)
        self.worker.image_generated.connect(self.on_image_generated)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()

    def on_image_generated(self, filename, preview_path):
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        self.current_filename = filename
        pixmap = QPixmap(preview_path).scaled(self.preview_label.size(), Qt.KeepAspectRatio)
        self.preview_label.setPixmap(pixmap)
        self.save_btn.setEnabled(True)
        self.open_image(filename)
        QMessageBox.information(self, "Success", f"Saved: {filename}")

    def on_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"API Error:\n{error_msg}")

    def save_image(self):
        if hasattr(self, 'current_filename'):
            path, _ = QFileDialog.getSaveFileName(self, "Save Image", self.current_filename, "PNG (*.png)")
            if path:
                Image.open(self.current_filename).save(path)

    def open_image(self, filename):
        img = Image.open(filename)
        img.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageGenApp()
    window.show()
    sys.exit(app.exec())
