import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
import requests
import json
import threading
from tkinter import filedialog

# OpenAI setup
API_URL = "https://api.openai.com/v1/chat/completions"

HEADERS = {
    "Authorization": "Bearer YOUR_API_KEY_HERE",
    "Content-Type": "application/json"
}

# Define teams of bots with complementary roles and preset prompts
TEAMS = {
    "Social Media Campaign": {
        "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a social media strategist. Plan a social media campaign."},
        "bot2": {"model": "gpt-3.5-turbo", "preset": "You are a content creator. Create engaging content for the campaign. When asked to continue, provide detailed content ideas."}
    },
    "Tech Support": {
        "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a tech support specialist. Identify and troubleshoot issues."},
        "bot2": {"model": "gpt-3.5-turbo", "preset": "You are a solutions architect. Provide solutions to tech issues. When asked to continue, provide detailed solutions."}
    },
    "Creative Writing": {
        "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a creative writer. Develop a plot for a short story."},
        "bot2": {"model": "gpt-3.5-turbo", "preset": "You are an editor. Edit and enhance the story. When asked to continue, provide editing suggestions."}
    },
    "Financial Planning": {
        "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a financial planner. Create a financial plan."},
        "bot2": {"model": "gpt-3.5-turbo", "preset": "You are an investment advisor. Suggest investment options. When asked to continue, provide detailed investment advice."}
    },
    "Customer Support": {
        "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a customer service representative. Greet the customer and gather information about their issue."},
        "bot2": {"model": "gpt-3.5-turbo", "preset": "You are a problem solver. Provide solutions to the customer's issue. When asked to continue, offer additional troubleshooting steps or escalate the issue."}
    },
    "Marketing Strategy": {
        "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a marketing strategist. Develop a comprehensive marketing strategy."},
        "bot2": {"model": "gpt-3.5-turbo", "preset": "You are a content creator. Create engaging content that aligns with the marketing strategy. When asked to continue, provide content ideas and execution plans."}
    },
    "Health and Wellness": {
        "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a nutritionist. Provide advice on balanced diets and healthy eating habits."},
        "bot2": {"model": "gpt-3.5-turbo", "preset": "You are a fitness coach. Suggest workout routines and fitness tips. When asked to continue, provide detailed workout plans and fitness guidance."}
    },
    "Product Development": {
        "bot1": {"model": "gpt-3.5-turbo", "preset": "You are a product manager. Outline the product development process."},
        "bot2": {"model": "gpt-3.5-turbo", "preset": "You are a product designer. Create design concepts and prototypes. When asked to continue, provide detailed design ideas and improvements."}
    },
    "Event Planning": {
        "bot1": {"model": "gpt-3.5-turbo", "preset": "You are an event planner. Plan the event details and logistics."},
        "bot2": {"model": "gpt-3.5-turbo", "preset": "You are an event coordinator. Coordinate the event activities and schedule. When asked to continue, provide detailed coordination plans and schedules."}
    }
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

        # Team selection
        self.team_label = tk.Label(root, text="Select Team:")
        self.team_var = tk.StringVar(value="Social Media Campaign")
        self.team_dropdown = tk.OptionMenu(root, self.team_var, *TEAMS.keys())

        self.team_label.grid(row=0, column=0, sticky='w')
        self.team_dropdown.grid(row=0, column=1, sticky='w', padx=5)

        # Initial user prompt
        self.prompt_label = tk.Label(root, text="Initial User Prompt:")
        self.prompt_entry = tk.Entry(root, width=50)

        self.prompt_label.grid(row=1, column=0, sticky='w')
        self.prompt_entry.grid(row=1, column=1, columnspan=2, sticky='w', padx=5)

        # Conversation display and control buttons
        self.convo_box = scrolledtext.ScrolledText(root, width=70, height=20)
        self.convo_box.grid(row=3, column=0, columnspan=3, pady=10)

        self.start_button = tk.Button(root, text="Start", command=self.start_convo)
        self.stop_button = tk.Button(root, text="Stop", state=tk.DISABLED, command=self.stop_convo)
        self.save_button = tk.Button(root, text="Save Convo", command=self.save_convo)

        self.start_button.grid(row=4, column=0, sticky='w')
        self.stop_button.grid(row=4, column=1, sticky='w')
        self.save_button.grid(row=4, column=2, sticky='w')

        self.running = False
        self.messages = [{"role": "system", "content": "You are a helpful assistant."}]

    def ask_api_key(self):
        return simpledialog.askstring("API Key", "Please enter your OpenAI API key:", show='*')

    def start_convo(self):
        self.start_button['state'] = tk.DISABLED
        self.stop_button['state'] = tk.NORMAL
        self.running = True
        initial_prompt = self.prompt_entry.get()
        self.messages.append({"role": "user", "content": initial_prompt})
        self.convo_box.insert(tk.END, f"User: {initial_prompt}\n")
        thread = threading.Thread(target=self.convo_loop)
        thread.start()

    def stop_convo(self):
        self.running = False
        self.start_button['state'] = tk.NORMAL
        self.stop_button['state'] = tk.DISABLED

    def convo_loop(self):
        bot_turn = 1
        team = TEAMS[self.team_var.get()]
        while self.running:
            if bot_turn == 1:
                model = team["bot1"]["model"]
                preset_prompt = team["bot1"]["preset"]
                prompt = self.messages[-1]['content']
            else:
                model = team["bot2"]["model"]
                preset_prompt = team["bot2"]["preset"]
                prompt = "Continue"

            response = self.ask_openai(prompt, model, preset_prompt)

            if not self.running:
                break

            self.convo_box.insert(tk.END, f"Bot {bot_turn}: {response}\n")
            self.messages.append({"role": "assistant", "content": response})

            bot_turn = 2 if bot_turn == 1 else 1

    def ask_openai(self, prompt, model, preset_prompt):
        data = {
            "model": model,
            "messages": [{"role": "system", "content": preset_prompt}] + self.messages + [{"role": "user", "content": prompt}]
        }

        try:
            response = requests.post(API_URL, headers=HEADERS, json=data)
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

    def save_convo(self):
        convo_content = self.convo_box.get("1.0", tk.END)
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(convo_content)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatGPTConvoApp(root)
    root.mainloop()
