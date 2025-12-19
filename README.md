# BitMine Immersion - BMNR Stock Tracker

A rigorous, epistemologically-grounded tracker for BitMine (BMNR) stock, built with Julia.

## Philosophy

This project applies formal systems thinking to market analysis:

- **Galois Principle**: Small cases lie; understand structural limits before extrapolating
- **GEB/Formal Systems**: Distinguish syntax from semantics, metaphor from mechanism
- **Emergent Complexity**: Causal structures change with scale
- **Assembly Discipline**: Know the hardware before abstracting
- **Toy Universe Method**: Solve constrained systems, then carefully scale

## Architecture

```
BitMineImmersion/
├── main.jl                  # Entry point
├── src/
│   ├── fetch_stock_data.jl  # Yahoo Finance API integration
│   └── generate_html.jl     # Static site generation
├── data/                    # Historical CSV data
├── docs/                    # Generated GitHub Pages site
└── .github/workflows/       # Hourly auto-update
```

## Features

- **Hourly updates** via GitHub Actions
- **Yahoo Finance data** (free tier, no API key needed)
- **Statistical analysis**: volatility, price changes, volume
- **Clean visualization**: Julia Plots for price history
- **GitHub Pages deployment**: Static site at `username.github.io/BitMineImmersion`

## 🔒 Security Features

This project implements enterprise-grade security practices:

1. **Rate Limiting & Retry Logic** - Exponential backoff for API calls
2. **Data Validation** - Comprehensive validation of all stock data
3. **Error Logging** - Structured logging with timestamps and stack traces
4. **Workflow Security** - SHA-pinned actions and exact version pinning
5. **Content Security Policy** - XSS protection for the web dashboard

See [SECURITY_FEATURES.md](SECURITY_FEATURES.md) for detailed documentation.

**Log Files:**
- `logs/fetch_and_generate.log` - Main tracker operations
- `logs/eth_correlation.log` - Correlation analysis
- `logs/fibonacci_calculator.log` - Fibonacci calculations
- `logs/prediction_tracker.log` - Prediction tracking

All logs include timestamps, log levels (INFO/WARNING/ERROR), and full stack traces for debugging.

## Setup

### Quick Start (Python)

```bash
# Fetch data and generate tracker
python3 fetch_and_generate.py

# Run ETH correlation analysis
python3 eth_correlation.py

# Calculate Fibonacci levels
python3 fibonacci_calculator.py

# Track predictions
python3 prediction_tracker.py
```

### Julia Version (Optional)

The project includes Julia implementations, but Python scripts work without dependencies.

```bash
julia --project=. main.jl  # Requires HTTP, JSON3, DataFrames, CSV
```

### View Tracker

Open `docs/index.html` in your browser to see the live tracker.

### 4. Deploy to GitHub Pages

1. Push to GitHub
2. Go to Settings → Pages
3. Set source to "GitHub Actions"
4. The workflow will auto-deploy on push and hourly thereafter

## Why Python + Julia?

**Python** (Primary):
- **Zero dependencies**: Works with just stdlib for core functionality
- **Universal**: Available on all systems
- **Rapid prototyping**: Quick iteration on analysis tools
- **Battle-tested**: Mature ecosystem for data work

**Julia** (Optional):
- **Numerical computing**: When performance matters
- **Type system**: More rigorous for complex calculations
- **REPL-driven**: Interactive exploration
- **Toy universe friendly**: Easy to experiment and extend

## Analysis Tools

This is a **toy universe** for market analysis. Tools implemented:

1. ✅ **ETH correlation analysis** - Test "ETH would get this going" claims
   - Pearson correlation coefficient
   - R² variance explanation
   - Statistical interpretation
   
2. ✅ **Fibonacci level calculator** - Validate Fibonacci predictions
   - Multiple swing scenarios
   - Retracement and extension levels
   - Reverse engineering of claims
   
3. ✅ **Prediction tracker** - Log and measure prediction accuracy
   - Track multiple predictions
   - Progress monitoring
   - Accuracy scoring

4. 🔲 **Pattern detection** (quantify "symmetric movement" claims)
5. 🔲 **Statistical hypothesis testing** (rigorous claim evaluation)
6. 🔲 **Sentiment analysis** (correlate social signals with price)

## The Filter

Every market claim about BMNR gets evaluated through:

1. Is the structure formally defined?
2. Are we extrapolating from insufficient cases?
3. Are abstractions hiding critical constraints?
4. Can this be tested in a simpler system first?
5. Where does the model break?

**Structure determines solvability. Formal foundations before claims.**

## License

MIT - Build, analyze, learn.
# Test
