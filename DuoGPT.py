import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox, filedialog, ttk
from tkinter import PhotoImage, Menu
import requests
import json
import threading
import re
import zipfile
import os
import pandas as pd
from io import BytesIO
from PIL import Image, ImageTk
import subprocess

# OpenAI setup
CHAT_API_URL = "https://api.openai.com/v1/chat/completions"
DALLE3_API_URL = "https://api.openai.com/v1/images/generations"

API_KEY_FILE = "api_key.json"

HEADERS = {
    "Authorization": "",
    "Content-Type": "application/json"
}

# Define teams of bots with complementary roles and preset prompts
TEAMS = {
    "Marketing": {
        "Social Media Campaign": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a social media strategist. Plan a social media campaign."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide recommendations based on the previous response."},
            "bot3": {"model": "gpt-4", "preset": "You are a project manager. Organize and structure the conversation to present a cohesive plan."}
        },
        "Content Creation": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a content creator. Generate engaging content ideas."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide recommendations based on the previous response."},
            "bot3": {"model": "gpt-4", "preset": "You are an editor. Organize and improve the content ideas."}
        }
    },
    "Development": {
        "Software Development": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a software developer. Provide solutions and suggestions for software development."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide recommendations based on the previous response."},
            "bot3": {"model": "gpt-4", "preset": "You are an expert analyst. Organize and structure the conversation, including all code snippets. Combine partial snippets into complete code blocks if applicable."}
        },
        "Python Development": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a Python developer. Provide Python code examples and solutions."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide recommendations based on the previous response."},
            "bot3": {"model": "gpt-4", "preset": "You are an expert analyst. Organize and structure the conversation, including all code snippets. Combine partial snippets into complete code blocks if applicable."}
        },
        "JavaScript Development": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a JavaScript developer. Provide JavaScript code examples and solutions."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide recommendations based on the previous response."},
            "bot3": {"model": "gpt-4", "preset": "You are an expert analyst. Organize and structure the conversation, including all code snippets. Combine partial snippets into complete code blocks if applicable."}
        },
        "HTML Development": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are an HTML developer. Provide HTML code examples and solutions."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide recommendations based on the previous response."},
            "bot3": {"model": "gpt-4", "preset": "You are an expert analyst. Organize and structure the conversation, including all code snippets. Combine partial snippets into complete code blocks if applicable."}
        },
        "CSS Development": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a CSS developer. Provide CSS code examples and solutions."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide recommendations based on the previous response."},
            "bot3": {"model": "gpt-4", "preset": "You are an expert analyst. Organize and structure the conversation, including all code snippets. Combine partial snippets into complete code blocks if applicable."}
        },
        "Java Development": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a Java developer. Provide Java code examples and solutions."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide recommendations based on the previous response."},
            "bot3": {"model": "gpt-4", "preset": "You are an expert analyst. Organize and structure the conversation, including all code snippets. Combine partial snippets into complete code blocks if applicable."}
        },
        "C++ Development": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a C++ developer. Provide C++ code examples and solutions."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide recommendations based on the previous response."},
            "bot3": {"model": "gpt-4", "preset": "You are an expert analyst. Organize and structure the conversation, including all code snippets. Combine partial snippets into complete code blocks if applicable."}
        }
    },
    "Data Science": {
        "Data Analysis": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a data scientist. Provide insights and analysis on data science topics."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide recommendations based on the previous response."},
            "bot3": {"model": "gpt-4", "preset": "You are an expert analyst. Organize and structure the conversation to present a cohesive analysis."}
        },
        "Machine Learning": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a machine learning expert. Provide insights and solutions for machine learning tasks."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide recommendations based on the previous response."},
            "bot3": {"model": "gpt-4", "preset": "You are an expert analyst. Organize and structure the conversation to present a cohesive analysis."}
        }
    },
    "Business": {
        "Strategy Development": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a business strategist. Develop a business strategy."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide recommendations based on the previous response."},
            "bot3": {"model": "gpt-4", "preset": "You are a project manager. Organize and structure the conversation to present a cohesive strategy."}
        },
        "Market Analysis": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a market analyst. Provide a market analysis."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide recommendations based on the previous response."},
            "bot3": {"model": "gpt-4", "preset": "You are an expert analyst. Organize and structure the conversation to present a cohesive analysis."}
        },
        "Financial Planning": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a financial planner. Provide financial planning advice."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide recommendations based on the previous response."},
            "bot3": {"model": "gpt-4", "preset": "You are an expert analyst. Organize and structure the conversation to present a cohesive financial plan."}
        }
    },
    "Graphic Designer": {
        "Image Creation": {
            "bot1": {"model": "dalle-3", "preset": "You are a DALL-E model. Generate an image based on the provided prompt."},
            "bot2": {"model": "gpt-4-vision-preview", "preset": "You are a GPT-4 Vision model. Analyze the generated image and recommend edits."},
            "bot3": {"model": "gpt-4-vision-preview", "preset": "You are an organizer. Organize and structure the conversation and prepare a collection of images."}
        },
        "Album Cover Maker": {
            "bot1": {"model": "dalle-3", "preset": "You are a DALL-E model. Generate an album cover based on the provided prompt."},
            "bot2": {"model": "gpt-4-vision-preview", "preset": "You are a GPT-4 Vision model. Analyze the generated album cover and recommend edits."},
            "bot3": {"model": "gpt-4-vision-preview", "preset": "You are an organizer. Organize and structure the conversation and prepare a collection of album covers."}
        },
        "Logo Maker": {
            "bot1": {"model": "dalle-3", "preset": "You are a DALL-E model. Generate a logo based on the provided prompt."},
            "bot2": {"model": "gpt-4-vision-preview", "preset": "You are a GPT-4 Vision model. Analyze the generated logo and recommend edits."},
            "bot3": {"model": "gpt-4-vision-preview", "preset": "You are an organizer. Organize and structure the conversation and prepare a collection of logos."}
        },
        "Product Designer": {
            "bot1": {"model": "dalle-3", "preset": "You are a DALL-E model. Generate a product design based on the provided prompt."},
            "bot2": {"model": "gpt-4-vision-preview", "preset": "You are a GPT-4 Vision model. Analyze the generated product design and recommend edits."},
            "bot3": {"model": "gpt-4-vision-preview", "preset": "You are an organizer. Organize and structure the conversation and prepare a collection of product designs."}
        },
        "Character Developer": {
            "bot1": {"model": "dalle-3", "preset": "You are a DALL-E model. Generate a character design based on the provided prompt."},
            "bot2": {"model": "gpt-4-vision-preview", "preset": "You are a GPT-4 Vision model. Analyze the generated character design and recommend edits."},
            "bot3": {"model": "gpt-4-vision-preview", "preset": "You are an organizer. Organize and structure the conversation and prepare a collection of character designs."}
        },
        "Algorithmic Graphic Designer": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are an algorithmic graphic designer. Write Python scripts to generate highly detailed visual masterpieces."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide feedback on the previous response's Python script for generating visual masterpieces."},
            "bot3": {"model": "gpt-4", "preset": "You are an organizer. Organize and structure the conversation and prepare a collection of Python scripts."}
        }
    },
    "Music": {
        "Algorithmic Composer": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are an algorithmic composer. Write Python scripts for algorithmic composition."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide feedback on the previous response's Python script for algorithmic composition."},
            "bot3": {"model": "gpt-4", "preset": "You are an organizer. Organize and structure the conversation and prepare a collection of Python scripts."}
        },
        "MIDI Maker": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a MIDI maker. Write Python scripts to generate MIDI files."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide feedback on the previous response's Python script for generating MIDI files."},
            "bot3": {"model": "gpt-4", "preset": "You are an organizer. Organize and structure the conversation and prepare a collection of Python scripts."}
        },
        "Sound Designer": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a sound designer. Write Python scripts to design sound."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide feedback on the previous response's Python script for sound design."},
            "bot3": {"model": "gpt-4", "preset": "You are an organizer. Organize and structure the conversation and prepare a collection of Python scripts."}
        },
        "Songwriter": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a songwriter. Write Python scripts to generate songs."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide feedback on the previous response's Python script for songwriting."},
            "bot3": {"model": "gpt-4", "preset": "You are an organizer. Organize and structure the conversation and prepare a collection of Python scripts."}
        }
    },
    "Game Design": {
        "Story Writer": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a game story writer. Write engaging and immersive game stories."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide feedback on the previous response's game story."},
            "bot3": {"model": "gpt-4", "preset": "You are an editor. Organize and structure the game story into a cohesive narrative."}
        },
        "Level Designer": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a game level designer. Design detailed and engaging game levels."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide feedback on the previous response's game level design."},
            "bot3": {"model": "gpt-4", "preset": "You are an organizer. Organize and structure the conversation and prepare a collection of level designs."}
        },
        "Mechanics Designer": {
            "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a game mechanics designer. Design innovative and engaging game mechanics."},
            "bot2": {"model": "gpt-3.5-turbo", "preset": "Provide feedback on the previous response's game mechanics design."},
            "bot3": {"model": "gpt-4", "preset": "You are an organizer. Organize and structure the conversation and prepare a collection of game mechanics designs."}
        }
    }
}

class ChatGPTConvoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ChatGPT Convo with Function Calls")

        self.api_key = self.load_api_key()
        if not self.api_key:
            self.api_key = self.ask_api_key()
            if not self.api_key:
                messagebox.showerror("Error", "API key is required to proceed.")
                root.quit()
                return
            self.save_api_key(self.api_key)

        global HEADERS
        HEADERS = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        self.history = []

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
        self.main_frame.rowconfigure(0, weight=1)

        # Left column frame - GPT Team Chat
        self.left_frame = ttk.Frame(self.main_frame, padding="2 2 2 2")
        self.left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Center column frame - Divider
        self.center_frame = ttk.Frame(self.main_frame, padding="2 2 2 2")
        self.center_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Right column frame - Regular Chat
        self.right_frame = ttk.Frame(self.main_frame, padding="2 2 2 2")
        self.right_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure frames to expand with window resize
        for frame in (self.left_frame, self.center_frame, self.right_frame):
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)

        # Add labels at the top
        self.team_mode_label = ttk.Label(self.left_frame, text="Team Mode", font=("Arial", 16, "bold"))
        self.team_mode_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.solo_mode_label = ttk.Label(self.right_frame, text="Solo Mode", font=("Arial", 16, "bold"))
        self.solo_mode_label.grid(row=0, column=0, columnspan=2, pady=10)

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

        self.team_label.grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.team_menu.grid(row=1, column=1, sticky='w', padx=5, pady=2)

        # Initial user prompt
        self.prompt_label = ttk.Label(self.left_frame, text="Initial User Prompt:")
        self.prompt_entry = ttk.Entry(self.left_frame, width=50)
        self.start_button = ttk.Button(self.left_frame, text="Start", command=self.start_convo)

        self.prompt_label.grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.prompt_entry.grid(row=2, column=1, columnspan=2, sticky='w', padx=5, pady=2)
        self.start_button.grid(row=2, column=3, sticky='w', padx=5, pady=2)

        # Autostop count
        self.autostop_label = ttk.Label(self.left_frame, text="Number of Exchanges:")
        self.autostop_entry = ttk.Entry(self.left_frame, width=10)
        self.autostop_entry.insert(0, "10")

        self.autostop_label.grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.autostop_entry.grid(row=3, column=1, sticky='w', padx=5, pady=2)

        # Interject user prompt
        self.interject_label = ttk.Label(self.left_frame, text="Interject Prompt:")
        self.interject_entry = ttk.Entry(self.left_frame, width=50)
        self.interject_button = ttk.Button(self.left_frame, text="Interject", state=tk.DISABLED, command=self.interject_convo)

        self.interject_label.grid(row=4, column=0, sticky='w', padx=5, pady=2)
        self.interject_entry.grid(row=4, column=1, columnspan=2, sticky='w', padx=5, pady=2)
        self.interject_button.grid(row=4, column=3, sticky='w', padx=5, pady=2)

        # Conversation display and control buttons
        self.convo_box = scrolledtext.ScrolledText(self.left_frame, width=70, height=25)
        self.convo_box.tag_config("user", foreground="green")
        self.convo_box.tag_config("paused", foreground="yellow")
        self.convo_box.tag_config("stopped", foreground="red")
        self.convo_box.grid(row=5, column=0, columnspan=4, padx=5, pady=5)
        self.convo_box.images = []

        self.pause_button = ttk.Button(self.left_frame, text="Pause", state=tk.NORMAL, command=self.pause_convo)
        self.stop_button = ttk.Button(self.left_frame, text="Stop", state=tk.DISABLED, command=self.stop_convo)
        self.save_button = ttk.Button(self.left_frame, text="Save Convo", command=self.save_convo)
        self.organize_button = ttk.Button(self.left_frame, text="Organize", state=tk.NORMAL, command=self.organize_convo)

        self.pause_button.grid(row=6, column=0, sticky='w', padx=5, pady=2)
        self.stop_button.grid(row=6, column=1, sticky='w', padx=5, pady=2)
        self.save_button.grid(row=6, column=2, sticky='w', padx=5, pady=2)
        self.organize_button.grid(row=6, column=3, sticky='w', padx=5, pady=2)

        self.running = False
        self.paused = False
        self.messages = [{"role": "system", "content": "You are a helpful assistant."}]
        self.exchange_count = 0
        self.max_exchanges = 0
        self.generated_images = []

        # Center frame - Divider
        self.divider = ttk.Separator(self.center_frame, orient='vertical')
        self.divider.grid(row=0, column=0, sticky='ns')

        # Right column - Solo Mode Chat with model selection
        self.solo_chat_box = scrolledtext.ScrolledText(self.right_frame, width=70, height=25)
        self.solo_chat_box.tag_config("user", foreground="#d3d3d3")  # Light gray color
        self.solo_chat_box.tag_config("assistant", foreground="red")
        self.solo_chat_box.tag_config("thinking", foreground="blue")
        self.solo_chat_box.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        self.solo_chat_box.images = []

        self.solo_chat_entry = ttk.Entry(self.right_frame, width=50)
        self.solo_chat_button = ttk.Button(self.right_frame, text="Send", command=self.send_solo_chat)

        self.model_label = ttk.Label(self.right_frame, text="Select Model:")
        self.model_var = tk.StringVar(value="gpt-3.5-turbo")
        models = [
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-4-turbo",
            "gpt-3.5-turbo-16k",
            "dalle-3"
        ]
        self.model_dropdown = ttk.OptionMenu(self.right_frame, self.model_var, models[0], *models)

        self.model_label.grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.model_dropdown.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        self.solo_chat_entry.grid(row=3, column=0, padx=5, pady=2)
        self.solo_chat_button.grid(row=3, column=1, padx=5, pady=2)

        # Implement right-click menu
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_text)
        self.context_menu.add_command(label="Cut", command=self.cut_text)
        self.context_menu.add_command(label="Paste", command=self.paste_text)
        self.context_menu.add_command(label="Analyze", command=self.analyze_text)

        self.solo_chat_box.bind("<Button-3>", self.show_context_menu)

        # Implement quick keys
        self.root.bind("<Control-c>", lambda event: self.copy_text())
        self.root.bind("<Control-x>", lambda event: self.cut_text())
        self.root.bind("<Control-v>", lambda event: self.paste_text())
        self.root.bind("<Control-a>", lambda event: self.analyze_text())

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
        self.convo_box.insert(tk.END, f"User: {initial_prompt}\n\n", "user")
        self.exchange_count = 0
        thread = threading.Thread(target=self.convo_loop)
        thread.start()

    def pause_convo(self):
        self.paused = True
        self.interject_button['state'] = tk.NORMAL
        self.convo_box.insert(tk.END, "Conversation paused.\n\n", "paused")

    def stop_convo(self):
        self.running = False
        self.paused = False
        self.start_button['state'] = tk.NORMAL
        self.pause_button['state'] = tk.DISABLED
        self.stop_button['state'] = tk.DISABLED
        self.interject_button['state'] = tk.DISABLED
        self.convo_box.insert(tk.END, "Conversation stopped.\n\n", "stopped")

    def interject_convo(self):
        interject_prompt = self.interject_entry.get()
        self.messages.append({"role": "user", "content": interject_prompt})
        self.convo_box.insert(tk.END, f"User: {interject_prompt}\n\n", "user")
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
                response = self.ask_openai(self.messages, model, preset_prompt, is_image=(model == "dalle-3"))
            else:
                model = team["bot2"]["model"]
                preset_prompt = team["bot2"]["preset"]
                response = self.ask_openai(self.messages, model, preset_prompt, is_image=(model == "gpt-4-vision-preview"))

            if not self.running:
                break

            if model == "dalle-3":
                self.generated_images.append(response)
                self.display_image(self.convo_box, response)
            else:
                self.insert_message_with_image(self.convo_box, f"Bot {bot_turn}: {response}\n\n", None)
                self.messages.append({"role": "assistant", "content": response})
            
            self.exchange_count += 1
            bot_turn = 2 if bot_turn == 1 else 1

        if not self.paused and not self.running:
            self.convo_box.insert(tk.END, "Conversation completed.\n\n")

    def ask_openai(self, messages, model, preset_prompt, is_image=False):
        if is_image and model == "dalle-3":
            return self.ask_dalle(preset_prompt)
        elif is_image and model == "gpt-4-vision-preview":
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

    def display_image(self, chat_box, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img.thumbnail((300, 300))
            photo = ImageTk.PhotoImage(img)
            chat_box.image_create(tk.END, image=photo)
            chat_box.images.append(photo)  # Keep a reference to avoid garbage collection
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
                    chat_box.insert(tk.END, part, tag)
        else:
            chat_box.insert(tk.END, message, tag)

    def organize_convo(self):
        thread = threading.Thread(target=self._organize_convo_thread)
        thread.start()

    def _organize_convo_thread(self):
        category, team_name = self.team_var.get().split("/")
        if category == "Marketing" and team_name == "Social Media Campaign":
            self.organize_social_media_campaign()
        else:
            organized_text, code_snippets = self.get_organized_text()
            self.create_code_zip(code_snippets)

            if self.generated_images:
                self.create_image_zip(self.generated_images)

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

    def create_image_zip(self, image_urls):
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
            for i, url in enumerate(image_urls, 1):
                response = requests.get(url)
                response.raise_for_status()
                img_data = response.content
                file_name = f"image_{i}.jpg"
                zip_file.writestr(file_name, img_data)

        zip_buffer.seek(0)
        file_path = filedialog.asksaveasfilename(defaultextension=".zip",
                                                 filetypes=[("Zip files", "*.zip"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'wb') as f:
                f.write(zip_buffer.read())

    def organize_social_media_campaign(self):
        full_convo = self.convo_box.get("1.0", tk.END)
        prompt = f"Identify and list all the social media posts created in the following conversation. Organize them into a spreadsheet format:\n{full_convo}"
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
                return

            organized_text = response_data["choices"][0]["message"]["content"]

            # Create a DataFrame from the organized text
            posts = self.extract_posts_from_text(organized_text)
            df = pd.DataFrame(posts)
            self.save_spreadsheet(df)

        except requests.RequestException as e:
            print(f"Request error: {e}")

    def extract_posts_from_text(self, text):
        # Extract post content from the organized text
        post_pattern = re.compile(r'Post (\d+):\s*(.*?)\n', re.DOTALL)
        posts = post_pattern.findall(text)
        return [{"Platform": "", "Date": "", "Time": "", "Post": content.strip(), "Hashtags": ""} for num, content in posts]

    def save_spreadsheet(self, df):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                 filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if not file_path:
            return
        df.to_excel(file_path, index=False)

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

    def send_solo_chat(self):
        message = self.solo_chat_entry.get()
        if message:
            self.solo_chat_box.insert(tk.END, f"You: {message}\n\n", "user")
            self.solo_chat_entry.delete(0, tk.END)
            # Send the message to OpenAI API and get the response
            threading.Thread(target=self._send_solo_chat_thread, args=(message,)).start()

    def _send_solo_chat_thread(self, message):
        model = self.model_var.get()
        self.solo_chat_box.insert(tk.END, "Assistant is thinking...\n", "thinking")
        if model == "dalle-3":
            response = self.ask_dalle(message)
        else:
            data = {
                "model": model,
                "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": message}]
            }
            try:
                response = requests.post(CHAT_API_URL, headers=HEADERS, json=data)
                response.raise_for_status()
                response_data = response.json()
                if "choices" not in response_data:
                    error_message = response_data.get("error", {}).get("message", "Unknown error")
                    print(f"Error from OpenAI API: {error_message}")
                    response = f"Error: {error_message}"
                else:
                    response = response_data["choices"][0]["message"]["content"]
            except requests.RequestException as e:
                print(f"Request error: {e}")
                response = "Error: Unable to communicate with the OpenAI API."

        self.solo_chat_box.delete("1.0", "end-1c")
        self.insert_message_with_image(self.solo_chat_box, f"Assistant: {response}\n\n", "assistant")

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def copy_text(self):
        self.solo_chat_box.event_generate("<<Copy>>")

    def cut_text(self):
        self.solo_chat_box.event_generate("<<Cut>>")

    def paste_text(self):
        self.solo_chat_box.event_generate("<<Paste>>")

    def analyze_text(self):
        selected_text = self.solo_chat_box.selection_get()
        self.solo_chat_box.insert(tk.END, f"\nAnalyzing: {selected_text}\n", "assistant")
        # Additional analysis code can be added here

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatGPTConvoApp(root)
    root.mainloop()

