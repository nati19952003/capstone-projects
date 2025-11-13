import cv2
import numpy as np
import os

# Create a white image
height, width = 400, 600
image = np.ones((height, width), dtype=np.uint8) * 255

# Draw table grid lines
cv2.line(image, (100, 50), (500, 50), 0, 2)  # Top horizontal
cv2.line(image, (100, 100), (500, 100), 0, 2)  # Header separator
cv2.line(image, (100, 150), (500, 150), 0, 2)  # Row 1
cv2.line(image, (100, 200), (500, 200), 0, 2)  # Row 2
cv2.line(image, (100, 250), (500, 250), 0, 2)  # Bottom

cv2.line(image, (100, 50), (100, 250), 0, 2)   # Left vertical
cv2.line(image, (300, 50), (300, 250), 0, 2)   # Middle vertical
cv2.line(image, (500, 50), (500, 250), 0, 2)   # Right vertical

# Add some text
font = cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(image, "Name", (150, 85), font, 0.7, 0, 2)
cv2.putText(image, "Value", (350, 85), font, 0.7, 0, 2)
cv2.putText(image, "Item 1", (150, 135), font, 0.7, 0, 2)
cv2.putText(image, "10.5", (350, 135), font, 0.7, 0, 2)
cv2.putText(image, "Item 2", (150, 185), font, 0.7, 0, 2)
cv2.putText(image, "20.0", (350, 185), font, 0.7, 0, 2)
cv2.putText(image, "Item 3", (150, 235), font, 0.7, 0, 2)
cv2.putText(image, "15.7", (350, 235), font, 0.7, 0, 2)

# Save the image
os.makedirs("data/test_data", exist_ok=True)
cv2.imwrite("data/test_data/sample_table.png", image)
print("Created test image: data/test_data/sample_table.png")