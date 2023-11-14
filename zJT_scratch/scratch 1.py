import pandas as pd
import matplotlib.pyplot as plt

# Sample DataFrame creation (replace this with your actual DataFrame)
data = {
    'datetime': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
    'peakForce': [100, 110, 95, 105, 115],
    'leg': ['left', 'right', 'left', 'right', 'left']
}
df = pd.DataFrame(data)

# Convert 'datetime' column to datetime objects
df['datetime'] = pd.to_datetime(df['datetime'])

# Sort DataFrame by 'datetime' and 'leg'
sorted_df = df.sort_values(by=['leg', 'datetime'])

# Create two subplots for the two graphs
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))

# Graph 1: Boxplot sorted by date (left leg first, then right leg)
sorted_df.boxplot(column='peakForce', by='leg', ax=axes[0])
axes[0].set_title('Boxplot sorted by date (Left leg first, then Right leg)')

# Graph 2: Boxplot sorted by leg (left leg first, then right leg)
sorted_df.boxplot(column='peakForce', by='datetime', ax=axes[1])
axes[1].set_title('Boxplot sorted by leg (Left leg first, then Right leg)')

# Rotate x-axis labels for better visibility
plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45)

# Adjust layout
plt.tight_layout()

# Show the plots
plt.show()
