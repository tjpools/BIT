#!/usr/bin/env julia
# Minimal test to fetch BMNR data

using Dates

println("Testing basic HTTP fetch without dependencies...")

# Use curl with proper headers
symbol = "BMNR"
now_ts = Int(floor(datetime2unix(now())))
month_ago_ts = Int(floor(datetime2unix(now() - Day(30))))

url = "https://query1.finance.yahoo.com/v8/finance/chart/$(symbol)?period1=$(month_ago_ts)&period2=$(now_ts)&interval=1d"

println("Fetching from: $url")
run(`curl -s -A "Mozilla/5.0" "$url" -o /tmp/bmnr_test.json`)

if isfile("/tmp/bmnr_test.json")
    println("✓ Data fetched successfully!")
    content = read("/tmp/bmnr_test.json", String)
    println("Response length: $(length(content)) bytes")
    println("\nFirst 500 chars:")
    println(content[1:min(500, length(content))])
else
    println("✗ Failed to fetch data")
end
