import rasterio
from rasterio.windows import Window
import numpy as np
from PIL import Image
import os
import glob
from tqdm import tqdm


def split_chunks(tiff_path, output_dir, x_pixels, y_pixels, prefix=""):
    """
    Splits a GeoTIFF file into smaller image chunks of specified dimensions and saves them as JPEG files.
    The chunks are named using an optional prefix and the TIFF file name.

    Parameters:
        tiff_path (str): Path to the input GeoTIFF file.
        output_dir (str): Directory where the smaller image chunks will be saved.
        x_pixels (int): Width of each chunk in pixels.
        y_pixels (int): Height of each chunk in pixels.
        prefix (str): Optional prefix to add to all chunk filenames.
    """
    # Extract the file name (without extension) to use as a prefix
    tiff_name = os.path.splitext(os.path.basename(tiff_path))[0]

    os.makedirs(output_dir, exist_ok=True)

    dataset = rasterio.open(tiff_path)

    # Calculate the number of chunks
    num_x_chunks = dataset.width // x_pixels
    num_y_chunks = dataset.height // y_pixels

    # Initialize tqdm progress bar
    total_chunks = num_x_chunks * num_y_chunks
    with tqdm(total=total_chunks, desc=f"Processing {tiff_name}", unit="chunk") as pbar:
        for i in range(num_y_chunks):
            for j in range(num_x_chunks):
                window = Window(
                    col_off=j * x_pixels,
                    row_off=i * y_pixels,
                    width=x_pixels,
                    height=y_pixels
                )

                # Read the window
                small_image = dataset.read(window=window)

                # Handle RGBA to RGB conversion if necessary
                if small_image.ndim == 3:
                    small_image = np.moveaxis(small_image, 0, -1)
                    if small_image.shape[2] == 4:
                        small_image = small_image[:, :, :3]

                # Skip all-white or all-black images
                if np.all(small_image == 255) or np.all(small_image == 0):
                    pbar.update(1)
                    continue

                # Define the filename with optional prefix and TIFF name
                if prefix:
                    chunk_name = f"{prefix}_{tiff_name}_chunk_{i}_{j}.jpg"
                else:
                    chunk_name = f"{tiff_name}_chunk_{i}_{j}.jpg"

                output_path = os.path.join(output_dir, chunk_name)

                # Save the chunk as a JPEG file
                pil_image = Image.fromarray(small_image)
                pil_image.save(output_path, format='JPEG', quality=100)

                # Update progress bar
                pbar.update(1)


def process_tiff_directory(input_dir, output_dir, x_pixels, y_pixels, prefix=""):
    """
    Processes all GeoTIFF files in a directory (including subdirectories),
    splits them into smaller chunks, and saves the output while preserving the original directory structure.

    Parameters:
        input_dir (str): Path to the root directory containing GeoTIFF files.
        output_dir (str): Path to the root output directory where split chunks will be saved.
        x_pixels (int): Width of each chunk in pixels.
        y_pixels (int): Height of each chunk in pixels.
        prefix (str): Optional prefix to add to all chunk filenames.
    """
    # Recursively find all .tif or .tiff files in the input directory
    tiff_files = glob.glob(os.path.join(input_dir, "**", "*.tif"), recursive=True)
    tiff_files.extend(glob.glob(os.path.join(input_dir, "**", "*.tiff"), recursive=True))

    if not tiff_files:
        print(f"No GeoTIFF files found in directory: {input_dir}")
        return

    # Process each GeoTIFF file
    for tiff_path in tiff_files:
        # Get the relative path to preserve directory structure
        relative_path = os.path.relpath(tiff_path, input_dir)
        relative_dir = os.path.dirname(relative_path)

        # Get the TIFF file name without extension
        tiff_name = os.path.splitext(os.path.basename(tiff_path))[0]

        # Create the corresponding output directory
        output_subdir = os.path.join(output_dir, relative_dir, tiff_name)
        os.makedirs(output_subdir, exist_ok=True)

        # Call the split_chunks function for the current TIFF file
        print(f"Processing file: {tiff_path}")
        split_chunks(tiff_path, output_subdir, x_pixels, y_pixels, prefix)

    print(f"All GeoTIFF files processed. Output saved to: {output_dir}")


def main():
    tiff_path = r"C:\Users\perez\Desktop\osirix_datasets\s3_bucket\cotton\cotton_plot_15_leaf_level_0_2.5.23_RGB\cotton_plot_15_leaf_level_0_2.5.23_RGB.tiff"
    output_dir = r"C:\Users\perez\Desktop\osirix_datasets\s3_bucket\cotton\cotton_plot_15_leaf_level_0_2.5.23_RGB\cotton_plot_15_leaf_level_0_2.5.23_RGB_chunks_5120x5120"

    os.makedirs(output_dir, exist_ok=True)
    x_pixels = 5120
    y_pixels = 5120
    prefix = "cotton_plot_15_leaf_level_0_2.5.23_RGB"  # Add your desired prefix here
    # process_tiff_directory(tiff_folder_path, output_dir, x_pixels, y_pixels, prefix)
    split_chunks(tiff_path, output_dir, x_pixels, y_pixels, prefix)


if __name__ == '__main__':
    main()
