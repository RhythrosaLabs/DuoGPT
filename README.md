# DuoGPT

A sophisticated and multifaceted ChatGPT conversation application based on Python and the OpenAI API. This application engages in interactive dialogs with specialized ChatGPT bots, executes code snippets, and provides a diverse array of conversation management tools.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Key Configuration](#api-key-configuration)
- [Contributing](#contributing)
- [License](#license)

## Features
- Interact with ChatGPT bots across various categories, including marketing and development.
- Engage with specialized bots for particular roles within each team, including strategists, developers, and expert analysts.
- Extract and organize dialog content, including code snippets, with the option to download organized outputs or code as a ZIP file.
- Start, pause, interject, and stop conversation flows with dedicated controls.
- Multi-threaded application architecture ensures a responsive interaction experience.
- Easily modify bot teams and settings through the TEAMS dictionary.

## Installation

This application requires Python installed on your system. The use of Python 3.6+ is recommended for compatibility.

1. Clone the repository:

    ```sh
    git clone https://github.com/your-username/chatgpt-convo-app.git
    cd chatgpt-convo-app
    ```

2. (Optional) Create and activate a virtual environment:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the necessary dependencies (if any are needed):

    ```sh
    pip install -r requirements.txt
    ```

## Usage

Run the application script using Python:

```sh
python chatgpt_convo_app.py
```

Upon launching, the application will prompt you to input your OpenAI API key, which is required for API communication to retrieve responses from ChatGPT bots.

## API Key Configuration

An API key from OpenAI is required for this application. You can obtain it by creating an account on OpenAI's platform.

- The application will ask for your API key upon initialization. Enter it in the designated prompt to proceed.

## Contributing
If you're interested in contributing, your input is welcome! Here's how you can do it:

1. Fork the repository.
2. Create a feature branch or a branch for your bug fix.
3. Commit your modifications with clear commit messages.
4. Push to the branch and open a pull request.

For significant changes, please open an issue first to discuss what you would like to change or add.

## License
This project is open-source and available under the [MIT License](LICENSE.txt). See the `LICENSE` file for more information.

