# MIT License
# 
# Copyright (c) 2025 Nickscha
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("This script requires the Pillow library. Install it using:")
    print("    pip install pillow")
    exit(1)

def ttf_to_bmp_c89(font_path, pixel_height=32, bmp_output="font_atlas.bmp", c_output="font_data.h", flip_y=False):
    ascii_chars = [chr(i) for i in range(32, 127)]
    num_chars   = len(ascii_chars)

    # Load font with possible different style (adjust pixel_height to suit)
    try:
        font = ImageFont.truetype(font_path, pixel_height)
    except IOError:
        print(f"Error: Could not load font at {font_path}")
        return

    # Determine max bounding box
    max_width    = 0
    max_height   = 0
    min_offset_x = 0
    min_offset_y = 0

    for ch in ascii_chars:
        bbox = font.getbbox(ch, anchor="lt")  # returns (x0, y0, x1, y1)
        x0, y0, x1, y1 = bbox
        w = x1 - x0
        h = y1 - y0
        max_width    = max(max_width, w)
        max_height   = max(max_height, h)
        min_offset_x = min(min_offset_x, x0)
        min_offset_y = min(min_offset_y, y0)

    char_width   = max_width
    char_height  = max_height
    atlas_width  = char_width * num_chars
    atlas_height = char_height

    # Create image
    image = Image.new("RGBA", (atlas_width, atlas_height), (0, 0, 0, 0))
    draw  = ImageDraw.Draw(image)

    # Draw each character at fixed spacing
    for i, ch in enumerate(ascii_chars):
        x = i * char_width
        draw.text((x - min_offset_x, -min_offset_y), ch, font=font, fill=(255, 255, 255, 255))

    # Convert the image to grayscale and then to binary (black and white)
    image     = image.convert("L")                                 # Convert to grayscale
    threshold = 128                                                # Threshold to decide what is black or white (can be adjusted)
    image     = image.point(lambda p: 255 if p > threshold else 0) # Apply threshold to make it binary (white and black)
    image     = image.convert("1", dither=Image.NONE)              # Convert to binary image with 1-bit pixels

    # Get the pixel data manually (by accessing pixel values)
    pixel_data = []
    pixels = image.load()
    for y in range(atlas_height):
        row = []
        for x in range(atlas_width):
            pixel = pixels[x, y]
            row.append(1 if pixel == 255 else 0)
        pixel_data.append(row)


    # Flip Y axis if requested
    if flip_y:
        pixel_data = pixel_data[::-1]

    # Convert the pixel data into a C89 array format
    c_array = []
    for row in pixel_data:
        # Convert each row into a list of bytes where each byte represents 8 pixels
        row_bytes = []
        for i in range(0, len(row), 8):
            byte = 0
            for j in range(8):
                if i + j < len(row) and row[i + j] == 1:
                    byte |= (1 << (7 - j))  # Set the bit
            row_bytes.append(byte)
        c_array.append(row_bytes)

    # Write the C89-compliant static array to a C file without stdlib
    with open(c_output, "w") as f:

        f.write(f"/* Font path used : {font_path} */\n")
        f.write(f"/* Font atlas size: {atlas_width}x{atlas_height} */\n")
        f.write(f"/* Each glyph size: {char_width}x{char_height}   */\n")
        f.write(f"/* Y-axis flipped : {'yes' if flip_y else 'no '} */\n")
        f.write("\n")
        f.write(f"#ifndef FONT_H\n")
        f.write(f"#define FONT_H\n")
        f.write("\n")
        f.write(f"static unsigned int font_atlas_width        = {atlas_width};\n")
        f.write(f"static unsigned int font_atlas_height       = {atlas_height};\n")
        f.write(f"static unsigned int font_atlas_glyph_width  = {char_width};\n")
        f.write(f"static unsigned int font_atlas_glyph_height = {char_height};\n")
        f.write("\n")
        f.write("static unsigned char font_atlas_data[]      = {\n")

        # Format the C array for output
        for i, row_bytes in enumerate(c_array):
            f.write("    ")
            f.write(", ".join(f"0x{byte:02X}" for byte in row_bytes))
            if i < len(c_array) - 1:
                f.write(",")
            f.write("\n")

        f.write("};\n")
        f.write("\n")
        f.write("#endif /* FONT_H */\n")
        f.write("\n")

    # Save BMP image
    image.save(bmp_output)

    print("Saved BMP:", bmp_output)
    print("C89 static array saved to:", c_output)
    print("Each glyph: {}x{}".format(char_width, char_height))
    print("Total atlas: {}x{}".format(atlas_width, atlas_height))

if __name__ == "__main__":
    
    ttf_to_bmp_c89(
        font_path    = "C:\\Windows\\Fonts\\consola.ttf",  # Path to TTF Font file
        pixel_height = 32,                                 # Pixel height for each glyph
        bmp_output   = "font_atlas.bmp",                   # Bitmap output file
        c_output     = "font_data.h",                      # C89 single header output file
        flip_y       = True                                # If true Y axis is inverted for OpenGl/Vulkan compatibility
    )
