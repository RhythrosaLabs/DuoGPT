import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
from tkinter import ttk
import requests
import json
import threading
import io

# OpenAI setup
CHAT_API_URL = "https://api.openai.com/v1/chat/completions"
# IMAGE_API_URL = "https://api.openai.com/v1/images/generations"  # Commented out image generation

def load_api_key():
    try:
        with open('api_key.json', 'r') as file:
            data = json.load(file)
            return data['api_key']
    except (FileNotFoundError, KeyError):
        return None

def save_api_key(api_key):
    with open('api_key.json', 'w') as file:
        json.dump({'api_key': api_key}, file)

api_key = load_api_key()
if api_key is None:
    api_key = simpledialog.askstring("API Key", "Please enter your OpenAI API key:", show='*')
    if api_key:
        save_api_key(api_key)
    else:
        messagebox.showerror("Error", "API key is required to proceed.")
        exit()

HEADERS = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Define teams of bots with complementary roles and preset prompts
TEAMS = {
    "Social Media Campaign": {
        "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a social media strategist. Plan a social media campaign."},
        "bot2": {"model": "gpt-3.5-turbo", "preset": "You are a content creator. Create engaging content for the campaign. When asked to continue, provide detailed content ideas."},
        "bot3": {"model": "gpt-4", "preset": "You are a project manager. Organize and structure the conversation to present a cohesive plan."}
    },
    "Software Development": {
        "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a software developer. Provide solutions and suggestions for software development."},
        "bot2": {"model": "gpt-3.5-turbo", "preset": "You are a code reviewer. Review the given code and provide improvements. When asked to continue, provide detailed code reviews."},
        "bot3": {"model": "gpt-4", "preset": "You are a project manager. Organize and structure the conversation to present a cohesive development plan."}
    },
    "Python Development": {
        "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a Python developer. Provide Python code examples and solutions."},
        "bot2": {"model": "gpt-3.5-turbo", "preset": "You are a Python code reviewer. Review the given Python code and provide improvements. When asked to continue, provide detailed code reviews."},
        "bot3": {"model": "gpt-4", "preset": "You are a project manager. Organize and structure the conversation to present a cohesive Python project plan."}
    },
    "Visual Studio Code": {
        "bot1": {"model": "gpt-3.5-turbo", "preset": "You are an expert in Visual Studio Code. Provide tips and tricks for using VS Code effectively."},
        "bot2": {"model": "gpt-3.5-turbo", "preset": "You are a plugin developer. Suggest and explain useful VS Code plugins. When asked to continue, provide detailed plugin configurations."},
        "bot3": {"model": "gpt-4", "preset": "You are a project manager. Organize and structure the conversation to present a cohesive setup for Visual Studio Code."}
    },
    "Marketing": {
        "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a marketing strategist. Develop a comprehensive marketing strategy."},
        "bot2": {"model": "gpt-3.5-turbo", "preset": "You are a content creator. Create engaging marketing content. When asked to continue, provide detailed content ideas."},
        "bot3": {"model": "gpt-4", "preset": "You are a project manager. Organize and structure the conversation to present a cohesive marketing plan."}
    },
    # Add more specialized teams as needed...
}

class ChatGPTConvoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ChatGPT Convo with Function Calls")
        self.root.geometry("900x900")

        # Apply style
        style = ttk.Style()
        style.configure("TButton", padding=1, relief="flat", background="#ccc")
        style.configure("TLabel", padding=1)
        style.configure("TEntry", padding=1)

        # Create main frame
        self.main_frame = ttk.Frame(root, padding="1 1 1 1")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Left column frame - GPT Team Chat
        self.left_frame = ttk.Frame(self.main_frame, padding="1 1 1 1")
        self.left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Center column frame - Regular Chat
        self.center_frame = ttk.Frame(self.main_frame, padding="1 1 1 1")
        self.center_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Right column frame - Images (Commented out image generation)
        # self.right_frame = ttk.Frame(self.main_frame, padding="1 1 1 1")
        # self.right_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure frames to expand with window resize
        for frame in (self.left_frame, self.center_frame):  # Removed right_frame
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)

        # Team selection
        self.team_label = ttk.Label(self.left_frame, text="Select Team:")
        self.team_var = tk.StringVar(value="Social Media Campaign")
        self.team_dropdown = ttk.OptionMenu(self.left_frame, self.team_var, *TEAMS.keys())

        self.team_label.grid(row=0, column=0, sticky='w', padx=2, pady=1)
        self.team_dropdown.grid(row=0, column=1, sticky='w', padx=2, pady=1)

        # Initial user prompt
        self.prompt_label = ttk.Label(self.left_frame, text="Initial User Prompt:")
        self.prompt_entry = ttk.Entry(self.left_frame, width=30)

        self.prompt_label.grid(row=1, column=0, sticky='w', padx=2, pady=1)
        self.prompt_entry.grid(row=1, column=1, columnspan=2, sticky='w', padx=2, pady=1)

        # Autostop count
        self.autostop_label = ttk.Label(self.left_frame, text="Number of Exchanges:")
        self.autostop_entry = ttk.Entry(self.left_frame, width=5)
        self.autostop_entry.insert(0, "10")

        self.autostop_label.grid(row=2, column=0, sticky='w', padx=2, pady=1)
        self.autostop_entry.grid(row=2, column=1, sticky='w', padx=2, pady=1)

        # Interject user prompt
        self.interject_label = ttk.Label(self.left_frame, text="Interject Prompt:")
        self.interject_entry = ttk.Entry(self.left_frame, width=30)
        self.interject_button = ttk.Button(self.left_frame, text="Interject", state=tk.DISABLED, command=self.interject_convo)

        self.interject_label.grid(row=3, column=0, sticky='w', padx=2, pady=1)
        self.interject_entry.grid(row=3, column=1, columnspan=2, sticky='w', padx=2, pady=1)
        self.interject_button.grid(row=3, column=3, sticky='w', padx=2, pady=1)

        # Conversation display and control buttons
        self.convo_box = scrolledtext.ScrolledText(self.left_frame, width=40, height=15)
        self.convo_box.grid(row=4, column=0, columnspan=4, padx=2, pady=2)

        self.start_button = ttk.Button(self.left_frame, text="Start", command=self.start_convo)
        self.pause_button = ttk.Button(self.left_frame, text="Pause", state=tk.DISABLED, command=self.pause_convo)
        self.stop_button = ttk.Button(self.left_frame, text="Stop", state=tk.DISABLED, command=self.stop_convo)
        self.save_button = ttk.Button(self.left_frame, text="Save Convo", command=self.save_convo)
        self.organize_button = ttk.Button(self.left_frame, text="Organize", state=tk.NORMAL, command=self.organize_convo)

        self.start_button.grid(row=5, column=0, sticky='w', padx=2, pady=1)
        self.pause_button.grid(row=5, column=1, sticky='w', padx=2, pady=1)
        self.stop_button.grid(row=5, column=2, sticky='w', padx=2, pady=1)
        self.save_button.grid(row=5, column=3, sticky='w', padx=2, pady=1)
        self.organize_button.grid(row=6, column=0, columnspan=4, sticky='w', padx=2, pady=1)

        self.running = False
        self.paused = False
        self.messages = [{"role": "system", "content": "You are a helpful assistant."}]
        self.exchange_count = 0
        self.max_exchanges = 0

        # Center column - Regular Chat
        self.center_chat_label = ttk.Label(self.center_frame, text="Regular Chat:")
        self.center_chat_box = scrolledtext.ScrolledText(self.center_frame, width=40, height=15)
        self.center_chat_entry = ttk.Entry(self.center_frame, width=30)
        self.center_chat_button = ttk.Button(self.center_frame, text="Send", command=self.send_center_chat)

        self.center_chat_label.grid(row=0, column=0, sticky='w', padx=2, pady=1)
        self.center_chat_box.grid(row=1, column=0, padx=2, pady=2)
        self.center_chat_entry.grid(row=2, column=0, padx=2, pady=1)
        self.center_chat_button.grid(row=2, column=1, padx=2, pady=1)

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
        self.convo_box.insert(tk.END, f"User: {initial_prompt}\n")
        thread = threading.Thread(target=self.convo_loop)
        thread.start()

    def pause_convo(self):
        self.paused = True
        self.interject_button['state'] = tk.NORMAL

    def stop_convo(self):
        self.running = False
        self.paused = False
        self.start_button['state'] = tk.NORMAL
        self.pause_button['state'] = tk.DISABLED
        self.stop_button['state'] = tk.DISABLED
        self.interject_button['state'] = tk.DISABLED

    def interject_convo(self):
        interject_prompt = self.interject_entry.get()
        self.messages.append({"role": "user", "content": interject_prompt})
        self.convo_box.insert(tk.END, f"User: {interject_prompt}\n")
        self.paused = False
        self.interject_button['state'] = tk.DISABLED
        self.pause_button['state'] = tk.NORMAL
        if self.running:
            thread = threading.Thread(target=self.convo_loop)
            thread.start()

    def convo_loop(self):
        bot_turn = 1
        team = TEAMS[self.team_var.get()]
        while self.running and not self.paused and (self.max_exchanges == 0 or self.exchange_count < self.max_exchanges):
            if bot_turn == 1:
                model = team["bot1"]["model"]
                preset_prompt = team["bot1"]["preset"]
                prompt = self.messages[-1]['content']
            else:
                model = team["bot2"]["model"]
                preset_prompt = team["bot2"]["preset"]
                prompt = "Continue"

            response = self.ask_openai(prompt, model, preset_prompt)

            if not self.running or self.paused:
                break

            self.convo_box.insert(tk.END, f"Bot {bot_turn}: {response}\n")
            self.messages.append({"role": "assistant", "content": response})
            self.exchange_count += 1

            bot_turn = 2 if bot_turn == 1 else 1

        if not self.paused:
            self.stop_convo()

    def ask_openai(self, prompt, model, preset_prompt):
        data = {
            "model": model,
            "messages": [{"role": "system", "content": preset_prompt}] + self.messages + [{"role": "user", "content": prompt}]
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
            self.messages.append({"role": "user", "content": prompt})
            return content

        except requests.RequestException as e:
            print(f"Request error: {e}")
            return f"Error: Unable to communicate with the OpenAI API."

    def organize_convo(self):
        thread = threading.Thread(target=self._organize_convo_thread)
        thread.start()

    def _organize_convo_thread(self):
        organized_text = self.get_organized_text()
        self.convo_box.insert(tk.END, f"Organizer Bot: {organized_text}\n")
        self.messages.append({"role": "assistant", "content": organized_text})

        # Allow organized text to be downloaded
        self.download_organized_convo(organized_text)

    def get_organized_text(self):
        full_convo = self.convo_box.get("1.0", tk.END)
        prompt = f"Organize and structure the following conversation into a cohesive and detailed plan:\n{full_convo}"
        team = TEAMS[self.team_var.get()]
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
                return f"Error: {error_message}"

            organized_text = response_data["choices"][0]["message"]["content"]
            return organized_text

        except requests.RequestException as e:
            print(f"Request error: {e}")
            return f"Error: Unable to communicate with the OpenAI API."

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
            self.center_chat_box.insert(tk.END, f"You: {message}\n")
            self.center_chat_entry.delete(0, tk.END)
            # Send the message to OpenAI API and get the response
            threading.Thread(target=self._send_center_chat_thread, args=(message,)).start()

    def _send_center_chat_thread(self, message):
        data = {
            "model": "gpt-3.5-turbo",
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
