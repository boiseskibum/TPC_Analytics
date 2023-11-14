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

summarized_df = df.groupby(['datetime', 'leg'])['peakForce'].max().reset_index()

pivoted_df = summarized_df.pivot(index='datetime', columns='leg', values='peakForce').reset_index()

# Sort DataFrame by 'datetime', 'left', and 'right'
sorted_df1 = pivoted_df.sort_values(by=['datetime', 'left', 'right'])

# Create boxplots for left and right legs, sorted by date
plt.figure(figsize=(10, 6))
sorted_df1.boxplot(column=['left', 'right'], by='datetime', widths=0.6)
plt.title('Boxplots of PeakForce Values (Left Leg First, Then Right Leg)')
plt.xlabel('Date')
plt.ylabel('PeakForce')
plt.xticks(range(1, len(sorted_df1['datetime']) + 1), sorted_df1['datetime'].dt.date, rotation=45)
plt.tight_layout()
plt.show()


# Create boxplots for left and right legs, grouped by date
plt.figure(figsize=(10, 6))
pivoted_df.boxplot(column=['left', 'right'], widths=0.6)
plt.title('Boxplots of PeakForce Values (Grouped by Date)')
plt.xlabel('Leg')
plt.ylabel('PeakForce')
plt.xticks([1, 2], ['Left', 'Right'])
plt.tight_layout()
plt.show()
