
# DuoGPTeam

ChatGPT Convo App is a versatile application that integrates OpenAI's GPT models and DALL-E for enhanced conversations, automated content creation, and graphic design. This app is designed to facilitate various team-based and solo tasks, leveraging AI capabilities to assist in development, marketing, business strategy, and more.

## Features

### Team-Based Conversations
- **Marketing Teams**: Generate and organize social media campaigns, content creation plans, and more.
- **Development Teams**: Assist in software development, providing code snippets and complete code blocks for Python, JavaScript, HTML, CSS, Java, C++, and more.
- **Data Science Teams**: Offer insights and solutions for data analysis and machine learning tasks.
- **Business Strategy Teams**: Develop business strategies, market analysis, and financial planning.
- **Graphic Design Teams**: Create images, album covers, logos, product designs, and character designs using DALL-E and GPT-4 Vision.
- **Music Teams**: Compose music, generate MIDI files, and design sounds with Python scripts.
- **Game Design Teams**: Write immersive game stories, design game levels, and create innovative game mechanics.

### Solo Mode Conversations
- Engage in one-on-one conversations with GPT models for personalized assistance, using various models including GPT-3.5-turbo, GPT-4, GPT-4-turbo, and DALL-E.

### Advanced Features
- **API Key Management**: Securely save and load your OpenAI API key.
- **Conversation Control**: Start, pause, interject, and stop conversations with ease.
- **Autostop Mode**: Set the number of message exchanges before autostop.
- **Contextual Right-Click Menu**: Quickly copy, cut, paste, and analyze text within the conversation.
- **Organize Conversations**: Automatically organize and structure conversations, extracting code snippets and creating zip files of scripts and images.
- **Save Conversations**: Save entire conversations to a text file for future reference.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Required Python packages: `tkinter`, `requests`, `json`, `threading`, `re`, `zipfile`, `os`, `pandas`, `io`, `PIL`, `subprocess`
- OpenAI API key

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/chatgpt-convo-app.git
    cd chatgpt-convo-app
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:
    ```bash
    python chatgpt_convo_app.py
    ```

### Usage

#### Starting a Conversation
1. Launch the application.
2. Enter your OpenAI API key when prompted.
3. Select a team and task from the dropdown menu.
4. Enter the initial user prompt and click "Start".
5. The conversation will begin with the selected team of bots.

#### Solo Mode
1. Select the desired model from the dropdown menu in the Solo Mode section.
2. Enter your message and click "Send".
3. The response from the selected model will appear in the conversation box.

#### Interjecting and Controlling the Conversation
- **Pause**: Click "Pause" to temporarily halt the conversation.
- **Interject**: Enter a new prompt in the "Interject Prompt" field and click "Interject" to steer the conversation.
- **Stop**: Click "Stop" to end the conversation.

#### Organizing and Saving Conversations
- **Organize**: Click "Organize" to structure the conversation and extract code snippets.
- **Save Convo**: Click "Save Convo" to save the entire conversation to a text file.

### Advanced Configuration
- **API Key Management**: The application will prompt for the API key on the first run. The key will be saved securely for future sessions.
- **Right-Click Menu**: Right-click on the conversation box to access options for copying, cutting, pasting, and analyzing text.

## Contributing
1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more information.

## Contact
For questions or support, please contact `your.email@example.com`.

Enjoy using the ChatGPT Convo App!
```
