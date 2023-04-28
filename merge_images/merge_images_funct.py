import cv2
import numpy as np
from PIL import Image


def find_longest_line(image):
    image = image.convert("RGB")

    # Convert the image to grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    # Apply Canny edge detection with lower and upper thresholds of 50 and 150
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Apply Hough Line Transform
    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180, threshold=50, minLineLength=100, maxLineGap=10
    )

    # Check if any lines were detected
    if lines is not None:
        # Find the longest line
        longest_line = None
        max_length = 0
        for line in lines:
            x1, y1, x2, y2 = line[0]
            length = abs(x2 - x1)
            if length > max_length:
                max_length = length
                longest_line = (x1, y1, x2, y2)

        # Return the coordinates of the longest line
        return longest_line[0], longest_line[1], longest_line[2], longest_line[3]

    # If no lines were detected, return None
    return None


def merge_images(image1, image2, mode="centered"):
    if mode == "aligned":
        x1 = find_longest_line(image1)
        x2 = find_longest_line(image2)
        shift = x1[0] - x2[0]
    else:
        shift = 0

    max_width = max(image1.width, image2.width + shift)
    total_height = image1.height + image2.height

    composite_image = Image.new(
        "RGBA", (int(max_width), total_height), (255, 255, 255, 255)
    )

    composite_image.paste(image1, (0, 0))

    if mode == "aligned":
        composite_image.paste(image2, (int(shift), image1.height))
    else:
        composite_image.paste(image2, ((max_width - image2.width) // 2, image1.height))
    composite_image.show()
    return composite_image


def draw_detected_line(image, line_rho, line_length, color=(255, 0, 0), thickness=2):
    a = np.cos(np.pi / 2)
    b = np.sin(np.pi / 2)
    x0 = a * line_rho
    y0 = b * line_rho
    x1 = int(x0 + line_length * (-b))
    y1 = int(y0 + line_length * a)
    x2 = int(x0 - line_length * (-b))
    y2 = int(y0 - line_length * a)

    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    cv2.line(cv_image, (x1, y1), (x2, y2), color, thickness)

    return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
