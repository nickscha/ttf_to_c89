# ttf_to_c89
A small python utility that converts a given ttf font file into a single row font atlas BMP and C89 header file.

## Quick Start

Install pillow package if not available and run the python file.

```sh
pip install pillow

python ttf_to_c89.py
```

Afterwards a font_atlas.bmp single row bitmap and a C89 compatible font.h file are generated.

A "Consolas" rendered font bitmap would look like this:

<p align="center">
<a href="https://nickscha.github.io/"><img src="example.png"></a>
</p>

## Customization

Modify the "generate_ascii_bitmap" call in the file and adjust the parameters as needed.

For a higher/smoother resolution try adjusting the pixel_height parameter since it can vary based on the ttf font.

Works best with monospaced fonts.

```python
if __name__ == "__main__":
    
    ttf_to_bmp_c89(
        font_path    = "C:\\Windows\\Fonts\\consola.ttf", 
        pixel_height = 32,
        bmp_output   = "font_atlas.bmp", 
        c_output     = "font_data.h"
    )
```
