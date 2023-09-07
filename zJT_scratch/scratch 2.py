import numpy as np
import matplotlib.pyplot as plt

# Sample data (replace with your data)
line = np.sin(np.linspace(0, 4 * np.pi, 550))
key = 'Sample Data'

# Create the x-axis values in seconds
x_seconds = np.linspace(0, 20, len(line))  # Adjust the time range based on your data

# Create the plot with the x-axis in seconds
plt.plot(x_seconds, line, linestyle='-', label=key, color='blue', linewidth=1)

# Customize x-axis ticks and labels (adjust the range and step as needed)
plt.xticks(np.arange(0, max(x_seconds) + 1, 1))
plt.xlabel('Time (seconds)')

# Add other plot customizations as needed
plt.ylabel('Y-axis Label')
plt.title('Your Title')
plt.legend()

# Show the plot
plt.show()