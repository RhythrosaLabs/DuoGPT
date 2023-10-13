import tkinter as tk
from tkinter import scrolledtext
import requests
import json
import openai
import threading
from tkinter import filedialog


# OpenAI setup
API_URL = "https://api.openai.com/v1/chat/completions"

HEADERS = {
    "Authorization": "Bearer YOUR_API_KEY_HERE",
    "Content-Type": "application/json"
}

class ChatGPTConvoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ChatGPT Convo with Function Calls")

        self.save_button = tk.Button(root, text="Save Convo", command=self.save_convo)
        self.save_button.grid(row=3, column=2, sticky='w')

        self.start_button = tk.Button(root, text="Start", command=self.start_convo)
        self.stop_button = tk.Button(root, text="Stop", state=tk.DISABLED, command=self.stop_convo)
        self.convo_box = scrolledtext.ScrolledText(root, width=70, height=20)

        self.start_button.grid(row=3, column=0, sticky='w')
        self.stop_button.grid(row=3, column=1, sticky='w')
        self.convo_box.grid(row=1, column=0, columnspan=2, pady=10)

        self.running = False
        self.messages = [{"role": "system", "content": "You are a helpful assistant."}]

        self.prompt_label = tk.Label(root, text="Initial Prompt:")
        self.prompt_entry = tk.Entry(root, width=50)

        self.prompt_label.grid(row=0, column=0, sticky='w')
        self.prompt_entry.grid(row=0, column=1, columnspan=2, sticky='w', padx=5)

    def start_convo(self):
        self.start_button['state'] = tk.DISABLED
        self.stop_button['state'] = tk.NORMAL
        self.running = True
        thread = threading.Thread(target=self.convo_loop)
        thread.start()

    def stop_convo(self):
        self.running = False
        self.start_button['state'] = tk.NORMAL
        self.stop_button['state'] = tk.DISABLED

    def convo_loop(self):
        if not self.running:
            return

        if len(self.messages) == 1:
            prompt = self.prompt_entry.get()
            user_message = {"role": "user", "content": prompt}
            self.messages.append(user_message)
        else:
            prompt = self.messages[-1]["content"]

        agent_response = self.run_conversation(prompt, role="assistant")
        self.messages.append({"role": "assistant", "content": agent_response})

        # Schedule GUI update in the main thread
        self.root.after(0, lambda: self.convo_box.insert(tk.END, f"ChatBot1 (Agent): {agent_response}\n"))

        user_sim_response = self.run_conversation(agent_response, role="user")
        self.messages.append({"role": "user", "content": user_sim_response})

        # Schedule GUI update in the main thread
        self.root.after(0, lambda: self.convo_box.insert(tk.END, f"ChatBot2 (User Sim): {user_sim_response}\n"))

        self.root.after(1000, self.convo_loop)

    def is_similar_response(self, resp1, resp2):
        # Placeholder similarity check. Can use more sophisticated methods.
        return resp1.strip() == resp2.strip()

    def truncate_messages(self):
        """Keeps the last N messages in the self.messages list."""
        max_messages = 10  # You can adjust this value as needed
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]

    def run_conversation(self, prompt, role="user"):
        """Initiate a conversation with the OpenAI API and return the response."""
        # Prepare the data
        data = {
            "model": "gpt-3.5-turbo",
            "messages": self.messages + [{"role": role, "content": prompt}]
        }

        try:
            # Send request to OpenAI API
            response = requests.post(API_URL, headers=HEADERS, json=data)
            response.raise_for_status()  # Raise an exception for HTTP errors

            response_data = response.json()

            # Check if the expected data is present
            if "choices" not in response_data:
                error_message = response_data.get("error", {}).get("message", "Unknown error")
                print(f"Error from OpenAI API: {error_message}")
                return f"Error: {error_message}"

            content = response_data["choices"][0]["message"]["content"]
            self.messages.append({"role": role, "content": prompt})  # Append the message after successful API call
            return content

        except requests.RequestException as e:
            print(f"Request error: {e}")
            return f"Error: Unable to communicate with the OpenAI API."

    def save_convo(self):
        # Get the conversation content from the convo_box
        convo_content = self.convo_box.get("1.0", tk.END)

        # Ask the user where they want to save the file
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"),
                                                            ("All files", "*.*")])
        if not file_path:  # If the user cancels the save dialog
            return

        # Write the content to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(convo_content)


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatGPTConvoApp(root)
    root.mainloop()
