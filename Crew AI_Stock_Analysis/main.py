from dotenv import load_dotenv

from crew import kickoff_stock

load_dotenv()

def run(stock: str):
    result = kickoff_stock(inputs={"stock": stock})
    print(result)


if __name__ == "__main__":
    run("AAPL")