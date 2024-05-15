import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox, filedialog, ttk
import requests
import json
import threading
import re
import zipfile
import os
from io import BytesIO

# OpenAI setup
CHAT_API_URL = "https://api.openai.com/v1/chat/completions"

HEADERS = {
    "Authorization": "Bearer YOUR_API_KEY_HERE",
    "Content-Type": "application/json"
}

# Define teams of bots with complementary roles and preset prompts
TEAMS = {
    "Marketing": {
        "Social Media Campaign": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a social media strategist. Plan a social media campaign."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Continue."},
            "bot3": {"model": "gpt-4", "preset": "You are a project manager. Organize and structure the conversation to present a cohesive plan."}
        },
        "Content Creation": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a content creator. Generate engaging content ideas."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Continue."},
            "bot3": {"model": "gpt-4", "preset": "You are an editor. Organize and improve the content ideas."}
        }
    },
    "Development": {
        "Software Development": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a software developer. Provide solutions and suggestions for software development."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Continue writing the codes how you see best fit."},
            "bot3": {"model": "gpt-4", "preset": "You are an expert analyst. Organize and structure the conversation, including all code snippets. Combine partial snippets into complete code blocks if applicable."}
        },
        "Python Development": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a Python developer. Provide Python code examples and solutions."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Continue development."},
            "bot3": {"model": "gpt-4", "preset": "You are an expert analyst. Organize and structure the conversation, including all code snippets. Combine partial snippets into complete code blocks if applicable."}
        }
    },
    "Data Science": {
        "Data Analysis": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a data scientist. Provide insights and analysis on data science topics."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Continue."},
            "bot3": {"model": "gpt-4", "preset": "You are an expert analyst. Organize and structure the conversation to present a cohesive analysis."}
        },
        "Machine Learning": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a machine learning expert. Provide insights and solutions for machine learning tasks."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Continue."},
            "bot3": {"model": "gpt-4", "preset": "You are an expert analyst. Organize and structure the conversation to present a cohesive analysis."}
        }
    },
    # Add more categories and teams as needed...
}

class ChatGPTConvoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ChatGPT Convo with Function Calls")

        self.api_key = self.ask_api_key()
        if not self.api_key:
            messagebox.showerror("Error", "API key is required to proceed.")
            root.quit()
            return

        global HEADERS
        HEADERS = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Apply style
        style = ttk.Style()
        style.configure("TButton", padding=2, relief="flat", background="#ccc")
        style.configure("TLabel", padding=2)
        style.configure("TEntry", padding=2)

        # Create main frame
        self.main_frame = ttk.Frame(root, padding="2 2 2 2")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Left column frame - GPT Team Chat
        self.left_frame = ttk.Frame(self.main_frame, padding="2 2 2 2")
        self.left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Center column frame - Regular Chat
        self.center_frame = ttk.Frame(self.main_frame, padding="2 2 2 2")
        self.center_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Right column frame - Images
        self.right_frame = ttk.Frame(self.main_frame, padding="2 2 2 2")
        self.right_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure frames to expand with window resize
        for frame in (self.left_frame, self.center_frame, self.right_frame):
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)

        # Team selection with categories
        self.team_label = ttk.Label(self.left_frame, text="Select Team:")
        self.team_var = tk.StringVar(value="Marketing/Social Media Campaign")
        self.team_menu = ttk.Menubutton(self.left_frame, textvariable=self.team_var)
        self.team_menu.menu = tk.Menu(self.team_menu, tearoff=0)
        self.team_menu["menu"] = self.team_menu.menu

        for category, teams in TEAMS.items():
            submenu = tk.Menu(self.team_menu.menu, tearoff=0)
            for team in teams:
                submenu.add_radiobutton(label=team, variable=self.team_var, value=f"{category}/{team}")
            self.team_menu.menu.add_cascade(label=category, menu=submenu)

        self.team_label.grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.team_menu.grid(row=0, column=1, sticky='w', padx=5, pady=2)

        # Initial user prompt
        self.prompt_label = ttk.Label(self.left_frame, text="Initial User Prompt:")
        self.prompt_entry = ttk.Entry(self.left_frame, width=50)

        self.prompt_label.grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.prompt_entry.grid(row=1, column=1, columnspan=2, sticky='w', padx=5, pady=2)

        # Autostop count
        self.autostop_label = ttk.Label(self.left_frame, text="Number of Exchanges:")
        self.autostop_entry = ttk.Entry(self.left_frame, width=10)
        self.autostop_entry.insert(0, "10")

        self.autostop_label.grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.autostop_entry.grid(row=2, column=1, sticky='w', padx=5, pady=2)

        # Interject user prompt
        self.interject_label = ttk.Label(self.left_frame, text="Interject Prompt:")
        self.interject_entry = ttk.Entry(self.left_frame, width=50)
        self.interject_button = ttk.Button(self.left_frame, text="Interject", state=tk.DISABLED, command=self.interject_convo)

        self.interject_label.grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.interject_entry.grid(row=3, column=1, columnspan=2, sticky='w', padx=5, pady=2)
        self.interject_button.grid(row=3, column=3, sticky='w', padx=5, pady=2)

        # Conversation display and control buttons
        self.convo_box = scrolledtext.ScrolledText(self.left_frame, width=50, height=35)
        self.convo_box.tag_config("user", foreground="green")
        self.convo_box.tag_config("paused", foreground="yellow")
        self.convo_box.tag_config("stopped", foreground="red")
        self.convo_box.grid(row=4, column=0, columnspan=4, padx=5, pady=5)

        self.start_button = ttk.Button(self.left_frame, text="Start", command=self.start_convo)
        self.pause_button = ttk.Button(self.left_frame, text="Pause", state=tk.NORMAL, command=self.pause_convo)
        self.stop_button = ttk.Button(self.left_frame, text="Stop", state=tk.DISABLED, command=self.stop_convo)
        self.save_button = ttk.Button(self.left_frame, text="Save Convo", command=self.save_convo)
        self.organize_button = ttk.Button(self.left_frame, text="Organize", state=tk.NORMAL, command=self.organize_convo)

        self.start_button.grid(row=5, column=0, sticky='w', padx=5, pady=2)
        self.pause_button.grid(row=5, column=1, sticky='w', padx=5, pady=2)
        self.stop_button.grid(row=5, column=2, sticky='w', padx=5, pady=2)
        self.save_button.grid(row=5, column=3, sticky='w', padx=5, pady=2)
        self.organize_button.grid(row=6, column=0, columnspan=4, sticky='w', padx=5, pady=2)

        self.running = False
        self.paused = False
        self.messages = [{"role": "system", "content": "You are a helpful assistant."}]
        self.exchange_count = 0
        self.max_exchanges = 0

        # Center column - Regular Chat with model selection
        self.center_chat_box = scrolledtext.ScrolledText(self.center_frame, width=50, height=35)
        self.center_chat_entry = ttk.Entry(self.center_frame, width=50)
        self.center_chat_button = ttk.Button(self.center_frame, text="Send", command=self.send_center_chat)

        self.model_label = ttk.Label(self.center_frame, text="Select Model:")
        self.model_var = tk.StringVar(value="gpt-3.5-turbo")
        self.model_dropdown = ttk.OptionMenu(self.center_frame, self.model_var, "gpt-3.5-turbo", "gpt-3.5-turbo", "gpt-4-turbo")

   
        self.model_label.grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.model_dropdown.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        self.center_chat_box.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        self.center_chat_entry.grid(row=3, column=0, padx=5, pady=2)
        self.center_chat_button.grid(row=3, column=1, padx=5, pady=2)

    def ask_api_key(self):
        return simpledialog.askstring("API Key", "Please enter your OpenAI API key:", show='*')

    def start_convo(self):
        try:
            self.max_exchanges = int(self.autostop_entry.get())
        except ValueError:
            self.max_exchanges = 10  # Default value

        self.start_button['state'] = tk.DISABLED
        self.pause_button['state'] = tk.NORMAL
        self.stop_button['state'] = tk.NORMAL
        self.running = True
        self.paused = False
        initial_prompt = self.prompt_entry.get()
        self.messages.append({"role": "user", "content": initial_prompt})
        self.convo_box.insert(tk.END, f"User: {initial_prompt}\n", "user")
        self.exchange_count = 0
        thread = threading.Thread(target=self.convo_loop)
        thread.start()

    def pause_convo(self):
        self.paused = True
        self.interject_button['state'] = tk.NORMAL
        self.convo_box.insert(tk.END, "Conversation paused.\n", "paused")

    def stop_convo(self):
        self.running = False
        self.paused = False
        self.start_button['state'] = tk.NORMAL
        self.pause_button['state'] = tk.DISABLED
        self.stop_button['state'] = tk.DISABLED
        self.interject_button['state'] = tk.DISABLED
        self.convo_box.insert(tk.END, "Conversation stopped.\n", "stopped")

    def interject_convo(self):
        interject_prompt = self.interject_entry.get()
        self.messages.append({"role": "user", "content": interject_prompt})
        self.convo_box.insert(tk.END, f"User: {interject_prompt}\n", "user")
        self.paused = False
        self.interject_button['state'] = tk.DISABLED
        self.pause_button['state'] = tk.NORMAL
        if self.running:
            thread = threading.Thread(target=self.convo_loop)
            thread.start()

    def convo_loop(self):
        bot_turn = 1
        category, team_name = self.team_var.get().split("/")
        team = TEAMS[category][team_name]
        while self.running and (self.max_exchanges == 0 or self.exchange_count < self.max_exchanges):
            if self.paused:
                continue
            if bot_turn == 1:
                model = team["bot1"]["model"]
                preset_prompt = team["bot1"]["preset"]
            else:
                model = team["bot2"]["model"]
                preset_prompt = team["bot2"]["preset"]

            response = self.ask_openai(self.messages, model, preset_prompt)

            if not self.running:
                break

            self.convo_box.insert(tk.END, f"Bot {bot_turn}: {response}\n")
            self.messages.append({"role": "assistant", "content": response})
            self.exchange_count += 1

            bot_turn = 2 if bot_turn == 1 else 1

        if not self.paused and not self.running:
            self.convo_box.insert(tk.END, "Conversation completed.\n")

    def ask_openai(self, messages, model, preset_prompt):
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

    def organize_convo(self):
        thread = threading.Thread(target=self._organize_convo_thread)
        thread.start()

    def _organize_convo_thread(self):
        organized_text, code_snippets = self.get_organized_text()

        if code_snippets:
            self.create_code_zip(code_snippets)

        # Allow organized text to be downloaded
        self.download_organized_convo(organized_text)

    def get_organized_text(self):
        full_convo = self.convo_box.get("1.0", tk.END)
        prompt = f"Organize and structure the following conversation into a cohesive and detailed plan. If there are code snippets, identify and save each as a separate file:\n{full_convo}"
        category, team_name = self.team_var.get().split("/")
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
        file_path = filedialog.asksaveasfilename(defaultextension=".zip",
                                                 filetypes=[("Zip files", "*.zip"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'wb') as f:
                f.write(zip_buffer.read())

    def download_organized_convo(self, organized_text):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(organized_text)

    def save_convo(self):
        convo_content = self.convo_box.get("1.0", tk.END)
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(convo_content)

    def send_center_chat(self):
        message = self.center_chat_entry.get()
        if message:
            self.center_chat_box.insert(tk.END, f"You: {message}\n", "user")
            self.center_chat_entry.delete(0, tk.END)
            # Send the message to OpenAI API and get the response
            threading.Thread(target=self._send_center_chat_thread, args=(message,)).start()

    def _send_center_chat_thread(self, message):
        data = {
            "model": self.model_var.get(),
            "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": message}]
        }

        try:
            response = requests.post(CHAT_API_URL, headers=HEADERS, json=data)
            response.raise_for_status()
            response_data = response.json()
            if "choices" not in response_data:
                error_message = response_data.get("error", {}).get("message", "Unknown error")
                print(f"Error from OpenAI API: {error_message}")
                return

            reply = response_data["choices"][0]["message"]["content"]
            self.center_chat_box.insert(tk.END, f"Assistant: {reply}\n")

        except requests.RequestException as e:
            print(f"Request error: {e}")
            self.center_chat_box.insert(tk.END, f"Error: Unable to communicate with the OpenAI API.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatGPTConvoApp(root)
    root.mainloop()
