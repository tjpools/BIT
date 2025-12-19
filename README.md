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

## Setup

### 1. Install Julia Dependencies

```bash
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

### 2. Run Locally

```bash
julia --project=. main.jl
```

This will:
- Fetch BMNR data from Yahoo Finance
- Save to `data/bmnr_data.csv`
- Generate `docs/index.html` and `docs/price_chart.png`

### 3. View Locally

Open `docs/index.html` in your browser.

### 4. Deploy to GitHub Pages

1. Push to GitHub
2. Go to Settings → Pages
3. Set source to "GitHub Actions"
4. The workflow will auto-deploy on push and hourly thereafter

## Why Julia?

- **Numerical computing strength**: Statistical analysis, volatility calculations
- **Plotting ecosystem**: Beautiful charts with Plots.jl
- **Fast enough**: Not assembly, but respects performance
- **Data science stack**: DataFrames, CSV, HTTP libraries
- **Toy universe friendly**: Easy to experiment and extend

## Extending the System

This is a **toy universe** for market analysis. Extensions:

1. **ETH correlation analysis** (test the "ETH would get this going" claim)
2. **Fibonacci level calculator** (measure actual vs predicted)
3. **Pattern detection** (quantify "symmetric movement" claims)
4. **Prediction tracking** (log external predictions, measure accuracy)
5. **Statistical hypothesis testing** (rigorous claim evaluation)

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
