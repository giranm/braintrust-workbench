# Multi Agent Chat Demo

**Interactive weather chat with AI tool calling and full Braintrust observability**

## Overview

This project showcases **Braintrust Observability** through an interactive web-based weather chat assistant that demonstrates:

- Real-time tool calling (weather API integration)
- Agent conversation tracing with Anthropic Claude
- Web UI built with Reflex
- Full observability of tool usage and LLM interactions

**Type**: Python (Web App)
**Focus**: Observability, Tool Use, Interactive Chat

## What This Demonstrates

- ✅ **Interactive Web UI**: Real-time chat interface built with Reflex
- ✅ **Tool Calling**: Weather data fetching via Open-Meteo API
- ✅ **Agent Conversation Logging**: Full Braintrust tracing of chat interactions
- ✅ **Tool Use Tracing**: Monitor tool calls, inputs, and results
- ✅ **Multi-agent orchestration** (CLI demo still available)

## Prerequisites

**Option 1: Docker (Recommended)**
- [Docker](https://docs.docker.com/get-docker/) (20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (2.0+)
- Braintrust account ([sign up](https://www.braintrust.dev/))
- Anthropic API key ([get one](https://console.anthropic.com/))

**Option 2: Local Development**
- [mise](https://mise.jdx.dev/) installed
- Braintrust account ([sign up](https://www.braintrust.dev/))
- Anthropic API key ([get one](https://console.anthropic.com/))

## Quick Start

### 🐳 Docker (Recommended)

```bash
# Navigate to project
cd projects/multi-agent-chat-demo

# Set up environment
cp .env.example .env
# Edit .env with your API keys:
#   BRAINTRUST_API_KEY=your-braintrust-key
#   ANTHROPIC_API_KEY=your-anthropic-key

# Start with Docker Compose
docker compose up

# Or use Make commands
make setup    # Create .env file
make up       # Start containers
```

Open your browser to `http://localhost:3000` and start chatting about weather!

**Docker Commands:**

| Command | Description |
|---------|-------------|
| `make up` | Start in foreground (see logs) |
| `make up-d` | Start in background (detached) |
| `make down` | Stop and remove containers |
| `make logs` | View logs in real-time |
| `make shell` | Open shell in container |
| `make test` | Run tests in container |
| `make test-weather` | Test weather tool |
| `make rebuild` | Rebuild from scratch |
| `make clean` | Remove containers, volumes, images |
| `make help` | Show all 30+ commands |

**Troubleshooting:**
- Port already in use: `lsof -ti:3000 | xargs kill -9` (or 8000)
- Container won't start: `make logs` to check errors
- Changes not reflected: `make restart`
- Full reset: `make clean && make up`

### 💻 Local Development (Without Docker)

```bash
# Navigate to project
cd projects/multi-agent-chat-demo

# Install tools
mise install

# Sync dependencies
uv sync

# Set up environment
cp .env.example .env
# Edit .env with your BRAINTRUST_API_KEY and ANTHROPIC_API_KEY

# Initialize Reflex
uv run reflex init

# Start the web app
uv run reflex run
```

Open your browser to `http://localhost:3000`

## Project Structure

```
multi-agent-chat-demo/
├── src/
│   ├── main.py                 # CLI multi-agent demo
│   ├── eval.py                 # Braintrust evaluations
│   ├── agents/
│   │   └── weather_agent.py    # Weather-augmented agent
│   ├── tools/
│   │   └── weather.py          # Weather API tool
│   └── reflex_app/
│       ├── app.py              # Reflex app entry
│       ├── state.py            # Chat state management
│       └── components.py       # UI components
├── evals/                      # Evaluation suite
│   ├── README.md              # Evaluation documentation
│   ├── scorers.py             # Reusable scorer functions
│   ├── weather_conversation.py  # Single-turn evals
│   ├── multi_turn_conversation.py  # Multi-turn evals
│   ├── setup_evals.py         # Dataset initialization
│   ├── run_all_evals.py       # Run all evaluations
│   └── datasets/              # Test case datasets
│       ├── sample_conversations.json
│       └── multi_turn_conversations.json
├── multi_agent_chat_demo.py    # Reflex entry point
├── rxconfig.py                 # Reflex configuration
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Docker Compose orchestration
├── .dockerignore              # Docker build exclusions
├── Makefile                    # Convenience commands (make help)
├── tests/                      # Tests
├── docs/                       # Development docs
└── pyproject.toml              # Dependencies
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
BRAINTRUST_API_KEY=your-braintrust-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

**Note**: The weather tool uses Open-Meteo API which requires no API key.

## Running

### 🐳 Using Docker (Recommended)

**Essential Commands:**

```bash
# Start/Stop
make up                        # Start and view logs
make up-d                      # Start in background
make down                      # Stop and remove

# Development
make logs                      # View logs
make shell                     # Open shell in container
make test                      # Run tests
make test-weather              # Test weather tool

# Maintenance
make restart                   # Restart containers
make rebuild                   # Rebuild from scratch
make clean                     # Remove everything

# Help
make help                      # Show all commands
```

**Advanced Docker Commands:**

```bash
# Direct Docker Compose usage
docker compose up -d                          # Start detached
docker compose logs -f                        # Follow logs
docker compose exec app /bin/bash             # Shell access
docker compose exec app uv run pytest         # Run tests
docker compose down -v                        # Remove with volumes
docker compose ps                             # Show status

# Backup/Restore
make backup                                   # Backup database
make restore BACKUP_FILE=backup.tar.gz        # Restore database
```

### Web Chat Interface (Primary Demo)

**With Docker:**
```bash
docker compose up
# Open browser to http://localhost:3000
```

**Local development:**
```bash
uv run reflex run
# Open browser to http://localhost:3000
# Try: "What's the weather in London?"
```

The web interface provides:
- Real-time chat with weather assistant
- Live tool calling visualization
- Full conversation history
- Loading states and error handling

### CLI Multi-Agent Demo

**With Docker:**
```bash
docker compose exec app uv run python src/main.py
```

**Local development:**
```bash
uv run python src/main.py
```

### Evaluations

This project includes a comprehensive evaluation suite with custom scorers and LLM-as-a-judge patterns.

**Setup (one-time):**
```bash
# With Docker
docker compose exec app uv run python evals/setup_evals.py

# Local development
uv run python evals/setup_evals.py
```

**Run evaluations:**

**With Docker:**
```bash
# Run all evaluations
docker compose exec app uv run python evals/run_all_evals.py

# Run single-turn only
docker compose exec app uv run python evals/weather_conversation.py

# Run multi-turn only
docker compose exec app uv run python evals/multi_turn_conversation.py
```

**Local development:**
```bash
# Run all evaluations
uv run python evals/run_all_evals.py

# Run single-turn only
uv run python evals/weather_conversation.py

# Run multi-turn only
uv run python evals/multi_turn_conversation.py
```

View results at: https://www.braintrust.dev/app

See **[evals/README.md](./evals/README.md)** for detailed documentation on:
- Custom scorers (tool call checking, faithfulness)
- LLM-as-a-judge scorers (helpfulness, accuracy, coherence)
- Adding new test cases
- Using scorers for online evaluation

### Tests

**With Docker:**
```bash
docker compose exec app uv run pytest
make test
```

**Local development:**
```bash
uv run pytest
```

**Test weather tool directly:**

With Docker:
```bash
make test-weather
```

Local:
```bash
uv run python -c "
import asyncio
from src.tools.weather import get_weather_for_city, format_weather_response
weather = asyncio.run(get_weather_for_city('Tokyo'))
print(format_weather_response(weather))
"
```

## How It Works

### Weather Chat Assistant

The primary demo is an interactive chat application that showcases tool calling:

1. **User Query**: User asks about weather in a city via web interface
2. **Agent Processing**: WeatherAgent (powered by Claude Haiku 4.5) analyzes the query
3. **Tool Calling**: Agent automatically calls weather tool when needed
4. **API Fetch**: Tool geocodes city and fetches current weather from Open-Meteo
5. **Response**: Agent presents weather data in a friendly, conversational format
6. **Braintrust Logging**: All steps are traced in Braintrust dashboard

### Technology Stack

- **Frontend**: Reflex (Python-based web framework)
- **LLM**: Anthropic Claude Haiku 4.5 (cost-effective, supports tool use)
- **Weather Data**: Open-Meteo API (free, no key required)
- **Observability**: Braintrust SDK with `@traced` decorators
- **Async HTTP**: httpx for non-blocking API calls

### Multi-Agent Orchestration (CLI)

The original CLI demo showcases multiple agents collaborating:

1. **Agent Setup**: Initialize multiple agents with different roles
2. **Orchestration**: Route tasks between agents based on expertise
3. **Logging**: Track all conversations and results in Braintrust

## Braintrust Integration

This project demonstrates Braintrust observability for:

- **Conversation Logging**: Track all chat interactions with full context
- **Tool Use Tracing**: Monitor weather API calls with inputs/outputs
- **Agent Performance**: Measure latency and token usage
- **Error Tracking**: Capture and analyze failures

### Traced Components

Every component uses the `@traced` decorator:

- `WeatherAgent.respond()`: Main agent logic
- `get_weather_for_city()`: Weather data fetching
- `get_coordinates()`: City geocoding
- `get_weather()`: Weather API calls

### Key Metrics

- **Response Time**: End-to-end latency from user query to response
- **Token Usage**: Input/output tokens per conversation turn
- **Tool Success Rate**: Weather API call success/failure rates
- **API Latency**: Time spent in external API calls

## Example Usage

### Web Interface

User: "What's the weather in Tokyo?"
Agent: *calls weather tool*
Agent: "🌤️ Weather in Tokyo:
       Condition: Clear sky
       Temperature: 12.5°C
       Wind Speed: 8.2 km/h
       Humidity: 45%

       Perfect weather for outdoor activities!"
```

### Braintrust Dashboard

View detailed traces showing:
- Full conversation flow
- Tool call execution (city geocoding + weather fetch)
- Token usage per turn
- API latency breakdown
- Error handling (if any)

Visit: https://www.braintrust.dev/app

## Customization

### Changing Agent Personality

Edit `src/agents/weather_agent.py` to modify the system prompt or response style.

### Adding New Tools

Create new tools in `src/tools/` following the weather tool pattern:
- Use `@traced` decorator for observability
- Define Anthropic tool schema
- Register in WeatherAgent.tools list

### Customizing the UI

Edit `src/reflex_app/components.py` to change colors, layout, or add new features.

## References

### Braintrust Resources
- **[Official Docs](https://www.braintrust.dev/docs)**: API reference, guides, concepts
  - [Getting Started](https://www.braintrust.dev/docs/getting-started)
  - [Evaluations](https://www.braintrust.dev/docs/guides/evals)
  - [Logging](https://www.braintrust.dev/docs/guides/logging)
  - [Python SDK](https://www.braintrust.dev/docs/reference/python)
- **[Cookbook](https://github.com/braintrustdata/braintrust-cookbook)**: Practical examples and tutorials
  - [Agent Tracing Examples](https://github.com/braintrustdata/braintrust-cookbook)

### Related Resources
- [Anthropic Claude Documentation](https://docs.anthropic.com/)
- [Anthropic Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Open-Meteo API Docs](https://open-meteo.com/en/docs)
- [Reflex Documentation](https://reflex.dev/docs/getting-started/introduction/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## Documentation

See the `docs/` directory for:
- **[planning.md](./docs/planning.md)**: Project goals, scope, and implementation plan
- **[implementation.md](./docs/implementation.md)**: Technical decisions and progress
- **[issues.md](./docs/issues.md)**: Known issues and resolutions
- **[changelog.md](./docs/changelog.md)**: Version history

## Learn More

- **Braintrust Docs**: https://www.braintrust.dev/docs
- **Braintrust Cookbook**: https://github.com/braintrustdata/braintrust-cookbook
- **Braintrust Community**: https://www.braintrust.dev/community

## Troubleshooting

### Docker Issues

**Port already in use:**
```bash
# Kill process on port 3000 or 8000
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

**Container won't start:**
```bash
make logs              # Check logs for errors
make rebuild           # Rebuild from scratch
```

**Changes not reflected:**
```bash
make restart           # Restart containers
make rebuild           # Full rebuild if needed
```

**Full reset:**
```bash
make clean             # Remove everything
make up                # Start fresh
```

### Application Issues

**Agent not responding:**
- Check `ANTHROPIC_API_KEY` in `.env`
- Ensure you have sufficient credits in your Anthropic account
- Restart containers: `make restart`

**Traces not appearing in Braintrust:**
- Verify `BRAINTRUST_API_KEY` is set correctly
- Check you're logged into the right project
- View logs: `make logs`

**City not found:**
- Use full city name (e.g., "New York" instead of "NYC")
- The geocoding API works best with official city names

**Reflex won't start (local development):**
```bash
uv sync --reinstall    # Reinstall dependencies
uv run reflex init     # Re-initialize Reflex
uv run reflex run      # Try running again
```

## License

MIT - See [LICENSE](../../LICENSE)
