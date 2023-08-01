# bash command to download historical data

#!/bin/bash

# Loop through the years from 1960 to 2023
for year in {1960..2023}; do

    # Loop through the months from 1 to 12
    for month in {1..12}; do

        # Add leading zero for single-digit months
        month_padded=$(printf "%02d" $month)

        next_month=$((month + 1))

        # Handle December (month 12) separately
        if [ $month -eq 12 ]; then
            next_month=1
            next_year=$((year + 1))
        else
            next_year=$year
        fi

        next_month_padded=$(printf "%02d" $next_month)

        # Construct the URL with the date
        url="https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=${year}-${month_padded}-01&endtime=${next_year}-${next_month_padded}-01"

        wget $url
        gsutil cp "query?format=csv&starttime=${year}-${month_padded}-01&endtime=${next_year}-${next_month_padded}-01" gs://usgs_base_earthquakes

        # Print the URL for each month
        echo "Downloading from ${url}"
    done
done