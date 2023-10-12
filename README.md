
# DuoGPT

A simple and powerful GUI application built in Python that facilitates dynamic conversations between two instances of OpenAI's ChatGPT. Experience the unique interplay of two AI conversationalists as they interact and build upon each other's responses.

## Features

- Seamless and dynamic conversation loop between two ChatGPT instances.
- Real-time iterative responses between the ChatGPT agents.
- Interactive, super straightforward GUI

## Examples of Utility

Having two ChatGPT instances communicate can be transformative:

- **Brainstorming:** One instance introduces an idea, and the other expands upon it, allowing for rapid ideation.
- **Debate Simulation:** The instances can present opposing viewpoints, helping to explore multifaceted arguments.
- **Quality Assurance:** One instance produces content, while the other critiques or edits it, ensuring optimal output.
- **Role-playing:** In gaming or storytelling, instances can adopt characters, crafting rich narratives.
- **Learning and Tutoring:** One poses as a student, the other as a tutor, crafting an interactive Q&A.
- **Problem Solving:** With complex issues, two agents collaboratively dissect and address challenges.

## Prerequisites

- OpenAI API key (attain one here: https://openai.com)
- Python 3.x
- tkinter
- requests
- openai library:
```bash
pip install openai
```


## Setup

1. Clone this repository
   
3. Navigate to the directory:
```bash
cd DuoGPT
```
3. Set up your OpenAI API key. Replace `YOUR_OPENAI_API_KEY` in the `duogpt.py` with your actual key.

> :warning: **Warning:** Never share API keys publicly. Use environment variables or external configurations for secrets.

4. Run the application:
```bash
python duogpt_app.py
```

## Usage

- Launch the application using the command above.
- Via the GUI, witness the real-time conversation between the ChatGPT agents.
- Initiate conversations with "Start" and conclude with "Stop".

## Contributing

Pull requests and feedback are welcome. For significant changes or enhancements, please open an issue first.

## License

This project is open source and available under the MIT License.
