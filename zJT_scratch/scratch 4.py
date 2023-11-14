import pandas as pd
import matplotlib.pyplot as plt

# Sample data (replace this with your actual data)
data = {
    'leg': ['left', 'left', 'left', 'right', 'right', 'right', 'left', 'left', 'left', 'right', 'right', 'right',
            'left', 'left', 'left', 'left', 'right', 'right', 'right', 'right', 'left', 'left', 'left', 'left',
            'right', 'right', 'right', 'right'],
    'peak_force': [264.4260046, 263.8165044, 267.3170897, 78.30765188, 84.73303909, 89.53162608, 268.3041813,
                    176.201083, 274.1167682, 207.9601951, 117.133774, 154.0130339, 162.2055672, 228.5576723,
                    223.4729808, 233.4039604, 139.7503744, 150.7311791, 149.1640635, 150.8258907, 181.318211,
                    162.5178283, 253.1968963, 181.7984573, 182.5740288, 170.7425752, 172.6802579, 190.7598974],
    'col_timestamp_str': ['8/29/23 13:45', '8/29/23 13:47', '8/29/23 13:48', '8/29/23 13:53', '8/29/23 13:54',
                          '8/29/23 13:55', '8/29/23 13:57', '9/12/23 14:03', '9/12/23 14:04', '9/12/23 14:07',
                          '9/12/23 14:11', '9/12/23 14:12', '9/12/23 14:13', '9/26/23 13:53', '9/26/23 13:56',
                          '9/26/23 13:58', '9/26/23 14:00', '9/26/23 14:04', '9/26/23 14:06', '9/26/23 14:08',
                          '9/26/23 14:10', '10/24/23 14:01', '10/24/23 14:03', '10/24/23 14:05', '10/24/23 14:06',
                          '10/24/23 14:11', '10/24/23 14:13', '10/24/23 14:14']
}

# Convert 'col_timestamp_str' to datetime objects
data['col_timestamp_str'] = pd.to_datetime(data['col_timestamp_str'])

# Create DataFrame
df = pd.DataFrame(data)

# Extract date from 'col_timestamp_str' column
df['date'] = df['col_timestamp_str'].dt.date

#summarized_df = df.groupby(['date', 'leg'])['peak_force'].max().reset_index()
summarized_df = df.groupby(['date', 'leg'])['peak_force'].agg(['max', 'mean', 'median']).reset_index()
print(summarized_df)

#pivoted_df - will pivot out each of max mean and median values
pivoted_df = summarized_df.pivot(index='date', columns='leg')

#Rename the columns to reflect the leg and the aggregation function:
pivoted_df.columns = ['{}_{}'.format(func, leg) for leg, func in pivoted_df.columns]
pivoted_df.reset_index(inplace=True)

print('summarized')
print(pivoted_df)

exit()
###############################
pivoted_df = summarized_df.pivot(index='date', columns='leg', values='peak_force').reset_index()

print("big sample")
print(pivoted_df)

# Sample pivoted_df (replace this with your actual pivoted DataFrame)
# pivoted_df = pd.DataFrame({
#     'date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-08'],
#     'left': [100, 110, 115, 125],
#     'right': [120, 109, None, 108]
# })

print("small sample")
print(pivoted_df)

# Convert 'date' column to date objects
pivoted_df['date'] = pd.to_datetime(pivoted_df['date'])

# Create the XY plot
fig, ax = plt.subplots(figsize=(8, 6))

# Plot 'left' values
ax.plot(pivoted_df['date'], pivoted_df['left'], marker='o', label='Left')

# Plot 'right' values
right_data = pivoted_df['right'].dropna()  # Exclude None values for the 'right' column
right_dates = pivoted_df['date'][pivoted_df['right'].notna()]  # Dates corresponding to non-None values in 'right'
ax.plot(right_dates, right_data, marker='o', label='Right')

# Format x-axis with date ticks
ax.set_xticks(pivoted_df['date'])
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

# Set labels and legend
ax.set_xlabel('Date')
ax.set_ylabel('Values')
ax.legend()

# Show the plot
plt.tight_layout()
plt.show()
