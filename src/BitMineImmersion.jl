module BitMineImmersion

using HTTP
using JSON3
using DataFrames
using Dates
using CSV

# Include submodules
include("fetch_stock_data.jl")
include("generate_html.jl")

# Export main functions
export fetch_yahoo_finance, calculate_statistics, save_to_csv, load_from_csv
export generate_html, generate_plot

end # module
