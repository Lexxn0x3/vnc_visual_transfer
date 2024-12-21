import cv2
import numpy as np
import pyautogui
import time
from datetime import datetime
import hashlib

def setup_coordinates():
    """Set up grid coordinates with fixed defaults."""

    """
    columns = 96
    rows = 48
    top_left = (320, 154)
    top_right = (1090, 154)
    bottom_left = (320, 922)
    """
    columns = 160
    rows = 49
    top_left = (320, 154)
    top_right = (1603, 154)
    bottom_left = (320, 938)
    # Calculate block width and height
    block_width = (top_right[0] - top_left[0]) / columns
    block_height = (bottom_left[1] - top_left[1]) / rows

    # Calculate the region to capture
    region = (
        top_left[0],  # x-coordinate of the top-left corner
        top_left[1],  # y-coordinate of the top-left corner
        top_right[0] - top_left[0],  # width of the grid
        bottom_left[1] - top_left[1],  # height of the grid
    )

    print(f"Top-left corner: {top_left}")
    print(f"Top-right corner: {top_right}")
    print(f"Bottom-left corner: {bottom_left}")
    print(f"Block size: {block_width:.2f}x{block_height:.2f}")
    print(f"Capture region: {region}")

    return top_left, block_width, block_height, region, columns, rows

def calculate_block_centers(top_left, block_width, block_height, columns, rows):
    """Calculate the centers of all blocks in a grid layout."""
    centers = []
    for row in range(rows):
        row_centers = []
        for col in range(columns):
            center_x = top_left[0] + (col + 0.5) * block_width
            center_y = top_left[1] + (row + 0.5) * block_height
            row_centers.append((int(center_x), int(center_y)))
        centers.append(row_centers)
    return centers

def save_debug_screenshot(img, centers, region, decoded_bits, step):
    """Save the screenshot with markers for debugging."""
    # Convert to color image to draw markers
    img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # Draw markers at the center of each block
    for row_index, row_centers in enumerate(centers):
        for col_index, (x, y) in enumerate(row_centers):
            # Convert to relative coordinates within the captured region
            x -= region[0]
            y -= region[1]
            # Determine color based on the decoded bit
            if decoded_bits[row_index][col_index] == "2":
                color = (128, 128, 128)  # Gray for padding
            else:
                color = (0, 255, 0) if decoded_bits[row_index][col_index] == "1" else (0, 0, 255)  # Green for 1, Red for 0
            # Draw a 3x3 dot at the center
            cv2.rectangle(img_color, (x - 1, y - 1), (x + 1, y + 1), color, -1)

    # Save the image with a unique filename
    filename = f"debug_screenshot_{step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    cv2.imwrite(filename, img_color)
    print(f"Saved screenshot for debugging: {filename}")

    # Print decoded bits for this frame
    print(f"Decoded bits: {decoded_bits}")

def calculate_checksum(bits):
    """Calculate a SHA-256 checksum for a given binary string."""
    # Convert bits to bytes
    byte_data = int(bits, 2).to_bytes(len(bits) // 8, byteorder="big")
    # Calculate SHA-256 checksum
    checksum = hashlib.sha256(byte_data).digest()
    # Convert checksum to binary string
    checksum_bits = ''.join(f"{byte:08b}" for byte in checksum)
    return checksum_bits


def decode_visual_from_image(output_file_path, centers, region):
    """Decode binary data from grid visualization."""
    step = 0  # To differentiate each frame for debugging
    gray_detected = False  # Flag to detect gray blocks

    while not gray_detected:
        # Capture only the specified region
        screenshot = pyautogui.screenshot(region=region)
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

        decoded_bits = []
        frame_has_gray = False  # Track if the frame contains gray blocks

        for row_centers in centers:
            row_bits = []
            for x, y in row_centers:
                # Convert to relative coordinates within the captured region
                x -= region[0]
                y -= region[1]

                # Check the brightness of the center pixel
                pixel_value = img[y, x]

                # Detect gray blocks (padding) based on specific brightness threshold
                if 80 <= pixel_value < 90:  # Assuming gray falls in this range
                    frame_has_gray = True
                    row_bits.append("2")  # Mark as gray
                else:
                    row_bits.append("0" if pixel_value < 128 else "1")

            decoded_bits.append(row_bits)

        # Flatten decoded bits to a single binary string
        flattened_bits = "".join("".join(row) for row in decoded_bits)

        # Separate data bits and checksum bits
        data_bits = flattened_bits[:-256].replace("2", "")  # Remove gray bits before checksum
        checksum_bits = flattened_bits[-256:]

        #save_debug_screenshot(img, centers, region, decoded_bits, step)

        # Calculate the checksum for the valid data bits
        try:
            calculated_checksum = hashlib.sha256(
                int(data_bits, 2).to_bytes(len(data_bits) // 8, byteorder="big")
            ).hexdigest()

            # Convert the extracted checksum bits to hex
            extracted_checksum = hex(int(checksum_bits, 2))[2:].zfill(64)

            # Validate checksum
            if calculated_checksum == extracted_checksum:
                print("Checksum validation successful.")

                # Write only valid data bits to the output file
                data_bytes = [int(data_bits[i:i + 8], 2) for i in range(0, len(data_bits), 8)]
                with open(output_file_path, "ab") as output_file:
                    output_file.write(bytearray(data_bytes))

                # Simulate Enter press for Program 1 to display the next frame
                if not frame_has_gray:
                    pyautogui.press("enter")

            else:
                print("Checksum validation failed. Retrying frame...")

        except ValueError:
            print("Invalid data or checksum format. Skipping frame.")

        # Stop processing if gray blocks are detected
        if frame_has_gray:
            print("Gray blocks detected. Processing valid data and stopping further frames.")
            gray_detected = True

        time.sleep(0.1)  # Small delay to sync



if __name__ == "__main__":
    # Use the fixed setup
    top_left, block_width, block_height, region, columns, rows = setup_coordinates()

    # Calculate block centers
    centers = calculate_block_centers(top_left, block_width, block_height, columns, rows)

    # Specify the output file
    output_file_path = "archive.zip"

    # Start decoding
    time.sleep(5)
    decode_visual_from_image(output_file_path, centers, region)
