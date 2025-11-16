# FinLabs - Backend

A multiplayer financial simulation game designed to teach teenagers financial literacy through real-world economic scenarios. Players manage their finances, investments, and lifestyle choices while navigating historical economic events from 2008-2010.

## 📋 Overview

This backend API powers our financial literacy game. You can read more about the game in the [frontend repository](https://github.com/finlabs-junction/frontend).

## 🏗️ Architecture

Built with:

-   **Framework**: [Litestar](https://litestar.dev/) (modern async Python web framework)
-   **AI/ML**: OpenAI GPT-5.1 for financial tutoring and explanations
-   **Data**: Pandas + yfinance for stock market data
-   **Authentication**: JWT-based auth via Authlib
-   **Server**: Uvicorn ASGI server

## 📁 Project Structure

```
src/qs/
├── game/                      # Core game logic
│   ├── player.py             # Player state, finances, lifestyle
│   ├── session.py            # Game session management
│   ├── stocks.py             # Stock market data handling
│   └── priceMultiplier.py    # Dynamic pricing logic
├── nlp/                       # AI/NLP features
│   ├── chatbot.py            # Financial literacy chatbot
│   ├── llm.py                # LLM integration
│   └── embeddings.py         # Text embeddings
├── server/                    # API server
│   ├── routes.py             # HTTP endpoints
│   ├── schemas.py            # Request/response models
│   ├── services.py           # Business logic
│   └── dependencies.py       # Dependency injection
├── contrib/                   # Framework integrations
│   ├── litestar/             # Litestar configuration
│   ├── openai/               # OpenAI client
│   ├── redis/                # Redis client
│   ├── sqlalchemy/           # Database ORM
│   └── stripe/               # Payment integration
└── resources/                 # Data files
    ├── financial_events_2005_2010.csv
    └── finland_cost_of_living.csv

```

## 🚀 Getting Started

### Prerequisites

-   Python 3.12
-   Poetry (dependency manager)

### Installation

1. **Install dependencies:**

    ```bash
    poetry install
    ```

2. **Activate virtual environment:**

    ```bash
    poetry shell
    ```

3. **Set up environment variables:**
   Create a `.env` file with required configuration:
    ```bash
    QS_DEBUG=1                    # Enable debug mode
    OPENAI_API_KEY=your_key       # OpenAI API key
    ```

### Running the Server

**Production mode:**

```bash
qs run
```

**Debug mode:**

```bash
QS_DEBUG=1 qs run
```

The API will be available at `http://localhost:8000`

### Generate TypeScript Client

Generate TypeScript types for frontend integration:

```bash
qs schema typescript
```

> Output is saved to `/api-specs.ts`

## 🎯 API Endpoints

### Session Management

-   `POST /session/create` - Create a new game session
-   `POST /session/{session_id}/join` - Join an existing session
-   `GET /session/logout` - End user session

### Game Control

-   `POST /start` - Start the game session (leader only)
-   `POST /pause` - Pause time progression (leader only)
-   `POST /stop` - Stop the game session (leader only)
-   `GET /poll` - Get current game state (player stats, stocks, events)
-   `POST /set-time-progression-multiplier` - Adjust game speed

### Stock Trading

-   `POST /stock/{symbol}/buy` - Buy stock shares
-   `POST /stock/{symbol}/sell` - Sell stock shares
-   `POST /stock/{symbol}/liquidate` - Sell all shares
-   `GET /stock-prices` - Get historical stock prices
-   `GET /dividends` - Get dividend payment history

### Lifestyle Management

-   `GET /lifestyle/accommodations` - List available housing options
-   `POST /lifestyle/accommodations/move` - Change accommodation
-   `POST /set-monthly-grocery-expense` - Set food budget
-   `POST /set-monthly-leisure-expense` - Set entertainment budget

### AI Features

-   `POST /events/{event_id}/explanation` - Get AI explanation of economic events
-   `POST /explain-text` - Explain financial terms/concepts
-   `GET /evaluate-player-state` - Get AI financial advice
-   `POST /chat` - Chat with AI financial tutor

## 🎲 Game Mechanics

### Player Attributes

-   **Financial**: Balance, assets, equity, monthly income/expenses
-   **Well-being**: Health, happiness, energy, stress, social life
-   **Career**: Occupation, salary, career progress, skills/education
-   **Lifestyle**: Accommodation quality, location, living comfort

### Economic Events

Players can experience real historical events from 2005-2010:

### Stock Market

-   Real historical data from Yahoo Finance
-   Symbols: AAPL, GOOGL, MSFT, AMZN
-   Dividend payments
-   Price fluctuations based on actual 2005-2010 data provided by Perplexity

## 🤖 AI Integration

The game uses OpenAI's GPT models for:

1. **Event Explanations**: Contextual explanations of economic events
2. **Financial Tutoring**: Personalized advice based on player state
3. **Concept Explanations**: On-demand explanations of financial terms
4. **Interactive Chat**: Real-time Q&A with financial literacy focus

---

Built with ❤️ for Junction 2025
