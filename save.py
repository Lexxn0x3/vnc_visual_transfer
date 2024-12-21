import os
import hashlib

def calculate_checksum(bits):
    """Calculate a SHA-256 checksum for a given binary string."""
    # Convert bits to bytes
    byte_data = int(bits, 2).to_bytes(len(bits) // 8, byteorder="big")
    # Calculate SHA-256 checksum
    checksum = hashlib.sha256(byte_data).digest()
    # Convert checksum to binary string
    checksum_bits = ''.join(f"{byte:08b}" for byte in checksum)
    return checksum_bits

def colored_block(bit):
    """Return a block character with the appropriate color."""
    if bit == "1":
        return "\033[97m\u2588\033[0m"  # White block for 1
    elif bit == "0":
        return "\033[30m\u2588\033[0m"  # Black block for 0
    else:
        return "\033[90m\u2588\033[0m"  # Gray block for padding (end of file)

def binary_visualizer(file_path, x=16, y=8):
    with open(file_path, "rb") as binary_file:
        data = binary_file.read()

    total_bits = len(data) * 8
    frame_data_bits = x * y - 256  # Exclude 256 bits for the checksum
    total_frames = (total_bits + frame_data_bits - 1) // frame_data_bits  # Calculate total frames
    bit_index = 0
    current_frame = 0

    while bit_index < total_bits:
        current_frame += 1
        # Extract the frame's binary content
        frame_bits = ""
        for _ in range(frame_data_bits):
            if bit_index < total_bits:
                byte_index = bit_index // 8
                bit_offset = 7 - (bit_index % 8)  # MSB-first bit order
                # Extract the bit (1 or 0)
                bit = (data[byte_index] >> bit_offset) & 1
                frame_bits += str(bit)
                bit_index += 1
            else:
                frame_bits += "2"  # Pad with '2' to indicate end of file

        # Trim padding before calculating checksum
        valid_frame_bits = frame_bits.replace("2", "")
        checksum_bits = calculate_checksum(valid_frame_bits)
        full_frame_bits = frame_bits + checksum_bits

        # Generate the grid for the full frame (data + checksum)
        grid = []
        bit_pointer = 0
        for _ in range(y):
            line = ""
            for _ in range(x):
                if bit_pointer < len(full_frame_bits):
                    bit = full_frame_bits[bit_pointer]
                    line += colored_block(bit)
                    bit_pointer += 1
                else:
                    line += " "  # Fill remaining grid with spaces
            grid.append(line)

        # Clear screen and display grid
        os.system('clear')
        progress = (current_frame / total_frames) * 100
        print("\n".join(grid))
        print(f"Frame {current_frame}/{total_frames} ({progress:.2f}%)")
        input("Press Enter for next frame...")  # Wait for user input

# Example usage
binary_visualizer("save.zip", x=16, y=8)
