using HTTP
using JSON3
using DataFrames
using Dates
using CSV

"""
Fetch stock data from Yahoo Finance API
Returns DataFrame with columns: timestamp, open, high, low, close, volume
"""
function fetch_yahoo_finance(symbol::String, period::String="1mo", interval::String="1h")
    # Yahoo Finance API endpoint
    url = "https://query1.finance.yahoo.com/v8/finance/chart/$(symbol)"
    
    params = Dict(
        "period1" => string(Int(floor(datetime2unix(now() - Day(30))))),
        "period2" => string(Int(floor(datetime2unix(now())))),
        "interval" => interval,
        "events" => "history"
    )
    
    query_string = join(["$k=$v" for (k, v) in params], "&")
    full_url = "$url?$query_string"
    
    try
        response = HTTP.get(full_url)
        data = JSON3.read(String(response.body))
        
        # Extract relevant data
        result = data.chart.result[1]
        timestamps = result.timestamp
        quotes = result.indicators.quote[1]
        
        # Create DataFrame
        df = DataFrame(
            timestamp = unix2datetime.(timestamps),
            open = quotes.open,
            high = quotes.high,
            low = quotes.low,
            close = quotes.close,
            volume = quotes.volume
        )
        
        # Remove rows with missing data
        dropmissing!(df)
        
        return df
    catch e
        @error "Failed to fetch data for $symbol" exception=e
        return DataFrame()
    end
end

"""
Calculate basic statistics for the stock
"""
function calculate_statistics(df::DataFrame)
    if isempty(df)
        return Dict()
    end
    
    latest = df[end, :]
    previous = df[end-1, :]
    
    price_change = latest.close - previous.close
    price_change_pct = (price_change / previous.close) * 100
    
    # Calculate volatility (standard deviation of returns)
    returns = diff(log.(df.close))
    volatility = std(returns) * sqrt(252) * 100  # Annualized
    
    stats = Dict(
        "current_price" => round(latest.close, digits=2),
        "previous_price" => round(previous.close, digits=2),
        "price_change" => round(price_change, digits=2),
        "price_change_pct" => round(price_change_pct, digits=2),
        "daily_high" => round(maximum(df.high[end-23:end]), digits=2),
        "daily_low" => round(minimum(df.low[end-23:end]), digits=2),
        "volume" => Int(latest.volume),
        "volatility" => round(volatility, digits=2),
        "last_update" => Dates.format(latest.timestamp, "yyyy-mm-dd HH:MM:SS UTC")
    )
    
    return stats
end

"""
Save data to CSV file
"""
function save_to_csv(df::DataFrame, filename::String="data/bmnr_data.csv")
    mkpath(dirname(filename))
    CSV.write(filename, df)
    println("Data saved to $filename")
end

"""
Load historical data from CSV
"""
function load_from_csv(filename::String="data/bmnr_data.csv")
    if isfile(filename)
        return CSV.read(filename, DataFrame)
    else
        return DataFrame()
    end
end
