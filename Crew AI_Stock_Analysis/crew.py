from typing import Any, Dict, List, Union

import yfinance as yf
from crewai import Crew

from tasks.analyse_task import get_stock_analysis
from tasks.trade_task import trade_decision
from tasks.prediction_task import predict_future_performance
from agents.analyst_agent import analyst_agent, analyst_agent_fallback, analyst_agent_normal
from agents.trader_agent import trader_agent, trader_agent_fallback, trader_agent_normal

stock_crew = Crew(
    agents=[analyst_agent, trader_agent],
    tasks=[get_stock_analysis, trade_decision, predict_future_performance],
    verbose=True
)

fallback_stock_crew = Crew(
    agents=[analyst_agent_fallback, trader_agent_fallback],
    tasks=[get_stock_analysis, trade_decision, predict_future_performance],
    verbose=True
)

normal_stock_crew = Crew(
    agents=[analyst_agent_normal, trader_agent_normal],
    tasks=[get_stock_analysis, trade_decision, predict_future_performance],
    verbose=True
)


def normalize_stock_input(stock: Any) -> str:
    if isinstance(stock, (list, tuple, set)):
        symbols = [str(item).strip().upper() for item in stock if str(item).strip()]
        return ", ".join(symbols)
    if isinstance(stock, str):
        return stock.strip().upper()
    return str(stock).strip().upper()


def is_groq_token_error(message: str) -> bool:
    text = (message or "").lower()
    return any(
        token_phrase in text
        for token_phrase in [
            "token",
            "quota",
            "rate limit",
            "rate_limit",
            "token limit",
            "token is complete",
            "token completed",
            "inference token",
            "token exhausted",
            "limit exceeded",
            "rate limited",
            "ratelimit",
        ]
    )


def free_rule_based_fallback(stock_symbol: str) -> Dict[str, Any]:
    ticker = yf.Ticker(stock_symbol)
    info = ticker.info
    current_price = info.get("regularMarketPrice")
    change = info.get("regularMarketChange")
    change_percent = info.get("regularMarketChangePercent")
    prev_close = info.get("regularMarketPreviousClose")
    day_high = info.get("dayHigh")
    day_low = info.get("dayLow")
    volume = info.get("volume")
    avg_volume = info.get("averageDailyVolume3Month")
    currency = info.get("currency", "USD")

    if current_price is None:
        return {
            "stock": stock_symbol,
            "source": "rule_based_fallback",
            "error": f"Could not fetch price for {stock_symbol}. Please check the symbol.",
        }

    if change_percent is None:
        change_percent = 0.0

    if change_percent <= -2.0:
        recommendation = "Buy"
        rationale = "Price is down significantly today, which may present a buying opportunity."
    elif change_percent >= 2.0:
        recommendation = "Sell"
        rationale = "Price is up significantly today, which may be a good time to take profits."
    else:
        recommendation = "Hold"
        rationale = "The stock is trading in a narrow range today, so holding may be the best course."

    prediction = (
        "Expect sideways movement over the next 1-3 months with moderate risk, "
        "based on today’s price action and average volume." if abs(change_percent) < 2.0 else
        "Momentum appears to favor the current direction, but macro and sector conditions should be monitored."
    )

    analysis = (
        f"Stock: {stock_symbol}\n"
        f"Price: {current_price} {currency}\n"
        f"Change: {change} ({round(change_percent, 2)}%)\n"
        f"Previous Close: {prev_close} {currency}\n"
        f"Day High / Low: {day_high} / {day_low} {currency}\n"
        f"Volume: {volume}\n"
        f"Average Volume: {avg_volume}\n"
    )

    return {
        "stock": stock_symbol,
        "source": "rule_based_fallback",
        "analysis": analysis,
        "recommendation": recommendation,
        "recommendation_rationale": rationale,
        "prediction": prediction,
        "note": "Returned fallback analysis without model inference due to token/quota limits.",
    }


def kickoff_stock(inputs: Union[Dict[str, Any], str, List[str]], use_fallback: bool = True) -> Any:
    if isinstance(inputs, dict):
        stock_value = (
            inputs.get("stock")
            or inputs.get("stocks")
            or inputs.get("symbol")
            or inputs.get("symbols")
        )
    else:
        stock_value = inputs

    normalized = normalize_stock_input(stock_value)
    if not normalized:
        raise ValueError("No stock symbol(s) provided for analysis.")

    payload = {"stock": normalized}
    if not use_fallback:
        return stock_crew.kickoff(inputs=payload)

    try:
        return stock_crew.kickoff(inputs=payload)
    except Exception:
        try:
            return fallback_stock_crew.kickoff(inputs=payload)
        except Exception:
            try:
                return normal_stock_crew.kickoff(inputs=payload)
            except Exception:
                return free_rule_based_fallback(normalized)
