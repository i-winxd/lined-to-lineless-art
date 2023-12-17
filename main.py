from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import List, Tuple
from PIL import Image
import os

import tkinter as tk
from tkinter import filedialog
from functools import partial
from typing import Callable


class FileProcessorApp:
    fn: Callable[[str, str], None]
    a1: str
    a2: str

    def __init__(self, master: tk.Tk, fn: Callable[[str, str], None], a1: str, a2: str) -> None:
        self.a1 = a1
        self.a2 = a2
        self.fn = fn
        self.master = master
        self.master.title("File Processor App")

        self.file1_label = tk.Label(master, text=f"File 1 ({self.a1}):")
        self.file1_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.E)

        self.file1_entry = tk.Entry(master, state='readonly', width=40)
        self.file1_entry.grid(row=0, column=1, padx=10, pady=10)

        self.browse_file1_button = tk.Button(master, text="Browse", command=self.browse_file1)
        self.browse_file1_button.grid(row=0, column=2, padx=10, pady=10)

        self.file2_label = tk.Label(master, text=f"File 2 ({self.a2}):")
        self.file2_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)

        self.file2_entry = tk.Entry(master, state='readonly', width=40)
        self.file2_entry.grid(row=1, column=1, padx=10, pady=10)

        self.browse_file2_button = tk.Button(master, text="Browse", command=self.browse_file2)
        self.browse_file2_button.grid(row=1, column=2, padx=10, pady=10)

        self.run_button = tk.Button(master, text="Run", command=self.run_function)
        self.run_button.grid(row=2, column=1, pady=20)

    def browse_file1(self) -> None:
        initial_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = filedialog.askopenfilename(title=f"Open {self.a1}", initialdir=initial_dir,
                                               filetypes=[("PNG files", "*.png")])
        self.file1_entry.config(state='normal')
        self.file1_entry.delete(0, tk.END)
        self.file1_entry.insert(0, file_path)
        self.file1_entry.config(state='readonly')

    def browse_file2(self) -> None:
        initial_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = filedialog.askopenfilename(title=f"Open {self.a2}", initialdir=initial_dir,
                                               filetypes=[("PNG files", "*.png")])
        self.file2_entry.config(state='normal')
        self.file2_entry.delete(0, tk.END)
        self.file2_entry.insert(0, file_path)
        self.file2_entry.config(state='readonly')

    def run_function(self) -> None:
        file1_path = self.file1_entry.get()
        file2_path = self.file2_entry.get()

        if file1_path and file2_path:
            print("Executing run function with files:", file1_path, file2_path)
            self.fn(file1_path, file2_path)
            print("Run function successfully executed with files:", file1_path, file2_path)
        else:
            print("Please select both files before running the function.")


def get_unique_file_name(file_name: str) -> str:
    base_name, extension = os.path.splitext(file_name)
    counter = 1

    while os.path.exists(file_name):
        file_name = f"{base_name}_{counter}{extension}"
        counter += 1

    return file_name


def layer_images(background: Image.Image, overlay: Image.Image, position: tuple) -> Image.Image:
    """
    Layer one image over another image at the specified position.

    Args:
        background (Image.Image): The background image.
        overlay (Image.Image): The image to be layered over the background.
        position (tuple): The position (x, y) where the overlay should be pasted.

    Returns:
        Image.Image: The resulting image with the overlay layered over the background.
    """
    merged_image = background.copy()
    merged_image.paste(overlay, position, overlay)
    return merged_image


def open_image(file_path: str) -> Image.Image:
    """
    Open an image from a file path and convert it to RGBA mode.

    Args:
        file_path (str): The path to the image file.

    Returns:
        Image.Image: The opened image in RGBA mode.
    """
    image = Image.open(file_path)
    image = image.convert("RGBA")
    return image


def check_2d_lists_same_dimensions(list1: List[List], list2: List[List]) -> bool:
    """
    Check if two 2D lists have the same width and height everywhere.

    Args:
        list1 (List[List]): The first 2D list.
        list2 (List[List]): The second 2D list.

    Returns:
        bool: True if the lists have the same width and height everywhere, False otherwise.
    """
    if len(list1) != len(list2):
        return False

    for row1, row2 in zip(list1, list2):
        if len(row1) != len(row2):
            return False

    return True


@dataclass
class Pixel:
    r: int
    g: int
    b: int
    a: int

    def inherit_color(self, other: Pixel) -> None:
        """This pixel takes the r, g, b values of other and replaces its
        existing r, g, b with them. a remains unaltered."""
        self.r = other.r
        self.g = other.g
        self.b = other.b


def find_nearest(list_2d: List[List[Pixel]], coordinate: Tuple[int, int], predicate: Callable[[Pixel], bool]) -> Tuple[
    int, int]:
    """
    Finds the nearest index pair near the given coordinate that satisfies the predicate, using BFS.
    list_2d must have the same width and height.

    Args:
        list_2d (List[List[T]]): The 2D list to search.
        coordinate (Tuple[int, int]): The starting coordinate for the BFS search.
        predicate (Callable[[T], bool]): The predicate function to check for satisfaction.

    Returns:
        Tuple[int, int]: The nearest index pair that satisfies the predicate.
    """
    rows, cols = len(list_2d), len(list_2d[0])
    visited = set()
    queue = deque([(coordinate[0], coordinate[1])])

    while queue:
        row, col = queue.popleft()
        if 0 <= row < rows and 0 <= col < cols and (row, col) not in visited:
            visited.add((row, col))
            if predicate(list_2d[row][col]):
                return row, col

            neighbors = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
            queue.extend(neighbor for neighbor in neighbors if neighbor not in visited)

    return -1, -1


def image_to_pixel_list(image: Image.Image) -> List[List[Pixel]]:
    pixel_list: List[List[Pixel]] = []
    width, height = image.size
    for y in range(height):
        row: List[Pixel] = []
        for x in range(width):
            r, g, b, a = image.getpixel((x, y))
            pixel = Pixel(r=r, g=g, b=b, a=a)
            row.append(pixel)
        pixel_list.append(row)
    return pixel_list


def pixel_list_to_image(pixel_list: List[List[Pixel]]) -> Image.Image:
    height = len(pixel_list)
    width = len(pixel_list[0])

    new_image = Image.new('RGBA', (width, height))
    for y in range(height):
        for x in range(width):
            pixel = pixel_list[y][x]
            rgba = (pixel.r, pixel.g, pixel.b, pixel.a)
            new_image.putpixel((x, y), rgba)

    return new_image


def alpha_gte(pixel: Pixel, alpha: int) -> bool:
    return pixel.a >= alpha


class ImageCombiner:
    alpha_threshold: int

    _stroke_pixel_list: list[list[Pixel]]
    _color_pixel_list: list[list[Pixel]]

    # def get_stroke_as_image(self) -> Image.Image:
    #     return pixel_list_to_image(self._stroke_pixel_list)

    def get_stroke_color_as_image(self) -> tuple[Image.Image, Image.Image]:
        stroke_image = pixel_list_to_image(self._stroke_pixel_list)
        color_image = pixel_list_to_image(self._color_pixel_list)
        background = Image.new('RGB', color_image.size, "#2c4464")
        background.paste(stroke_image, mask=stroke_image.split()[3])
        background.paste(color_image, mask=color_image.split()[3])
        return stroke_image, background

    def __init__(self, stroke_layer: Image.Image, color_layer: Image.Image, alpha_threshold: int = 35) -> None:
        self._stroke_pixel_list = image_to_pixel_list(stroke_layer)
        self._color_pixel_list = image_to_pixel_list(color_layer)
        if not check_2d_lists_same_dimensions(self._stroke_pixel_list, self._color_pixel_list):
            raise ValueError("Input images not the same dimensions")
        self.alpha_threshold = alpha_threshold

    def replace_stroke_pixels(self) -> None:
        """Color all non-transparent pixels in self._stroke_pixel_list with the
        nearest corresponding pixel in self._color_pixel_list"""
        partial_alpha_gte = partial(alpha_gte, alpha=self.alpha_threshold)
        for i, row in enumerate(self._stroke_pixel_list):
            for j, pixel in enumerate(row):
                # coords: (i, j)
                if partial_alpha_gte(pixel):  # branch in if stroke pixel isn't transparent
                    nearest_i, nearest_j = find_nearest(self._color_pixel_list, (i, j), partial_alpha_gte)
                    if nearest_i == -1 or nearest_j == -1:
                        continue  # color pixel list happens to be transparent everywhere
                    # there is a found pixel
                    corresponding_pixel = self._color_pixel_list[nearest_i][nearest_j]
                    pixel.inherit_color(corresponding_pixel)
                pixel.a = 0 if pixel.a < 100 else 255
                # pixel.a = pixel.a if pixel.a < 10 else 255


def replace_stroke_pixel(i: int, row: List[Pixel], color_pixel_list: List[List[Pixel]], alpha_threshold: int) -> None:
    partial_alpha_gte = partial(alpha_gte, alpha=alpha_threshold)
    for j, pixel in enumerate(row):
        if partial_alpha_gte(pixel):
            nearest_i, nearest_j = find_nearest(color_pixel_list, (i, j), partial_alpha_gte)
            if nearest_i == -1 or nearest_j == -1:
                continue
            corresponding_pixel = color_pixel_list[nearest_i][nearest_j]
            pixel.inherit_color(corresponding_pixel)
        pixel.a = 0 if pixel.a < 100 else 255


def overlay_transparent_image_on_background(image: Image, background_color: str) -> Image:
    """
    Overlays a transparent image on top of a background color.

    Args:
    image: A transparent image.
    background_color: A string representing the background color in hex format.

    Returns:
    The input image overlaid on top of the background color.
    """
    background = Image.new('RGB', image.size, background_color)
    background.paste(image, mask=image.split()[3])
    return background


def make_lineless(stroke_img_path: str, color_img_path: str) -> None:
    stroke_image = open_image(stroke_img_path)
    color_image = open_image(color_img_path)
    print("Making combiner")
    image_combiner = ImageCombiner(stroke_image, color_image, 35)
    print("Replacing stroke pixels")
    image_combiner.replace_stroke_pixels()
    print("Getting stroke color as image")
    final_stroke_as_image, final_color_as_image = image_combiner.get_stroke_color_as_image()
    # final_color_as_image = image_combiner.get_color_as_image()
    # final_stroke_as_image = image_combiner.get_stroke_as_image()

    final_color_as_image.save(get_unique_file_name("exportFC.png"), format="PNG")
    final_stroke_as_image.save(get_unique_file_name("exportST.png"), format="PNG")

    layered = layer_images(final_color_as_image, final_stroke_as_image, (0, 0))
    layered.save("export.png", format="PNG")


if __name__ == '__main__':
    root = tk.Tk()
    app = FileProcessorApp(root, make_lineless, "STROKE", "COLOR")
    root.mainloop()
