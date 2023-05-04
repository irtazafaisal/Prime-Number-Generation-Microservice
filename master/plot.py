import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV data into a pandas DataFrame
df = pd.read_csv('resource_utilization.csv', names=['time', 'cpu_percent', 'memory_percent'])

# Convert the 'time' column to a datetime object
df['time'] = pd.to_datetime(df['time'], format='%m-%d-%Y %H:%M:%S')

# Plot the CPU and memory usage over time
fig, axes = plt.subplots(2, 1, figsize=(8, 8))
axes[0].plot(df['time'], df['cpu_percent'])
axes[0].set_ylabel('CPU %')
axes[1].plot(df['time'], df['memory_percent'])
axes[1].set_ylabel('Memory %')
plt.xlabel('Time')
plt.show()
