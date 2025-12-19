#!/usr/bin/env julia

# Main script to fetch BMNR data and generate tracking page

using BitMineImmersion

function main()
    println("=" ^ 50)
    println("BitMine (BMNR) Tracker - Data Fetch & Update")
    println("=" ^ 50)
    
    # Fetch current data
    println("\n📊 Fetching BMNR data from Yahoo Finance...")
    df = fetch_yahoo_finance("BMNR", "1mo", "1h")
    
    if isempty(df)
        @error "Failed to fetch data. Exiting."
        return
    end
    
    println("✓ Fetched $(nrow(df)) data points")
    
    # Save to CSV for historical tracking
    println("\n💾 Saving data to CSV...")
    save_to_csv(df)
    
    # Calculate statistics
    println("\n📈 Calculating statistics...")
    stats = calculate_statistics(df)
    
    println("Current Price: \$$(stats["current_price"])")
    println("24h Change: $(stats["price_change"]) ($(stats["price_change_pct"])%)")
    
    # Generate HTML page
    println("\n🌐 Generating HTML page...")
    generate_html(df, stats)
    
    println("\n" * "=" ^ 50)
    println("✓ Update complete!")
    println("=" ^ 50)
end

# Run main function
main()
