from typing import List, Dict, Any
from crew import kickoff_stock

class StockAnalysisBatch:
    """Handle batch analysis of multiple stocks with token limit management"""
    
    def __init__(self, max_retries: int = 3, timeout_seconds: float = 120):
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.results = {}
        self.errors = {}
    
    def analyze_single_stock(self, stock_symbol: str) -> Dict[str, Any]:
        """Analyze a single stock with retry logic and timeout handling"""
        for attempt in range(self.max_retries):
            try:
                result = kickoff_stock(
                    inputs={"stock": stock_symbol.upper().strip()}
                )
                return {
                    "symbol": stock_symbol.upper(),
                    "status": "success",
                    "data": result,
                    "attempt": attempt + 1
                }
            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a token limit error
                if "rate_limit" in error_msg.lower() or "quota" in error_msg.lower():
                    if attempt < self.max_retries - 1:
                        wait_time = (attempt + 1) * 5  # Exponential backoff: 5s, 10s, 15s
                        return {
                            "symbol": stock_symbol.upper(),
                            "status": "rate_limited",
                            "wait_time": wait_time,
                            "attempt": attempt + 1,
                            "error": error_msg
                        }
                    else:
                        return {
                            "symbol": stock_symbol.upper(),
                            "status": "failed",
                            "attempt": attempt + 1,
                            "error": f"Rate limited after {self.max_retries} attempts: {error_msg}"
                        }
                else:
                    return {
                        "symbol": stock_symbol.upper(),
                        "status": "failed",
                        "attempt": attempt + 1,
                        "error": error_msg
                    }
        
        return {
            "symbol": stock_symbol.upper(),
            "status": "failed",
            "attempt": self.max_retries,
            "error": "Max retries exceeded"
        }
    
    def analyze_batch(self, stock_symbols: List[str], progress_callback=None):
        """
        Analyze multiple stocks with progress tracking and token limit handling
        
        Args:
            stock_symbols: List of stock symbols to analyze
            progress_callback: Optional callback function for progress updates
        
        Returns:
            Dictionary with results and errors
        """
        self.results = {}
        self.errors = {}
        total = len(stock_symbols)
        
        for idx, symbol in enumerate(stock_symbols):
            result = self.analyze_single_stock(symbol)
            
            if result["status"] == "success":
                self.results[symbol.upper()] = result["data"]
            elif result["status"] == "rate_limited":
                self.errors[symbol.upper()] = {
                    "type": "rate_limited",
                    "message": result["error"],
                    "wait_time": result["wait_time"]
                }
            else:
                self.errors[symbol.upper()] = {
                    "type": "error",
                    "message": result["error"]
                }
            
            if progress_callback:
                progress_callback(idx + 1, total, symbol, result)
        
        return {
            "successful": self.results,
            "failed": self.errors,
            "summary": {
                "total": total,
                "successful": len(self.results),
                "failed": len(self.errors)
            }
        }
