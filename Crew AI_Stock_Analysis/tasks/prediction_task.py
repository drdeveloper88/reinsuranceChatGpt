from crewai import Task
from agents.analyst_agent import analyst_agent
from tasks.analyse_task import get_stock_analysis

predict_future_performance = Task(
    description=(
        "Based on the current market data and historical trends for {stock}, provide a future prediction for the stock's performance. "
        "Analyze potential price movements, market conditions, and external factors that could influence the stock. "
        "Predict the stock's performance for the next 1-3 months, including expected price range and key drivers."
    ),
    expected_output=(
        "A detailed future prediction including:\n"
        "- Expected price range for the next 1-3 months\n"
        "- Key factors influencing the prediction (market trends, news, economic indicators)\n"
        "- Confidence level in the prediction\n"
        "- Potential risks and opportunities"
    ),
    agent=analyst_agent,
    context=[get_stock_analysis]  # Depends on the analysis task
)