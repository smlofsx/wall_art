from palette import show_palette_nonblocking

if __name__ == "__main__":
    input_colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (128, 128, 128)
    ]
    show_palette_nonblocking(input_colors)