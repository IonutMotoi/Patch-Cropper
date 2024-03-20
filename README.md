# Patch-Cropper
A Python tool for patch selection and cropping from images, useful for data preparation in machine learning tasks.

## Instructions

### Prerequisites:
- Python

### Installation:
```
pip install -r requirements.txt
```
   
### Usage:
```
python main.py --images-path <path_to_images> --output-path <path_to_patches> --patch-size <size_of_patches>
```
Replace placeholders:
- <path_to_images>: Directory containing your source images.
- <path_to_patches>: Desired output directory for cropped patches.
- <size_of_patches>: Pixel dimensions of the patches (e.g., 512 for 512x512).

## Commands
- Mouse:
  - `Hover`: Preview patch area.
  - `Left click`: Draw a new patch (non-overlapping only).
  - `Middle click`: Delete an existing patch.
 
- Keyboard:
  - `s`: Save patches from all drawn squares.
  - `a`: Previous image.
  - `d`: Next image.
  - `q`: Quit the application.
