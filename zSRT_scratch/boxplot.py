import pandas as pd
import matplotlib.pyplot as plt

# Sample DataFrame
data = {
    'Date': ['2023-07-15', '2023-07-15', '2023-07-15', '2023-07-15', '2023-07-15', '2023-07-15', '2023-07-16', '2023-07-16'],
    'Category': ['left', 'left', 'left', 'right', 'right', 'right', 'right', 'right'],
    'Value': [10, 15, 12, 8, 30, 35, 32, 28]
}

df = pd.DataFrame(data)

# Select rows for a specific date (e.g., '2023-07-15')
selected_date = '2023-07-15'
df = df[df['Date'] == selected_date].copy()
print (df)

# Group the DataFrame by 'Category' and 'Date' and collect 'Value' as a list for each group
grouped_df = df.groupby('Category')['Value'].apply(list)

print('grouped df')
print (grouped_df)

# Plot the box plot using matplotlib
plt.figure(figsize=(8, 6))
plt.boxplot(grouped_df, labels=grouped_df.keys())
plt.title('Box Plot for left and right')
plt.xlabel('Category')
plt.ylabel('Value')
plt.show()
