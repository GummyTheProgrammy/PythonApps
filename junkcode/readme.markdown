# Data Analytics Tools

DistinctValues.py: Interactive script in pandas that reads Superstore.csv, lists columns and shows count of distinct values of the chosen column. Dependencies: pandas. Requires Superstore.csv (present).

TotalSales.py: Calculates total Sales sum and groups sales by Category using pandas. Dependencies: pandas. Reads Superstore.csv (present).

Superstore.csv: CSV (wide) dataset used as input by DistinctValues.py and TotalSales.py. Gift.

# VideoTools

get_video_resolution.py: Scans video files in the current directory and prints resolutions using moviepy.VideoFileClip. Dependencies: moviepy. Does not depend on other scripts; needs video files present to produce output.


video_sec_calc.py: Recursively scrolls through a folder indicated by the user and adds video durations with moviepy. Dependencies: moviepy. Requires videos in the specified folder tree.

video_to_images.py: Extracts frames from videos in the current directory to the render/ folder using moviepy + Pillow and shows progress with tqdm. Dependencies: moviepy, Pillow, tqdm. It requires videos in the directory to work and generates a lot of images.

# ImageTools

Recolor.py: Image batch processor with PIL/Numpy; quantizes colors to a palette, applies effects (vertical flash, contrast, bloom, grain) and saves in processed/. Dependencies: Pillow, numpy. It expects images in a batch folder (if it doesn't exist, it creates and asks to place images) — that is, it requires image samples to run.