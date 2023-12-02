import seaborn as sns
import matplotlib.pyplot as plt

palettes = ['Blues', 'Greys', 'rocket', 'icefire', 'rainbow', 'seismic']

for palette in palettes:

    # Get the color palette
    colors = sns.color_palette(palette, 10)

    # Create a bar plot to display the colors
    fig, ax = plt.subplots(figsize=(6, 1))
    for i, color in enumerate(colors):
        ax.fill_betweenx(y=[0, 1], x1=i, x2=i + 1, color=color)

    # Set the x and y limits, remove yticks and labels, and set xticks to the middle of each bar
    ax.set_xlim(0, len(colors))
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xticks([i + 0.5 for i in range(len(colors))])
    ax.set_xticklabels([str(i) for i in range(1, len(colors) + 1)], rotation=45, ha='right')
    print(f'number colors: {len(colors)}')
    plt.show()