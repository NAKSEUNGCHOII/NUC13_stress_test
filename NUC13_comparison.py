import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# File paths for the CSV files
file_path = [
    r"C:\Users\User\Desktop\Hello2\NUC_13_stress\stress_test\incremental_cpu_stress_test_results_00000787.csv",
    r"C:\Users\User\Desktop\Hello2\NUC_13_stress\stress_test\incremental_cpu_stress_test_results_00000788.csv",
    r"C:\Users\User\Desktop\Hello2\NUC_13_stress\stress_test\incremental_cpu_stress_test_results_00000789.csv",
    r"C:\Users\User\Desktop\Hello2\NUC_13_stress\stress_test\incremental_cpu_stress_test_results_55555551.csv"
]

# Plotting
plt.figure(figsize=(12, 6))

window_size = 60
# Store the start timestamps for each file
start_timestamps = []

# Loop through each file and plot its 'Throttle' data with segmentation and smoothing
for count, path in enumerate(file_path):
    # Read the CSV file
    df = pd.read_csv(path)
    # Convert the 'Timestamp' column to datetime format
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    
    segments = []
    current_segment = []

    for _, row in df.iterrows():
        if pd.isna(row['Timestamp']):
            if current_segment:
                segments.append(current_segment)
                if count == 0:
                    start_timestamps.append(current_segment[0].Timestamp)
                current_segment = []
        else:
            current_segment.append(row)
    if current_segment:
        segments.append(current_segment)
        if count == 0:
            start_timestamps.append(current_segment[0]['Timestamp'])  # Last segment start timestamp
    
    # Combine all segments back into a DataFrame
    combined_data = pd.concat([pd.DataFrame(segment) for segment in segments], ignore_index=True)
    
    # Apply Moving Average (Smoothing)
    window_size = 60  # You can adjust the window size based on your preference
    combined_data['Throttle'] = combined_data['Throttle'].rolling(window=window_size, min_periods=1).mean()

    # Filter out and plot only the core temperatures
    plt.plot(combined_data['Timestamp'], combined_data['Throttle'], label=f'Device {count + 1} ({file_path[count][-12:-4]})')

for i, start_time in enumerate(start_timestamps):
    plt.axvline(x=start_time, color='red', linestyle='--', linewidth=0.5, label='CPU usage (5%-100%)' if i == 0 else "")
    
    # Add a label near the vertical line
    plt.text(
        start_time,  # x-coordinate (aligned with the vertical line)
        plt.ylim()[1] * 0.45,  # y-coordinate (adjusted to 90% of the y-axis maximum)
        f'{(i + 1) * 5}%',  # Label text
        rotation=0,  # Rotate text vertically
        color='red',  # Text color
        fontsize=8,  # Text size
        ha='center',  # Horizontal alignment
        va='top'  # Vertical alignment
    )

# Formatting the plot
plt.xlabel('Time')
plt.ylabel('CPU Temperature (°C)')
plt.title('Temp Over Time for 4 NUCs')
plt.xticks(rotation=45)
plt.grid(True)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

# Add a legend
plt.legend()

# Adjust layout
plt.tight_layout()

# Show the plot
plt.show()
