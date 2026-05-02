import streamlit as st
from dotenv import load_dotenv
from crew import kickoff_stock
from batch_analysis import StockAnalysisBatch

load_dotenv()

st.title("🚀 Crew AI Stock Analysis with Future Predictions")

st.markdown("""
Analyze single or multiple stock symbols with AI-powered agents.
- **Single Stock**: Enter one symbol (e.g., AAPL)
- **Multiple Stocks**: Enter comma-separated symbols (e.g., AAPL, MSFT, GOOGL, NVDA, TSLA)

Features:
- Real-time market data and performance analysis
- Strategic buy/sell/hold recommendations
- 1-3 month future performance predictions
- Automatic token limit handling with fallback
""")

# Tabs for different input modes
tab1, tab2 = st.tabs(["Single Stock", "Batch Analysis"])

with tab1:
    st.markdown("### Analyze a Single Stock")
    stock_symbol = st.text_input("Stock Symbol", value="AAPL", placeholder="Enter stock symbol (e.g., AAPL)")
    
    if st.button("🔍 Analyze Stock", type="primary", key="single_analyze"):
        if stock_symbol.strip():
            with st.spinner("🤖 Running comprehensive AI analysis..."):
                try:
                    result = kickoff_stock(inputs={"stock": stock_symbol.upper()})
                    st.success("✅ Analysis Complete!")
                    
                    st.markdown("### 📊 Current Stock Analysis")
                    st.markdown("*Real-time market data and performance summary*")
                    
                    st.markdown("### 💼 Trading Recommendation")
                    st.markdown("*Strategic buy/sell/hold decision based on current data*")
                    
                    st.markdown("### 🔮 Future Performance Prediction")
                    st.markdown("*AI-powered forecast for the next 1-3 months*")
                    
                    st.markdown("### 📈 Complete Analysis Report")
                    st.write(result)
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
        else:
            st.warning("⚠️ Please enter a valid stock symbol.")

with tab2:
    st.markdown("### Batch Analysis - Multiple Stocks")
    
    # Example stock list
    example_stocks = "AAPL, MSFT, NVDA, AMZN, GOOGL, META, TSLA, BRK.B, JPM, V, JNJ, WMT, XOM, UNH, PG, MA, HD, CVX, ABBV, PFE, KO, COST, AVGO, MRK, PEPSI, NFLX, ORCL"
    
    col1, col2 = st.columns([3, 1])
    with col1:
        stocks_input = st.text_area(
            "Enter Stock Symbols (comma-separated)",
            value="AAPL, MSFT, GOOGL, NVDA, TSLA",
            height=100,
            placeholder="AAPL, MSFT, GOOGL,..."
        )
    
    with col2:
        st.markdown("#### Quick Presets")
        if st.button("📊 Tech", key="preset_tech"):
            st.session_state.stocks_input = "AAPL, MSFT, GOOGL, NVDA, TSLA, AMZN, META"
        if st.button("💰 Finance", key="preset_finance"):
            st.session_state.stocks_input = "JPM, GS, BAC, WFC, SCHW"
        if st.button("🏭 Industrial", key="preset_industrial"):
            st.session_state.stocks_input = "XOM, CVX, CAT, MMM, BA"
        if st.button("🏥 Healthcare", key="preset_health"):
            st.session_state.stocks_input = "JNJ, UNH, PFE, ABBV, MRK"
    
    # Parse stock symbols
    stock_list = [s.strip().upper() for s in stocks_input.split(",") if s.strip()]
    
    if stock_list:
        st.info(f"📋 Stocks to analyze: {len(stock_list)} | {', '.join(stock_list[:5])}{'...' if len(stock_list) > 5 else ''}")
    
    if st.button("🚀 Analyze Multiple Stocks", type="primary", key="batch_analyze"):
        if stock_list:
            batch_analyzer = StockAnalysisBatch()
            progress_bar = st.progress(0)
            status_text = st.empty()
            results_container = st.container()
            
            def update_progress(current, total, symbol, result):
                progress = current / total
                progress_bar.progress(progress)
                status_text.write(f"Processing: {current}/{total} - {symbol} - {result['status']}")
            
            with st.spinner(f"🤖 Analyzing {len(stock_list)} stocks..."):
                batch_results = batch_analyzer.analyze_batch(stock_list, update_progress)
            
            # Display summary
            st.success("✅ Batch Analysis Complete!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("✅ Successful", batch_results["summary"]["successful"])
            with col2:
                st.metric("❌ Failed", batch_results["summary"]["failed"])
            with col3:
                st.metric("📊 Total", batch_results["summary"]["total"])
            
            # Display successful results
            if batch_results["successful"]:
                st.markdown("### ✅ Successful Analyses")
                for symbol, data in batch_results["successful"].items():
                    with st.expander(f"📈 {symbol}", expanded=False):
                        st.write(data)
            
            # Display errors
            if batch_results["failed"]:
                st.markdown("### ❌ Failed Analyses")
                for symbol, error_info in batch_results["failed"].items():
                    error_type = error_info["type"]
                    error_msg = error_info["message"]
                    
                    if error_type == "rate_limited":
                        st.warning(f"⏳ **{symbol}**: Rate limited - {error_msg}")
                    else:
                        st.error(f"❌ **{symbol}**: {error_msg}")
        else:
            st.warning("⚠️ Please enter at least one valid stock symbol.")

st.markdown("---")
st.markdown("""
**Features:**
- 🔄 Automatic retry logic for rate-limited requests
- 📊 Real-time market data analysis
- 💼 Trading recommendations (Buy/Sell/Hold)
- 🔮 Future performance predictions
- 📈 Batch processing for multiple stocks

Built with CrewAI, Streamlit, and Groq LLM
""")