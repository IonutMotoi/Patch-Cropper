import argparse
import os

import cv2
import numpy as np


WINDOW_NAME = "Patch Cropper"


def is_overlapping(square1, square2):
    """
    Checks if two squares overlap.

    Args:
        square1: A tuple with two points ((x1, y1), (x2, y2)) representing the top-left and bottom-right corners of the first square.
        square2: A tuple with two points ((x1, y1), (x2, y2)) representing the top-left and bottom-right corners of the second square.

    Returns:
        A boolean indicating whether the two squares overlap.
    """
    # If one square is to the right of the other or above the other, they don't overlap
    if square1[1][0] < square2[0][0] or square1[0][0] > square2[1][0] or square1[1][1] < square2[0][1] or square1[0][1] > square2[1][1]:
        return False
    return True


def draw_squares(event, x, y, flags, param):
    """
    Handles mouse events to draw squares on an image.

    Args:
        event: The type of mouse event.
        x: The x-coordinate of the mouse event.
        y: The y-coordinate of the mouse event.
        flags: Any relevant flags for the mouse event.
        param: A list containing the image, patch size, squares, and preview square.

    This function updates the image based on mouse events. On mouse move, it updates the preview square.
    On left button down, it adds the square to the list of squares if it doesn't overlap with existing squares.
    On middle button down, it removes the square that contains the point.
    """
    # Get the image, patch size, squares, and preview square from param
    image, patch_size, squares, preview_square = param

    # Adjust the center point if it's too close to the image boundaries
    x = max(patch_size // 2, min(image.shape[1] - patch_size // 2, x))
    y = max(patch_size // 2, min(image.shape[0] - patch_size // 2, y))

    # Compute the top left and bottom right points of the square
    top_left = (x - patch_size // 2, y - patch_size // 2)
    bottom_right = (x + patch_size // 2, y + patch_size // 2)

    # If the mouse is moved, update the preview square
    if event == cv2.EVENT_MOUSEMOVE:
        preview_square[0] = top_left
        preview_square[1] = bottom_right

    # If the left mouse button was clicked, add the square to the list of squares
    elif event == cv2.EVENT_LBUTTONDOWN:
        # Check if the preview square overlaps with any of the existing squares
        for square in squares:
            if is_overlapping(preview_square, square):
                return
        squares.append((top_left, bottom_right))

    # If the right mouse button was clicked, remove the square that contains the point
    elif event == cv2.EVENT_MBUTTONDOWN:
        for square in squares:
            if square[0][0] <= x <= square[1][0] and square[0][1] <= y <= square[1][1]:
                squares.remove(square)
                return

    # Draw the preview square
    image_with_squares = image.copy()
    cv2.rectangle(image_with_squares, preview_square[0], preview_square[1], (0, 255, 0), 4)

    # Draw all the squares
    for square in squares:
        cv2.rectangle(image_with_squares, square[0], square[1], (0, 0, 255), 4)

    # Show the image with the squares
    cv2.imshow(WINDOW_NAME, image_with_squares)


def display_image(image_path, patch_size, squares, index, num_images):
    """
    Displays an image and sets up the mouse callback for drawing squares.

    Args:
        image_path: The path to the image file.
        patch_size: The size of the patch to be drawn.
        squares: A list of squares to be drawn on the image.
        index: The index of the current image in the list of images.
        num_images: The total number of images.

    This function clears the list of squares, reads the image from the image path, displays the image,
    and sets up the mouse callback for drawing squares.
    """
    print(f"Displaying image {image_path}. ({index + 1}/{num_images})")
    squares.clear()
    image = cv2.imread(image_path)
    cv2.imshow(WINDOW_NAME, image)
    cv2.setMouseCallback(WINDOW_NAME, draw_squares, param=[image, patch_size, squares, [[0, 0], [0, 0]]])


def navigate_images(images_path, output_path, patch_size):
    """
    Navigates through a directory of images, allowing the user to draw squares on them and save the squares as patches.

    Args:
        images_path: The path to the directory containing the images.
        output_path: The path to the directory where the patches will be saved.
        patch_size: The size of the patches to be drawn.

    This function sorts the image files in the directory, displays instructions for the user, and then enters a loop where it waits for user input.
    The user can navigate through the images, draw squares on them, and save the squares as patches.
    """
    # Get a sorted list of all image files in the directory
    image_files = sorted([os.path.join(images_path, f)
                         for f in os.listdir(images_path) if f.endswith('.jpg') or f.endswith('.png')])

    if not image_files:
        print("No images found in the directory.")
        return

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 900, 900)

    print("Instructions:")
    print("Press 'd' (next), 'a' (previous), 'q' (quit), 's' (save patches)")
    print("Left click (add square), middle click (remove square)\n")

    # Start at the first image
    index = 0
    squares = []
    display_image(image_files[index], patch_size, squares, index, len(image_files))

    while cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) > 0:
        key = cv2.waitKey(1000)

        if key == ord('q'):  # Quit
            break

        elif key == ord('d') and index < len(image_files) - 1:  # Next image
            index += 1
            squares = []
            display_image(image_files[index], patch_size, squares, index, len(image_files))

        elif key == ord('a') and index > 0:  # Previous image
            index -= 1
            display_image(image_files[index], patch_size, squares, index, len(image_files))

        elif key == ord('s'):  # Save the patches
            image = cv2.imread(image_files[index])
            for i, square in enumerate(squares):
                patch = image[square[0][1]:square[1][1], square[0][0]:square[1][0]]
                cv2.imwrite(os.path.join(output_path, f"{os.path.basename(image_files[index])[:-4]}_{i}.png"), patch)
            print(f"Patches saved for {os.path.basename(image_files[index])}: {len(squares)}")

    # Destroy all windows
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--images-path", type=str, help="Path to the input images")
    parser.add_argument("--output-path", type=str, default="./patches",
                        help="Path where to save the patches (default: ./patches)")
    parser.add_argument("--patch-size", type=int, default=512, help="Size of the patches (default: 512)")
    args = parser.parse_args()

    os.makedirs(args.output_path, exist_ok=True)
    if os.listdir(args.output_path):
        print("Warning: The output directory is not empty. Files may be overwritten.")

    navigate_images(args.images_path, args.output_path, args.patch_size)


if __name__ == "__main__":
    main()
