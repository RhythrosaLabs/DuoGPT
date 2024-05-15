# DuoGPT

DuoGPT is a Python-based desktop application that facilitates conversations between pairs of GPT-3.5-turbo bots with complementary roles. The application allows users to select from predefined teams of bots, each designed to work together on specific tasks such as planning social media campaigns, providing tech support, and more. Users can interject and steer the conversation as needed and set an autostop mode to limit the number of message exchanges.

## Features

- **Team Selection**: Choose from predefined teams of bots with complementary roles and preset prompts.
- **User Interjection**: Interject and steer the conversation at any point.
- **Autostop Mode**: Set a limit on the number of messages exchanged between the bots.
- **Save Conversations**: Save the conversation history to a text file.
- **Custom API Key**: Input your OpenAI API key securely at the start.

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/DuoGPT.git
    cd DuoGPT
    ```

2. Install the required dependencies:

    ```sh
    pip install requests tkinter
    ```

## Usage

1. Run the application:

    ```sh
    python DuoGPT.py
    ```

2. When prompted, enter your OpenAI API key.

3. Select a team from the dropdown menu.

4. Enter an initial user prompt to start the conversation.

5. Optionally, specify the number of message exchanges for autostop mode.

6. Click "Start" to begin the conversation between the bots.

7. Use the "Interject" button to steer the conversation at any point.

8. Click "Stop" to end the conversation manually.

9. Save the conversation using the "Save Convo" button.

## Teams

### Social Media Campaign

- **Bot 1**: Social Media Strategist
  - Preset: "You are a social media strategist. Plan a social media campaign."
- **Bot 2**: Content Creator
  - Preset: "You are a content creator. Create engaging content for the campaign. When asked to continue, provide detailed content ideas."

### Tech Support

- **Bot 1**: Tech Support Specialist
  - Preset: "You are a tech support specialist. Identify and troubleshoot issues."
- **Bot 2**: Solutions Architect
  - Preset: "You are a solutions architect. Provide solutions to tech issues. When asked to continue, provide detailed solutions."

### Creative Writing

- **Bot 1**: Creative Writer
  - Preset: "You are a creative writer. Develop a plot for a short story."
- **Bot 2**: Editor
  - Preset: "You are an editor. Edit and enhance the story. When asked to continue, provide editing suggestions."

### Financial Planning

- **Bot 1**: Financial Planner
  - Preset: "You are a financial planner. Create a financial plan."
- **Bot 2**: Investment Advisor
  - Preset: "You are an investment advisor. Suggest investment options. When asked to continue, provide detailed investment advice."

### Customer Support

- **Bot 1**: Customer Service Representative
  - Preset: "You are a customer service representative. Greet the customer and gather information about their issue."
- **Bot 2**: Problem Solver
  - Preset: "You are a problem solver. Provide solutions to the customer's issue. When asked to continue, offer additional troubleshooting steps or escalate the issue."

### Marketing Strategy

- **Bot 1**: Marketing Strategist
  - Preset: "You are a marketing strategist. Develop a comprehensive marketing strategy."
- **Bot 2**: Content Creator
  - Preset: "You are a content creator. Create engaging content that aligns with the marketing strategy. When asked to continue, provide content ideas and execution plans."

### Health and Wellness

- **Bot 1**: Nutritionist
  - Preset: "You are a nutritionist. Provide advice on balanced diets and healthy eating habits."
- **Bot 2**: Fitness Coach
  - Preset: "You are a fitness coach. Suggest workout routines and fitness tips. When asked to continue, provide detailed workout plans and fitness guidance."

### Product Development

- **Bot 1**: Product Manager
  - Preset: "You are a product manager. Outline the product development process."
- **Bot 2**: Product Designer
  - Preset: "You are a product designer. Create design concepts and prototypes. When asked to continue, provide detailed design ideas and improvements."

### Event Planning

- **Bot 1**: Event Planner
  - Preset: "You are an event planner. Plan the event details and logistics."
- **Bot 2**: Event Coordinator
  - Preset: "You are an event coordinator. Coordinate the event activities and schedule. When asked to continue, provide detailed coordination plans and schedules."

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or new features.

## License

This project is licensed under the MIT License.
