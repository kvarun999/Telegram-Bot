# LLM-Powered Telegram Bot for Personalized College Newsletters

## 📖 About the Project
This project is a production-ready, containerized Telegram bot designed to deliver highly personalized college newsletters to students. To solve the problem of generic information overload, the bot synthesizes contextual updates using a local open-source Large Language Model (LLM). 

**Key Features & Architecture:**
* **Local LLM Orchestration:** Utilizes Ollama running locally to generate content, ensuring data privacy and cost-free inference.
* **Context-Aware Generation:** Leverages the Meta-Controller Protocol (MCP) to supply the LLM with real-time, external data through specialized tools (Campus Events, Course Reminders, and OpenWeatherMap forecasts).
* **Automated Delivery:** Integrates `APScheduler` to asynchronously generate and broadcast weekly newsletters to all active subscribers.
* **Fully Containerized:** Deployed via Docker and Docker Compose, ensuring a seamless, one-command setup across any environment.

## 📁 Repository Structure

```text
.
├── src/
│   ├── main.py          # FastAPI application & lifecycle management
│   ├── bot.py           # Telegram bot handlers & conversational logic
│   ├── database.py      # SQLAlchemy setup and database seeding
│   ├── models.py        # Database schema definitions
│   ├── tools.py         # MCP tool implementations (Weather, Events, Courses)
│   └── llm.py           # Local Ollama integration and generation logic
├── templates/
│   ├── events.j2        # Jinja2 prompt template for events
│   ├── courses.j2       # Jinja2 prompt template for courses
│   └── weather.j2       # Jinja2 prompt template for weather
├── data/                # Directory for SQLite database (auto-generated)
├── Dockerfile           # Python application container configuration
├── docker-compose.yml   # Multi-container orchestration (Bot + Ollama)
├── .env.example         # Template for environment variables
├── requirements.txt     # Python dependencies
├── submission.json      # Automated evaluation configuration
└── README.md            # Project documentation
```

## ⚙️ Prerequisites

Before building the project, ensure you have the following installed on your host machine:

* Git
* Docker & Docker Compose
* A Telegram Bot Token (obtainable via @BotFather on Telegram)
* An OpenWeatherMap API Key

## 🚀 Setup & Build Instructions (From Git)

Follow these instructions to clone the repository and spin up the complete application environment.

### 1. Clone the Repository

Open your terminal and clone the repository to your local machine:

```bash
git clone <YOUR_REPOSITORY_URL_HERE>
cd <YOUR_REPOSITORY_FOLDER_NAME>
```

**Note:** Replace the URL and folder name with your actual Git repository details.

### 2. Configure Environment Variables

The application relies on environment variables for secure configuration. A template file (`.env.example`) is provided.

Copy the template to create your active `.env` file:

```bash
cp .env.example .env
```

Open the `.env` file and replace the placeholder values with your actual keys:

```ini
TELEGRAM_BOT_TOKEN=your_actual_telegram_token_here
OPENWEATHERMAP_API_KEY=your_actual_weather_api_key_here
OLLAMA_BASE_URL=http://ollama:11434
DATABASE_URL=sqlite:///data/newsletter.db
```

### 3. Build and Run the Containers

The project is orchestrated using Docker Compose. Run the following command to build the Docker image, download the LLM, and start all services in detached mode:

```bash
docker-compose up --build -d
```

**Initialization Note:**
* On the very first run, the ollama container will automatically pull the LLM model. This process takes a few minutes depending on your internet connection.
* The bot container has a depends_on healthcheck and will wait patiently until the Ollama API is fully initialized and the model is loaded before starting the FastAPI server and Telegram polling.
* The SQLite database will be automatically created and seeded with test data upon startup.

You can monitor the startup sequence by viewing the logs:

```bash
docker-compose logs -f
```

## 🧪 Automated Evaluation Setup

This repository contains a `submission.json` file in the root directory. This file dictates the test user parameters (Chat ID, College, Program) and the target weather location for the automated grading scripts. Do not modify the structure of this file, as it is strictly required for the autograder.

## 📱 Using the Bot

Once the containers are healthy, open Telegram and interact with your bot:

* **Register:** Send `/start`. The bot will ask for your College and Program to tailor your experience.
* **On-Demand Newsletter:** Send `/newsletter`. The bot will fetch current weather, upcoming events, and your specific course reminders, passing them through the local LLM to generate a custom Markdown-formatted update.
* **Unsubscribe:** Send `/unsubscribe`. This safely deactivates your weekly automated deliveries without deleting your historical data.

## 🔌 Testing the MCP Tools

For evaluation and debugging, the internal MCP tools are exposed via a localized HTTP endpoint. You can test tool isolation by sending a POST request to `http://localhost:8000/test-mcp-tool`.

Example using curl:

```bash
curl -X POST http://localhost:8000/test-mcp-tool \
-H "Content-Type: application/json" \
-d '{"tool_name": "get_weather_forecast", "tool_args": {"location": "New York,US"}}'
```
