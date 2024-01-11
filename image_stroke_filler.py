from __future__ import annotations

from collections import deque
import time
from typing import Any, List, Tuple, TypedDict
from PIL import Image
import os

import tkinter as tk
from functools import partial
from typing import Callable


PIXEL_SEARCH_LIMIT = 8000

def get_unique_file_name(file_name: str) -> str:
    base_name, extension = os.path.splitext(file_name)
    counter = 1

    while os.path.exists(file_name):
        file_name = f"{base_name}_{counter}{extension}"
        counter += 1

    return file_name


def layer_images(background: Image.Image, overlay: Image.Image, position: tuple[int, int]) -> Image.Image:
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


class IPixel(TypedDict):
    r: int
    g: int
    b: int
    a: int


def inherit_color(cur: IPixel, other: IPixel) -> None:
    """This pixel takes the r, g, b values of other and replaces its
        existing r, g, b with them. a remains unaltered."""
    cur["r"] = other["r"]
    cur["g"] = other["g"]
    cur["b"] = other["b"]


def init_pixel(r: int, g: int, b: int, a: int) -> IPixel:
    return {"r": r, "g": g, "b": b, "a": a,}



def find_nearest(list_2d: List[List[IPixel]], coordinate: Tuple[int, int], predicate: Callable[[IPixel], bool], limit: int) -> Tuple[
    int, int]:
    """
    Finds the nearest index pair near the given coordinate that satisfies the predicate, using BFS.
    list_2d must have the same width and height.

    Args:
        list_2d (List[List[T]]): The 2D list to search.
        coordinate (Tuple[int, int]): The starting coordinate for the BFS search.
        predicate (Callable[[T], bool]): The predicate function to check for satisfaction.
        limit (int): How many times BFS can run.

    Returns:
        Tuple[int, int]: The nearest index pair that satisfies the predicate.
    """
    rows, cols = len(list_2d), len(list_2d[0])
    visited = set()
    queue = deque([(coordinate[0], coordinate[1])])
    i = 0
    while queue and i <= limit:
        row, col = queue.popleft()
        if 0 <= row < rows and 0 <= col < cols and (row, col) not in visited:
            visited.add((row, col))
            if predicate(list_2d[row][col]):
                return row, col

            neighbors = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
            queue.extend(neighbor for neighbor in neighbors if neighbor not in visited)
        i += 1

    return -1, -1


def image_to_pixel_list(image: Image.Image) -> List[List[IPixel]]:
    pixel_list: List[List[IPixel]] = []
    width, height = image.size
    for y in range(height):
        row: List[IPixel] = []
        for x in range(width):
            r, g, b, a = image.getpixel((x, y))
            pixel = init_pixel(r=r, g=g, b=b, a=a)
            row.append(pixel)
        pixel_list.append(row)
    return pixel_list


def pixel_list_to_image(pixel_list: List[List[IPixel]]) -> Image.Image:
    height = len(pixel_list)
    width = len(pixel_list[0])

    new_image = Image.new('RGBA', (width, height))
    for y in range(height):
        for x in range(width):
            pixel = pixel_list[y][x]
            rgba = (pixel["r"], pixel["g"], pixel["b"], pixel["a"])
            new_image.putpixel((x, y), rgba)

    return new_image


def alpha_gte(pixel: IPixel, alpha: int) -> bool:
    return pixel["a"] >= alpha


class ImageCombiner:
    alpha_threshold: int

    _stroke_pixel_list: list[list[IPixel]]
    _color_pixel_list: list[list[IPixel]]

    # def get_stroke_as_image(self) -> Image.Image:
    #     return pixel_list_to_image(self._stroke_pixel_list)

    def get_stroke_color_as_image(self) -> tuple[Image.Image, Image.Image]:
        """RUNTIME: O(n^2 * UPPER_LIMIT)"""
        stroke_image = pixel_list_to_image(self._stroke_pixel_list)
        color_image = pixel_list_to_image(self._color_pixel_list)
        background = Image.new('RGBA', color_image.size, (0, 0, 0, 0))
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
        nearest corresponding pixel in self._color_pixel_list
        Time complexity: O(n^2 ) worst case; parallelize this one
        """
        print("")
        partial_alpha_gte = partial(alpha_gte, alpha=self.alpha_threshold)
        for i, row in enumerate(self._stroke_pixel_list):
            print(f"\rReplacing row {i}/{len(self._stroke_pixel_list)}", end="")
            for j, pixel in enumerate(row):
                # coords: (i, j)
                if partial_alpha_gte(pixel):  # branch in if stroke pixel isn't transparent
                    nearest_i, nearest_j = find_nearest(self._color_pixel_list, (i, j), partial_alpha_gte, PIXEL_SEARCH_LIMIT)
                    if nearest_i == -1 or nearest_j == -1:
                        continue  # color pixel list happens to be transparent everywhere
                    # there is a found pixel
                    corresponding_pixel = self._color_pixel_list[nearest_i][nearest_j]
                    inherit_color(pixel, corresponding_pixel)
                    # pixel.inherit_color(corresponding_pixel)
                pixel["a"] = 0 if pixel["a"] < 100 else 255
                # pixel.a = pixel.a if pixel.a < 10 else 255
        print("")



def overlay_transparent_image_on_background(image: Image.Image, background_color: str) -> Image.Image:
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


def make_lineless(path_to_stroke: str, path_to_color: str) -> Any:
    """Making lineless art variant"""
    print("This may take a minute.")
    now = time.perf_counter()
    stroke_image = open_image(path_to_stroke)
    color_image = open_image(path_to_color)
    print("Making combiner")
    image_combiner = ImageCombiner(stroke_image, color_image, 35)
    
    # TIMER UPDATE
    now_tmp = now
    now = time.perf_counter()
    print(f"This took {now - now_tmp} seconds")

    print("Replacing stroke pixels")
    image_combiner.replace_stroke_pixels()
    
        # TIMER UPDATE
    now_tmp = now
    now = time.perf_counter()
    print(f"This took {now - now_tmp} seconds")

    print("Getting stroke color as image")
    final_stroke_as_image, final_color_as_image = image_combiner.get_stroke_color_as_image()
    # final_color_as_image = image_combiner.get_color_as_image()
    # final_stroke_as_image = image_combiner.get_stroke_as_image()

        # TIMER UPDATE
    now_tmp = now
    now = time.perf_counter()
    print(f"This took {now - now_tmp} seconds")
    export_folder = "export"
    final_color_as_image.save(get_unique_file_name(os.path.join(export_folder ,"exportFC.png")), format="PNG")
    final_stroke_as_image.save(get_unique_file_name(os.path.join(export_folder, "exportST.png")), format="PNG")

    layered = layer_images(final_color_as_image, final_stroke_as_image, (0, 0))
    layered.save(get_unique_file_name(os.path.join("export.png")), format="PNG")



