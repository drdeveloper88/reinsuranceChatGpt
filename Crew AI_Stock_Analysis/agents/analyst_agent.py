from crewai import Agent, LLM

from tools.stock_research_tool import get_stock_price

# initialize the llms
PRIMARY_LLM_MODEL = "groq/llama-3.3-70b-versatile"
FALLBACK_LLM_MODEL = "gpt-4o-mini"
NORMAL_LLM_MODEL = "gpt-3.5-turbo"

primary_llm = LLM(
    model=PRIMARY_LLM_MODEL,
    temperature=0.1
)

fallback_llm = LLM(
    model=FALLBACK_LLM_MODEL,
    provider="openai",
    temperature=0.1
)

normal_llm = LLM(
    model=NORMAL_LLM_MODEL,
    provider="openai",
    temperature=0.1
)

analyst_agent = Agent(
    role="Financial Market Analyst",
    goal=("Perform in-depth evaluations of publicly traded stocks using real-time data, "
          "identifying trends, performance insights, and key financial signals to support decision-making."),
    backstory=("You are a veteran financial analyst with deep expertise in interpreting stock market data, "
               "technical trends, and fundamentals. You specialize in producing well-structured reports that evaluate "
               "stock performance using live market indicators."),
    llm=primary_llm,
    tools=[get_stock_price],
    verbose=True
)

analyst_agent_fallback = Agent(
    role=analyst_agent.role,
    goal=analyst_agent.goal,
    backstory=analyst_agent.backstory,
    llm=fallback_llm,
    tools=[get_stock_price],
    verbose=True
)

analyst_agent_normal = Agent(
    role=analyst_agent.role,
    goal=analyst_agent.goal,
    backstory=analyst_agent.backstory,
    llm=normal_llm,
    tools=[get_stock_price],
    verbose=True
)
