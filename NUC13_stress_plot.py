import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# File path to the CSV file
file_path = r"C:\Users\User\Desktop\Hello2\NUC_13_stress\stress_test\incremental_cpu_stress_test_results_00000789.csv"
print(file_path)

# Check if the file exists
if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit()

# Read the CSV data into a Pandas DataFrame
data = pd.read_csv(file_path)

# Change the 'Timestamp' column to datetime format
data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

# Initialize variables for segmenting the data
segments = []
current_segment = []
start_timestamps = []  # To keep track of the starting timestamp of each segment

# Iterate through the rows to segment the data
for index, row in data.iterrows():

    if pd.isna(row['Timestamp']):  # Found a NaT (invalid timestamp)
        if current_segment:  # If we already have a segment collected
            segments.append(current_segment)  # Store the current segment
            start_timestamps.append(current_segment[0]['Timestamp'])  # Record the first timestamp of this segment
            current_segment = []  # Reset for next segment
    else:
        current_segment.append(row)  # Collect data when Timestamp is valid

# Last data segment
if current_segment:
    segments.append(current_segment)
    start_timestamps.append(current_segment[0]['Timestamp'])  # Last segment start timestamp

# Combine all segments back into a DataFrame
combined_data = pd.concat([pd.DataFrame(segment) for segment in segments], ignore_index=True)

# Apply Moving Average (Smoothing)
window_size = 60  # You can adjust the window size based on your preference
for core in combined_data.columns:
    if 'Temp' in core:  # Only apply smoothing to temperature columns
        # Apply a moving average to smooth the data
        combined_data[core] = combined_data[core].rolling(window=window_size, min_periods=1).mean()

# Plotting all CPU core temperatures
plt.figure(figsize=(12, 6))

# Filter out and plot only the core temperatures
for core in combined_data.columns:
    if 'Temp' in core:  # Only plot columns that represent core temperatures
        plt.plot(combined_data['Timestamp'], combined_data[core], label=core)

# Add vertical lines for the start of each segment
for i, start_time in enumerate(start_timestamps):
    plt.axvline(x=start_time, color='red', linestyle='--', linewidth=0.5, label='CPU usage (5%-100%)' if i == 0 else "")
    
    # Add a label near the vertical line
    plt.text(
        start_time,  # x-coordinate (aligned with the vertical line)
        plt.ylim()[1] * 0.42,  # y-coordinate (adjusted to 90% of the y-axis maximum)
        f'{(i + 1) * 5}%',  # Label text
        rotation=0,  # Rotate text vertically
        color='red',  # Text color
        fontsize=8,  # Text size
        ha='center',  # Horizontal alignment
        va='top'  # Vertical alignment
    )
# Labels and title
plt.xlabel('Time')
plt.ylabel('Temperature (°C)')
plt.title('Each Core Temperatures over Time')
plt.xticks(rotation=45)
plt.grid(True)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

# Legend
plt.legend()
# Adjust layout for better display
plt.tight_layout()
# Show the plot
plt.show()
