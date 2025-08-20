import openai
from datetime import datetime
import yfinance as yf
from openai import OpenAI
from config_manager import load_config

def get_stock_data(ticker="AAPL"):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1mo")  # 1-month history
    return {
        "name": stock.info.get("shortName", ticker),
        "history": hist,
        "current_price": hist['Close'].iloc[-1]
    }


def format_stock_history_for_prompt(history):
    """Convert history DataFrame to a clean string"""
    formatted = []
    for date, row in history.iterrows():
        date_str = date.strftime("%Y-%m-%d")
        price = row['Close']
        formatted.append(f"{date_str}: ${price:.2f}")
    return "\n".join(formatted)

def generate_stock_report(stock_data, user_command="brief report"):
    config = load_config()
    OPENAI_API_KEY = config.get("openai_api_key", "")

    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)

    """
    Generate an AI-based summary of stock history.

    stock_data: {
        'name': 'Apple Inc.',
        'history': pd.DataFrame from yfinance (DateTime index, 'Close' column),
        'current_price': float
    }

    user_command: str – e.g., "brief report", "updates since yesterday", etc.
    """
    history_str = format_stock_history_for_prompt(stock_data["history"])
    today = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""
You are a financial assistant. A user has requested a stock report for {stock_data['name']} as of {today}.

Current price: ${stock_data['current_price']:.2f}
Price history:
{history_str}

The user asked for: "{user_command}"

Keep your ansewr direct and brief. It should look like:
Bitcoin is at $100,000, a $1000 increase from some time ago (default to yesterday or one month ago) which is an 1% increase.
"""

    try:
        messages = [
            {"role": "system", "content": prompt},
        ]
        # Append memory history for context

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        raw_text = response.choices[0].message.content.strip()
        return raw_text
    except:
        return "sorry no info found"
