import os
from PIL import Image, ImageDraw

# Define the directory and filename
save_dir = os.path.join('auctions_app', 'tests')
save_path = os.path.join(save_dir, 'image.jpg')

# Create a blank image (RGB) with white background
image = Image.new('RGB', (200, 200), color = (255, 255, 255))

# Initialize drawing context
draw = ImageDraw.Draw(image)

# Draw a simple rectangle and some text
draw.rectangle([(50, 50), (150, 150)], outline="blue", fill="lightblue")
draw.text((60, 90), "Auction", fill="black")

# Create directory if it doesn't exist
os.makedirs(save_dir, exist_ok=True)

# Save the image
image.save(save_path)
