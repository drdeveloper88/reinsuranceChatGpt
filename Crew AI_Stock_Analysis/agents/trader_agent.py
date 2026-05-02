from crewai import Agent, LLM

PRIMARY_LLM_MODEL = "groq/llama-3.3-70b-versatile"
FALLBACK_LLM_MODEL = "gpt-4o-mini"
NORMAL_LLM_MODEL = "gpt-3.5-turbo"

primary_llm = LLM(
    model=PRIMARY_LLM_MODEL,
    temperature=0
)

fallback_llm = LLM(
    model=FALLBACK_LLM_MODEL,
    provider="openai",
    temperature=0
)

normal_llm = LLM(
    model=NORMAL_LLM_MODEL,
    provider="openai",
    temperature=0
)

trader_agent = Agent(
    role="Strategic Stock Trader",
    goal=(
        "Decide whether to Buy, Sell, or Hold a given stock based on live market data, "
        "price movements, and financial analysis with the available data."
    ),
    backstory=(
        "You are a strategic trader with years of experience in timing market entry and exit points. "
        "You rely on real-time stock data, daily price movements, and volume trends to make trading decisions "
        "that optimize returns and reduce risk."
    ),
    llm=primary_llm,
    tools=[],
    verbose=True
)

trader_agent_fallback = Agent(
    role=trader_agent.role,
    goal=trader_agent.goal,
    backstory=trader_agent.backstory,
    llm=fallback_llm,
    tools=[],
    verbose=True
)

trader_agent_normal = Agent(
    role=trader_agent.role,
    goal=trader_agent.goal,
    backstory=trader_agent.backstory,
    llm=normal_llm,
    tools=[],
    verbose=True
)
