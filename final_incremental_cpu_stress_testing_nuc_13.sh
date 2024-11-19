#!/bin/bash

LOG_FILE="incremental_cpu_stress_test_results_55555551.csv"

NUM_CORES=$(nproc)
DURATION=1
declare -A prev_freq

# Create log file with headers if it doesn't exist
if [ ! -f "$LOG_FILE" ]; then
	echo "Timestamp,Core 0 Temp (°C),Core 4 Temp (°C),Core 8 Temp (°C),Core 12 Temp (°C),Core 16 Temp(°C),Core 17 Temp(°C),Core 18 Temp (°C),Core 19 Temp(°C),Core 20 Temp(°C),Core 21 Temp(°C),Core 22 Temp(°C),Core 23 Temp(°C),Throttle,Undervoltage,CPU Usage (%)" > "$LOG_FILE"
fi

# Function to get the temperature for each core and store them in an array
get_core_temps() {
    core_temps=()  # Array to store core temperatures
    core_index=0  # Index to track core number

    # Loop through each core and get its temperature
    for core_temp in $(sensors | grep -i 'Core' | awk '{print $3}' | cut -c2-5); do
        # Add core temperature to array
        core_temps[$core_index]="$core_temp"
        core_index=$((core_index + 1))
    done

    # Return the core temperature array (if needed, you can process it further here)
    echo "${core_temps[@]}"
}

# Function to check if the CPU frequency is capped
check_frequency_cap() {
    local throttling_flag="NO"

    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq; do
        cur_freq=$(cat "$cpu")
        core=$(basename $(dirname "$cpu"))

        if [[ -z "${prev_freq[$core]}" ]]; then
            prev_freq[$core]=$cur_freq
            continue
        fi

        diff=$((cur_freq - prev_freq[$core]))

        if [[ ${prev_freq[$core]} -gt 0 ]]; then
            percentage_diff=$(( (100 * diff) / prev_freq[$core] ))
        else
            percentage_diff=0
        fi

        if (( percentage_diff <= 5 && percentage_diff >= -5 )); then
            throttling_flag="YES"
        fi

        prev_freq[$core]=$cur_freq
    done

    echo "$throttling_flag"
}

# Function to check if thermal throttling is likely
check_throttling() {
    temp=$(cat /sys/class/thermal/thermal_zone1/temp)
    temp_celsius=$((temp / 1000))

    echo "$temp_celsius"

#    if [ "$temp_celsius" -ge 90 ]; then
#        echo "Possible"
#    else
#	    echo "Not likely"
    #fi
}

# Function to check undervoltage
check_undervoltage() {
    undervoltage=$(cat /sys/class/power_supply/AC/voltage_now 2>/dev/null)
    if [ -z "$undervoltage" ]; then
        undervoltage="No"
    else
        undervoltage="$undervoltage"
    fi
    echo "$undervoltage"
}

# Function to get CPU usage
get_cpu_usage() {
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    echo "$cpu_usage"
}

# Loop to increase CPU load from 5% to 100% in 5% increments
for load in {5..100..5}; do
    # Start stress-ng with the specified CPU load (run for 30 minutes = 1800 seconds)
    echo "cpu load $load: " >> "$LOG_FILE"
    TIMEOUT=1800  # 30 minutes (1800 seconds)
    stress-ng --cpu $NUM_CORES --timeout $TIMEOUT --cpu-load $load &  # Timeout of 30 minutes (1800 seconds)

    # Reset SECONDS counter for this loop
    SECONDS=0  # Reset the SECONDS counter to start fresh for the 30-minute interval

    end_time=$((SECONDS + TIMEOUT))  # Track the end time of the 30-minute interval

    while [ $SECONDS -lt $end_time ]; do
        # Get current timestamp
        timestamp=$(date "+%Y-%m-%d %H:%M:%S")

        # Get temperature of each core and store it in the core_temps array
        core_temps=$(get_core_temps)

        # Get CPU frequency capped
        freq=$(check_frequency_cap)

        # Get throttling status
        throttle=$(check_throttling)

        # Get undervoltage status
        undervoltage=$(check_undervoltage)

        # Get CPU usage
        cpu_usage=$(get_cpu_usage)

        # Prepare the core temperatures for output (join them with commas)
        core_temp_output=$(echo "$core_temps" | tr ' ' ',')

        # Log the data to the CSV file
        echo "$timestamp,$core_temp_output,$throttle,$undervoltage,$cpu_usage%" >> "$LOG_FILE"

        # Sleep for the specified duration (1 second)
        sleep $DURATION
    done

    # Optional: Add a delay before starting the next load increment (for clarity)
    sleep 5  # Small delay before incrementing the load
done

