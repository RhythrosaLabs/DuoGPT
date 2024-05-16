import sys
import json
import os
import requests
import re
import threading
import zipfile
import pandas as pd
from io import BytesIO
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QComboBox, QInputDialog, QFrame, QMainWindow, QStatusBar
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QMetaObject, Q_ARG
from PIL import Image
from teams import TEAMS  # Import teams from the teams.py module

# OpenAI setup
CHAT_API_URL = "https://api.openai.com/v1/chat/completions"
DALLE3_API_URL = "https://api.openai.com/v1/images/generations"

API_KEY_FILE = "api_key.json"

HEADERS = {
    "Authorization": "",
    "Content-Type": "application/json"
}

class GPTALL:
    def __init__(self, api_key):
        self.api_key = api_key
        HEADERS["Authorization"] = f"Bearer {self.api_key}"

    def generate_response(self, prompt, model="gpt-3.5-turbo"):
        data = {
            "model": model,
            "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}]
        }
        try:
            response = requests.post(CHAT_API_URL, headers=HEADERS, json=data)
            response.raise_for_status()
            response_data = response.json()
            if "choices" not in response_data:
                error_message = response_data.get("error", {}).get("message", "Unknown error")
                print(f"Error from OpenAI API: {error_message}")
                return f"Error: {error_message}"
            return response_data["choices"][0]["message"]["content"]
        except requests.RequestException as e:
            print(f"Request error: {e}")
            return "Error: Unable to communicate with the OpenAI API."

    def generate_image(self, prompt):
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024"
        }
        try:
            response = requests.post(DALLE3_API_URL, headers=HEADERS, json=data)
            response.raise_for_status()
            response_data = response.json()
            if "data" not in response_data:
                error_message = response_data.get("error", {}).get("message", "Unknown error")
                print(f"Error from DALL-E API: {error_message}")
                return f"Error: {error_message}"
            image_url = response_data["data"][0]["url"]
            return image_url
        except requests.RequestException as e:
            print(f"Request error: {e}")
            return "Error: Unable to communicate with the DALL-E API."

class ChatGPTConvoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT Convo with Function Calls")
        self.api_key = self.load_api_key()
        if not self.api_key:
            self.api_key = self.ask_api_key()
            if not self.api_key:
                QMessageBox.critical(self, "Error", "API key is required to proceed.")
                sys.exit()
            self.save_api_key(self.api_key)

        global HEADERS
        HEADERS = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        self.history = []
        self.initUI()
        self.convo_thread = None
        self.stop_thread_flag = False
        self.generated_images = []

    def initUI(self):
        main_layout = QHBoxLayout(self)

        # Status Bar
        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)

        # Left Column - Team Chat
        self.left_layout = QVBoxLayout()
        self.team_mode_label = QLabel("Team Mode")
        self.team_mode_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.team_mode_label.setToolTip("Select the team for the conversation")
        self.left_layout.addWidget(self.team_mode_label)

        self.team_combo = QComboBox()
        for category, teams in TEAMS.items():
            for team in teams:
                self.team_combo.addItem(f"{category}/{team}")
        self.team_combo.setToolTip("Select a team to work with")
        self.left_layout.addWidget(self.team_combo)

        self.prompt_label = QLabel("Initial User Prompt:")
        self.prompt_label.setToolTip("Enter the initial prompt for the conversation")
        self.left_layout.addWidget(self.prompt_label)
        self.prompt_entry = QLineEdit()
        self.prompt_entry.setPlaceholderText("Enter your prompt here...")
        self.left_layout.addWidget(self.prompt_entry)
        
        self.start_button = QPushButton("Start")
        self.start_button.setToolTip("Start the conversation with the selected team")
        self.start_button.clicked.connect(self.start_convo)
        self.left_layout.addWidget(self.start_button)

        self.autostop_label = QLabel("Number of Exchanges:")
        self.autostop_label.setToolTip("Set the number of exchanges between bots before stopping")
        self.left_layout.addWidget(self.autostop_label)
        self.autostop_entry = QLineEdit()
        self.autostop_entry.setText("10")
        self.autostop_entry.setToolTip("Enter the number of exchanges (default is 10)")
        self.left_layout.addWidget(self.autostop_entry)

        self.interject_label = QLabel("Interject Prompt:")
        self.interject_label.setToolTip("Enter a prompt to interject in the conversation")
        self.left_layout.addWidget(self.interject_label)
        self.interject_entry = QLineEdit()
        self.interject_entry.setPlaceholderText("Enter interjection prompt here...")
        self.left_layout.addWidget(self.interject_entry)
        
        self.interject_button = QPushButton("Interject")
        self.interject_button.setToolTip("Interject the conversation with the above prompt")
        self.interject_button.setEnabled(False)
        self.interject_button.clicked.connect(self.interject_convo)
        self.left_layout.addWidget(self.interject_button)

        self.convo_box = QTextEdit()
        self.convo_box.setReadOnly(True)
        self.convo_box.setToolTip("Conversation between bots will be displayed here")
        self.left_layout.addWidget(self.convo_box)

        self.pause_button = QPushButton("Pause")
        self.pause_button.setToolTip("Pause the conversation")
        self.pause_button.clicked.connect(self.pause_convo)
        self.left_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setToolTip("Stop the conversation")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_convo)
        self.left_layout.addWidget(self.stop_button)

        self.save_button = QPushButton("Save Convo")
        self.save_button.setToolTip("Save the current conversation to a file")
        self.save_button.clicked.connect(self.save_convo)
        self.left_layout.addWidget(self.save_button)

        self.organize_button = QPushButton("Organize")
        self.organize_button.setToolTip("Organize the conversation and save it")
        self.organize_button.clicked.connect(self.organize_convo)
        self.left_layout.addWidget(self.organize_button)

        main_layout.addLayout(self.left_layout)

        # Center Divider
        divider = QVBoxLayout()
        divider.addStretch()
        main_layout.addLayout(divider)

        # Add GPT-ALL6 column
        self.gpt_all6_layout = QVBoxLayout()
        self.gpt_all6_frame = QFrame()
        self.gpt_all6_ui = OpenAIGUI()  # Create an instance of the imported class
        self.gpt_all6_frame.setLayout(self.gpt_all6_ui.centralWidget().layout())  # Use its layout

        self.gpt_all6_layout.addWidget(self.gpt_all6_frame)
        main_layout.addLayout(self.gpt_all6_layout)

        self.setLayout(main_layout)

    def load_api_key(self):
        if os.path.exists(API_KEY_FILE):
            with open(API_KEY_FILE, 'r') as file:
                data = json.load(file)
                return data.get('api_key')
        return None

    def save_api_key(self, api_key):
        with open(API_KEY_FILE, 'w') as file:
            json.dump({'api_key': api_key}, file)

    def ask_api_key(self):
        api_key, ok = QInputDialog.getText(self, "API Key", "Please enter your OpenAI API key:", QLineEdit.Password)
        if ok:
            return api_key
        return None

    def start_convo(self):
        try:
            self.max_exchanges = int(self.autostop_entry.text())
        except ValueError:
            self.max_exchanges = 10  # Default value

        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.running = True
        self.paused = False
        self.stop_thread_flag = False
        initial_prompt = self.prompt_entry.text()
        self.messages = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": initial_prompt}]
        self.update_convo_box(f"User: {initial_prompt}")
        self.exchange_count = 0
        self.convo_thread = threading.Thread(target=self.convo_loop)
        self.convo_thread.start()
        self.status_bar.showMessage("Conversation started")

    def update_convo_box(self, message):
        QMetaObject.invokeMethod(self.convo_box, "append", Q_ARG(str, message))

    def pause_convo(self):
        self.paused = True
        self.interject_button.setEnabled(True)
        self.update_convo_box("Conversation paused.")
        self.status_bar.showMessage("Conversation paused")

    def stop_convo(self):
        self.running = False
        self.paused = False
        self.stop_thread_flag = True
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.interject_button.setEnabled(False)
        self.update_convo_box("Conversation stopped.")
        if self.convo_thread:
            self.convo_thread.join()
        self.status_bar.showMessage("Conversation stopped")

    def interject_convo(self):
        interject_prompt = self.interject_entry.text()
        self.messages.append({"role": "user", "content": interject_prompt})
        self.update_convo_box(f"User: {interject_prompt}")
        self.paused = False
        self.interject_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        if self.running:
            self.convo_thread = threading.Thread(target=self.convo_loop)
            self.convo_thread.start()
        self.status_bar.showMessage("Interjection sent")

    def convo_loop(self):
        category, team_name = self.team_combo.currentText().split("/")
        team = TEAMS[category][team_name]
        while self.running and not self.stop_thread_flag and (self.max_exchanges == 0 or self.exchange_count < self.max_exchanges):
            if self.paused:
                continue
            if self.exchange_count % 2 == 0:  # Bot 1's turn
                model = team["bot1"]["model"]
                preset_prompt = team["bot1"]["preset"]
                response = self.ask_openai(self.messages, model, preset_prompt, is_image=(model == "dalle-3"))
                self.update_convo_box(f"Bot 1: {response}\n\n")
                self.messages.append({"role": "assistant", "content": response})
            else:  # Bot 2's turn
                model = team["bot2"]["model"]
                preset_prompt = team["bot2"]["preset"]
                response = self.ask_openai([self.messages[-1]], model, preset_prompt, is_image=(model == "gpt-4-vision-preview"))
                self.update_convo_box(f"Bot 2: {response}\n\n")
                self.messages.append({"role": "assistant", "content": response})
            
            self.exchange_count += 1

        if not self.paused and not self.running:
            self.update_convo_box("Conversation completed.")
            self.status_bar.showMessage("Conversation completed")

    def ask_openai(self, messages, model, preset_prompt, is_image=False):
        if is_image and model == "dalle-3":
            return self.ask_dalle(preset_prompt)
        elif is_image and model == "gpt-4-vision-preview":
            return self.ask_gpt_vision(messages, model, preset_prompt)
        else:
            data = {
                "model": model,
                "messages": [{"role": "system", "content": preset_prompt}] + messages
            }
            try:
                response = requests.post(CHAT_API_URL, headers=HEADERS, json=data)
                response.raise_for_status()
                response_data = response.json()
                if "choices" not in response_data:
                    error_message = response_data.get("error", {}).get("message", "Unknown error")
                    print(f"Error from OpenAI API: {error_message}")
                    return f"Error: {error_message}"

                content = response_data["choices"][0]["message"]["content"]
                return content

            except requests.RequestException as e:
                print(f"Request error: {e}")
                return f"Error: Unable to communicate with the OpenAI API."

    def ask_dalle(self, prompt):
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024"
        }
        try:
            response = requests.post(DALLE3_API_URL, headers=HEADERS, json=data)
            response.raise_for_status()
            response_data = response.json()
            if "data" not in response_data:
                error_message = response_data.get("error", {}).get("message", "Unknown error")
                print(f"Error from DALL-E API: {error_message}")
                return f"Error: {error_message}"

            image_url = response_data["data"][0]["url"]
            return image_url

        except requests.RequestException as e:
            print(f"Request error: {e}")
            return f"Error: Unable to communicate with the DALL-E API."

    def save_image_locally(self, image_url, prompt):
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image_data = response.content
            file_name = re.sub(r'\W+', '_', prompt) + ".png"
            file_path = os.path.join(os.getcwd(), file_name)
            with open(file_path, 'wb') as image_file:
                image_file.write(image_data)
            return file_path
        except Exception as e:
            print(f"Failed to save image: {e}")
            return None

    def display_image(self, chat_box, url):
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            img_data = response.content
            img = QImage()
            img.loadFromData(img_data)
            pixmap = QPixmap(img)
            cursor = chat_box.textCursor()
            cursor.movePosition(cursor.End)
            cursor.insertText('\n')
            cursor.insertImage(pixmap)
            chat_box.setTextCursor(cursor)
        except Exception as e:
            print(f"Failed to load image from {url}: {e}")

    def insert_message_with_image(self, chat_box, message, tag):
        image_url_pattern = re.compile(r'(https?://\S+\.(?:jpg|jpeg|png|gif))')
        image_urls = image_url_pattern.findall(message)

        if image_urls:
            parts = image_url_pattern.split(message)
            for part in parts:
                if image_url_pattern.match(part):
                    # Display image
                    self.display_image(chat_box, part)
                else:
                    self.update_convo_box(part)
        else:
            self.update_convo_box(message)

    def organize_convo(self):
        self.status_bar.showMessage("Organizing conversation...")
        thread = threading.Thread(target=self._organize_convo_thread)
        thread.start()

    def _organize_convo_thread(self):
        try:
            category, team_name = self.team_combo.currentText().split("/")
            if category == "Marketing" and team_name == "Social Media Campaign":
                self.organize_social_media_campaign()
            else:
                organized_text, code_snippets = self.get_organized_text()
                if organized_text:
                    self.create_code_zip(code_snippets)
                    if self.generated_images:
                        self.create_image_zip(self.generated_images)
                    self.download_organized_convo(organized_text)
                self.update_status_bar("Conversation organized successfully", 5000)
        except Exception as e:
            self.update_convo_box(f"Failed to organize conversation: {e}")
            self.update_status_bar("Failed to organize conversation", 5000)

    def update_status_bar(self, message, timeout=0):
        QMetaObject.invokeMethod(self.status_bar, "showMessage", Q_ARG(str, message), Q_ARG(int, timeout))

    def get_organized_text(self):
        full_convo = self.convo_box.toPlainText()
        prompt = f"Organize and structure the following conversation into a cohesive and detailed plan. If there are code snippets, identify and save each as a separate file:\n{full_convo}"
        category, team_name = self.team_combo.currentText().split("/")
        team = TEAMS[category][team_name]
        model = team["bot3"]["model"]
        preset_prompt = team["bot3"]["preset"]
        
        data = {
            "model": model,
            "messages": [{"role": "system", "content": preset_prompt}, {"role": "user", "content": prompt}]
        }

        try:
            response = requests.post(CHAT_API_URL, headers=HEADERS, json=data)
            response.raise_for_status()
            response_data = response.json()
            if "choices" not in response_data:
                error_message = response_data.get("error", {}).get("message", "Unknown error")
                print(f"Error from OpenAI API: {error_message}")
                return f"Error: {error_message}", []

            organized_text = response_data["choices"][0]["message"]["content"]
            
            # Extract code snippets using regex
            code_snippets = re.findall(r'```(.*?)```', organized_text, re.DOTALL)
            
            return organized_text, code_snippets

        except requests.RequestException as e:
            print(f"Request error: {e}")
            return f"Error: Unable to communicate with the OpenAI API.", []

    def create_code_zip(self, code_snippets):
        try:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
                for i, snippet in enumerate(code_snippets, 1):
                    # Infer the file extension if possible
                    language_match = re.match(r'^(\w+)', snippet)
                    if language_match:
                        language = language_match.group(1)
                        if language.lower() in ['python', 'py']:
                            ext = 'py'
                        elif language.lower() in ['javascript', 'js']:
                            ext = 'js'
                        elif language.lower() in ['html']:
                            ext = 'html'
                        elif language.lower() in ['css']:
                            ext = 'css'
                        else:
                            ext = 'txt'
                    else:
                        ext = 'txt'
                    
                    file_name = f"code_snippet_{i}.{ext}"
                    code_content = re.sub(r'^(\w+)', '', snippet, count=1).strip()  # Remove language specifier if present
                    zip_file.writestr(file_name, code_content)

            zip_buffer.seek(0)
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Code Snippets", "", "Zip files (*.zip);;All files (*)")
            if file_path:
                with open(file_path, 'wb') as f:
                    f.write(zip_buffer.read())
        except Exception as e:
            self.update_convo_box(f"Failed to create code ZIP: {e}")
            self.status_bar.showMessage("Failed to create code ZIP", 5000)

    def create_image_zip(self, image_urls):
        try:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
                for i, url in enumerate(image_urls, 1):
                    response = requests.get(url, headers=HEADERS)
                    response.raise_for_status()
                    img_data = response.content
                    file_name = f"image_{i}.jpg"
                    zip_file.writestr(file_name, img_data)

            zip_buffer.seek(0)
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Images", "", "Zip files (*.zip);;All files (*)")
            if file_path:
                with open(file_path, 'wb') as f:
                    f.write(zip_buffer.read())
        except Exception as e:
            self.update_convo_box(f"Failed to create image ZIP: {e}")
            self.status_bar.showMessage("Failed to create image ZIP", 5000)

    def organize_social_media_campaign(self):
        full_convo = self.convo_box.toPlainText()
        prompt = f"Identify and list all the social media posts created in the following conversation. Organize them into a spreadsheet format:\n{full_convo}"
        category, team_name = self.team_combo.currentText().split("/")
        team = TEAMS[category][team_name]
        model = team["bot3"]["model"]
        preset_prompt = team["bot3"]["preset"]
        
        data = {
            "model": model,
            "messages": [{"role": "system", "content": preset_prompt}, {"role": "user", "content": prompt}]
        }

        try:
            response = requests.post(CHAT_API_URL, headers=HEADERS, json=data)
            response.raise_for_status()
            response_data = response.json()
            if "choices" not in response_data:
                error_message = response_data.get("error", {}).get("message", "Unknown error")
                print(f"Error from OpenAI API: {error_message}")
                return

            organized_text = response_data["choices"][0]["message"]["content"]

            # Create a DataFrame from the organized text
            posts = self.extract_posts_from_text(organized_text)
            df = pd.DataFrame(posts)
            self.save_spreadsheet(df)

        except requests.RequestException as e:
            self.update_convo_box(f"Failed to organize social media campaign: {e}")
            self.status_bar.showMessage("Failed to organize social media campaign", 5000)

    def extract_posts_from_text(self, text):
        # Extract post content from the organized text
        post_pattern = re.compile(r'Post (\d+):\s*(.*?)\n', re.DOTALL)
        posts = post_pattern.findall(text)
        return [{"Platform": "", "Date": "", "Time": "", "Post": content.strip(), "Hashtags": ""} for num, content in posts]

    def save_spreadsheet(self, df):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Spreadsheet", "", "Excel files (*.xlsx);;All files (*)")
        if not file_path:
            return
        try:
            df.to_excel(file_path, index=False)
        except Exception as e:
            self.update_convo_box(f"Failed to save spreadsheet: {e}")
            self.status_bar.showMessage("Failed to save spreadsheet", 5000)

    def download_organized_convo(self, organized_text):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Conversation", "", "Text files (*.txt);;All files (*)")
        if not file_path:
            return
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(organized_text)
        except Exception as e:
            self.update_convo_box(f"Failed to save conversation: {e}")
            self.status_bar.showMessage("Failed to save conversation", 5000)

    def save_convo(self):
        convo_content = self.convo_box.toPlainText()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Conversation", "", "Text files (*.txt);;All files (*)")
        if not file_path:
            return
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(convo_content)
        except Exception as e:
            self.update_convo_box(f"Failed to save conversation: {e}")
            self.status_bar.showMessage("Failed to save conversation", 5000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatGPTConvoApp()
    window.show()
    sys.exit(app.exec_())
