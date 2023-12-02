import matplotlib.pyplot as plt
import io

# Sample data for the line graph
x = [1, 2, 3, 4, 5]
y = [10, 20, 30, 25, 15]

# Create the line plot
plt.plot(x, y)
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Line Plot')

# Save the plot to memory
buffer = io.BytesIO()
plt.savefig(buffer, format='png', transparent=False, facecolor='white', dpi=300, bbox_inches="tight")
plt.close()  # Close the plot to free resources

# Now, you can do other operations with the plot stored in 'buffer'

# For example, save the plot to disk
with open('graph.png', 'wb') as f:
    f.write(buffer.getvalue())

# Or display the plot using an image viewer
from PIL import Image
image = Image.open(buffer)
image.show()
