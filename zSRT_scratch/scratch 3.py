import pandas as pd
import matplotlib.pyplot as plt

# RIGHT Sample DataFrame
data = {
    'Date': ['2023-07-15', '2023-07-15', '2023-07-15', '2023-07-15'],
    'leg': ['R', 'R', 'R', 'R'],
    'Value': [10, 20, 30, 40]
}
df_R = pd.DataFrame(data)

# Add a new 'Trial' column using apply() and f-string formatting
df_R['Trial'] = df_R.apply(lambda row: f'T-{row.name + 1}', axis=1)
print(df_R)

df_R['combine'] = df_R['leg'] + " " + df_R['Trial']

# Select rows for a specific date (e.g., '2023-07-15')
selected_date = '2023-07-15'
selected_rows_R = df_R[df_R['Date'] == selected_date]

########################################################
# LEFT Sample DataFrame
data = {
    'Date': ['2023-07-15', '2023-07-15', '2023-07-15', '2023-07-15'],
    'leg': ['L', 'L', 'L', 'L'],
    'Value': [12, 22, 32, 42]
}
df_L = pd.DataFrame(data)

# Add a new 'Trial' column using apply() and f-string formatting
df_L['Trial'] = df_L.apply(lambda row: f'T-{row.name + 1}', axis=1)
print(df_L)

df_L['combine'] = df_L['leg'] + " " + df_L['Trial']

# Select rows for a specific date (e.g., '2023-07-15')
selected_date = '2023-07-15'
selected_rows_L = df_L[df_L['Date'] == selected_date]

selected_rows = pd.concat([selected_rows_R, selected_rows_L])

# Sort values by the 'Category' column
selected_rows = selected_rows.sort_values(by='Trial')

print(selected_rows)

#############################
# Create the bar chart
plt.bar(selected_rows['combine'], selected_rows['Value'])

# Set chart title and axis labels
plt.title(f'Values for {selected_date}')
plt.xlabel('combine')
plt.ylabel('Value')

# Show the chart
plt.show()
