import sys
import json
import openai
import os
import base64
import requests
from PyQt5.QtWidgets import (
    QApplication, QFrame, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QComboBox, QLineEdit, QTextEdit, QFileDialog, QMessageBox, QInputDialog
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from urllib.request import urlopen

# muse code file imports
from image_saver import ImageSaver
from constants import API_KEY_FILE, DALLE_API_ENDPOINT, CHAT_API_ENDPOINT, GPT_IMAGE_API_ENDPOINT
from api_key_manager import APIKeyManager

# main
class OpenAIGUI(QMainWindow, ImageSaver):
    def __init__(self):
        super().__init__()
        self.api_key_manager = APIKeyManager(self)
        self.initUI()
        self.encoded_image = None  # Attribute to store the base64 encoded image
        self.image_analysis_result = None  # Attribute to store image analysis result

    def initUI(self):
        self.setWindowTitle('OpenAI Integration GUI')
        self.setGeometry(100, 100, 1000, 600)

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        self.image_layout = QVBoxLayout()
        main_layout.addLayout(self.image_layout)

        self.uploaded_image_label = QLabel("Uploaded Image")
        self.configure_image_label(self.uploaded_image_label)
        self.generated_image_label = QLabel("Generated Image")
        self.configure_image_label(self.generated_image_label)

        self.image_layout.addWidget(self.uploaded_image_label)  # Moved the uploaded image label here

        self.add_button("Upload Image", self.upload_image, self.image_layout)  # Added upload button

        self.image_layout.addWidget(self.generated_image_label)  # Moved the generated image label here

        self.interaction_layout = QVBoxLayout()
        main_layout.addLayout(self.interaction_layout)

        self.model_label = QLabel("Select Model:")
        self.interaction_layout.addWidget(self.model_label)

        self.model_combo = QComboBox()
        models = [
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-4-turbo",
            "gpt-3.5-turbo-16k",
            "dalle-3",
            "gpt-4o"
        ]
        self.model_combo.addItems(models)
        self.interaction_layout.addWidget(self.model_combo)

        self.prompt_entry = QLineEdit()
        self.interaction_layout.addWidget(self.prompt_entry)

        self.size_dropdown = QComboBox()
        self.size_dropdown.addItems(["1024x1024", "1024x1792", "1792x1024"])
        self.interaction_layout.addWidget(self.size_dropdown)

        self.quality_dropdown = QComboBox()
        self.quality_dropdown.addItems(["standard", "hd"])
        self.interaction_layout.addWidget(self.quality_dropdown)

        buttons_layout = QHBoxLayout()
        self.add_button("Analyze Image", self.analyze_image, buttons_layout)
        self.add_button("Generate Image", self.generate_dalle_image, buttons_layout)
        self.add_button("ChatGPT Send", self.chat_with_gpt, buttons_layout)
        self.interaction_layout.addLayout(buttons_layout)

        self.add_button("Save Generated Image", self.save_generated_image, self.image_layout)

        self.response_text = QTextEdit()
        self.interaction_layout.addWidget(self.response_text)

    def configure_image_label(self, label):
        label.setFrameStyle(QFrame.Sunken | QFrame.StyledPanel)
        label.setAlignment(Qt.AlignCenter)
        label.setFixedSize(200, 200)
        self.image_layout.addWidget(label)

    def add_button(self, text, handler, layout):
        button = QPushButton(text)
        button.clicked.connect(handler)
        layout.addWidget(button)

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.display_image(file_path, self.uploaded_image_label)

    def display_image(self, file_path, image_label):
        image = QImage(file_path)
        pixmap = QPixmap.fromImage(image)
        pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(pixmap)
        self.encoded_image = self.encode_image(file_path)

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_image(self):
        if self.encoded_image:
            self.perform_image_analysis(self.encoded_image)
        else:
            QMessageBox.warning(self, "Warning", "Please upload an image first.")

    def perform_image_analysis(self, base64_image):
        headers = {"Authorization": f"Bearer {self.api_key_manager.api_key}"}
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What’s in this image?"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            "max_tokens": 1000
        }
        try:
            response = requests.post(CHAT_API_ENDPOINT, headers=headers, json=payload)
            if response.status_code == 200 and 'choices' in response.json():
                description = response.json()['choices'][0]['message']['content']
                self.response_text.append(description + "\n\n")
                self.image_analysis_result = description
            else:
                self.response_text.append("Failed to analyze the image.\n\n")
        except Exception as e:
            self.response_text.append(f"An error occurred: {e}\n\n")

    def generate_dalle_image(self):
        # Ensure the API key is set (assuming self.api_key_manager is your APIKeyManager instance)
        if not self.api_key_manager.api_key:
            self.append_response("API key is not set. Please set the API key and try again.")
            return

        # Explicitly set the API key (optional if APIKeyManager already does this)
        openai.api_key = self.api_key_manager.api_key
        prompt, size, quality = self.prompt_entry.text(), self.size_dropdown.currentText(), self.quality_dropdown.currentText()
        try:
            response = openai.Image.create(model="dall-e-3", prompt=prompt, size=size, quality=quality, n=1)
            if response.data:
                self.display_dalle_image(response.data[0].url, self.generated_image_label)
            else:
                self.append_response("Failed to generate image or no data returned.")
        except Exception as e:
            self.append_response(f"An error occurred: {e}")

    def display_dalle_image(self, image_url, image_label):
        try:
            image_data = urlopen(image_url).read()
            image = QImage()
            if image.loadFromData(image_data):
                pixmap = QPixmap.fromImage(image).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(pixmap)
            else:
                self.append_response("Failed to load image data.")
        except Exception as e:
            self.append_response(f"Failed to display image: {e}")

    def append_response(self, message):
        self.response_text.append(f"{message}\n\n")

    def chat_with_gpt(self):
        prompt = self.prompt_entry.text()
        model = self.model_combo.currentText()  # Get the selected model
        chat_history = [{"role": "system", "content": "Image analysis: " + self.image_analysis_result}] if self.image_analysis_result else []
        chat_history.append({"role": "user", "content": prompt})

        headers = {"Authorization": f"Bearer {self.api_key_manager.api_key}"}
        payload = {"model": model, "messages": chat_history, "max_tokens": 2000}

        try:
            response = requests.post(CHAT_API_ENDPOINT, headers=headers, json=payload).json()
            chat_response = response.get('choices', [{}])[0].get('message', {}).get('content', "Failed to get a response.")
            self.response_text.append(f"{chat_response}\n\n")
        except Exception as e:
            self.response_text.append(f"An error occurred: {e}\n\n")

def main():
    app = QApplication(sys.argv)
    ex = OpenAIGUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
