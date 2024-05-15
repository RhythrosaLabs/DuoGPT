# DuoGPT

A minimalistic ChatGPT conversation application with integrated team roles, developed in Python utilizing the OpenAI API.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Key Configuration](#api-key-configuration)
- [Contributing](#contributing)
- [License](#license)

## Features
- Support for multiple bots with predefined roles including strategist, content creator, reviewer, and project manager for various scenarios like marketing, software development, etc.
- Image generation capabilities (commented out).
- Real-time chat interjections and conversation organization features.
- Multi-threaded design for non-blocking UI interaction.
- Save organized conversations and sessions.

## Installation

To use this app, you need Python installed on your machine. Python 3.6 or higher is recommended.

1. Clone the repository:

    ```sh
    git clone https://github.com/your-username/chatgpt-convo-app.git
    cd chatgpt-convo-app
    ```

2. (Recommended) Create and activate a virtual environment:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

Run the application script with Python:

```sh
python chatgpt_convo_app.py
```

When the application is first launched, you will be prompted to enter your OpenAI API key. This is necessary for the app to communicate with the OpenAI API and retrieve responses from ChatGPT bots.

## API Key Configuration

The app requires an API key to interact with OpenAI's API. An API key can be obtained from OpenAI's platform.

- Save your API key in a file called `api_key.json` at the root of the project directory.

    ```json
    {
        "api_key": "your-api-key"
    }
    ```

- The application will attempt to load this key on startup. If it can't find the file or if the key is missing, it will prompt you to enter the API key manually.

## Contributing
Contributions are welcome! Here's how you can help:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes with meaningful commit messages.
4. Push your branch and open a pull request.

For significant changes, please open an issue first to discuss what you would like to change.

## License
Distributed under the [MIT License](LICENSE.txt). See `LICENSE` for more information.

---
