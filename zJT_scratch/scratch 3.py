import pandas as pd
import matplotlib.pyplot as plt

# Sample data (replace this with your actual data)
data = {
    'leg': ['left', 'left', 'left', 'right', 'right', 'right', 'left', 'left', 'left', 'right', 'right', 'right',
            'left', 'left', 'left', 'left', 'right', 'right', 'right', 'right', 'left', 'left', 'left', 'left',
            'right', 'right', 'right', 'right'],
    'peak_torque': [264.4260046, 263.8165044, 267.3170897, 78.30765188, 84.73303909, 89.53162608, 268.3041813,
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

# Group data by leg and date
grouped = df.groupby(['leg', 'date'])['peak_torque'].apply(list).reset_index(name='peak_torque')

# Create separate positions for left and right legs
left_positions = range(1, len(grouped[grouped['leg'] == 'left']) + 1)
right_positions = range(1, len(grouped[grouped['leg'] == 'right']) + 1)

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Plot left leg data
ax.boxplot(grouped[grouped['leg'] == 'left']['peak_torque'], positions=left_positions, labels=['left']*len(left_positions))

# Plot right leg data
ax.boxplot(grouped[grouped['leg'] == 'right']['peak_torque'], positions=right_positions, labels=['right']*len(right_positions))

ax.set_xlabel('Leg')
ax.set_ylabel('Peak Torque')
ax.set_xticks([pos - 0.5 for pos in left_positions] + [pos + 0.5 for pos in right_positions])
ax.set_xticklabels(['Left'] * len(left_positions) + ['Right'] * len(right_positions))
ax.set_title('Boxplots for Each Day\'s Data (Left and Right Legs)')

plt.tight_layout()
plt.show()
