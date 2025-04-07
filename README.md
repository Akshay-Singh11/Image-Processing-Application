# Advanced Digital Image Processing Project

A comprehensive Python application for image processing operations, featuring a modern user interface with a wide range of adjustments, filters, and transformations.

## Features

### User Interface
- Modern tabbed interface for organized access to all features
- Color-coded controls with intuitive grouping
- Tooltips providing helpful information about each control
- Keyboard shortcuts for common operations
- Side-by-side view of original and processed images
- Scrollable panels for accessing all features regardless of window size

### Basic Operations
- Load and save images in various formats (PNG, JPEG, BMP, GIF, TIFF, WebP)
- Export to different formats with format-specific options (e.g., JPEG quality)
- Undo/Redo functionality with history tracking
- Real-time preview toggle for performance optimization

### Image Adjustments
- Brightness adjustment (-100 to +100)
- Contrast adjustment (0.1x to 3.0x)
- Saturation control (0.0 to 2.0)
- Hue shifting (0° to 360°)

### Transformations
- Rotate images (90° clockwise/counterclockwise)
- Flip images horizontally and vertically
- Crop functionality with interactive selection
- Advanced resizing with pixel and percentage options, preview, and file size estimation

### Filters and Effects
- Multiple built-in filters (Blur, Sharpen, Edge Detection, etc.)
- Sepia tone effect
- Histogram equalization for improved contrast

### Advanced Features
- Zoom and pan functionality for detailed editing
- Image information display (dimensions, format, file size)
- Performance optimization with real-time preview toggle

## Requirements

- Python 3.6 or higher
- Required packages:
  - Pillow (PIL Fork)
  - NumPy
  - Tkinter (usually comes with Python)

## Installation

1. Clone or download this repository
2. Install the required packages:

```bash
pip install pillow numpy
```

## Usage

Run the main application script:

```bash
python image_processor.py
```

### How to use the application:

#### Basic Operations
1. Click "Load Image" to select an image file
2. Use "Save Image" to save your processed image in various formats
3. Use "Undo" and "Redo" buttons to navigate through your edit history
4. Toggle "Real-time Preview" to enable/disable live updates as you adjust settings
5. Click "Reset All" to restore all settings to default

#### Adjustments
1. Use the sliders in the "Basic Adjustments" section to modify brightness and contrast
2. Use the sliders in the "Color Adjustments" section to modify saturation and hue

#### Transformations
1. Use "Rotate Left" and "Rotate Right" buttons to rotate the image by 90 degrees
2. Use "Flip Horiz" and "Flip Vert" buttons to mirror the image
3. For cropping:
   - Click "Toggle Crop Mode" to enter crop mode
   - Click and drag on the processed image to select the area to keep
   - Release the mouse button to apply the crop
4. For resizing:
   - Choose between pixel dimensions or percentage scaling
   - Enter the desired width and height or percentage
   - Check/uncheck "Keep Aspect Ratio" as needed
   - Click "Preview" to see the result without applying
   - View estimated file size before committing changes
   - Click "Apply" to resize the image

#### Filters and Effects
1. Select a filter from the dropdown menu to apply predefined effects
2. Click "Histogram Equalization" to enhance image contrast automatically
3. Select "sepia" from the filter dropdown to apply a vintage sepia tone

#### Advanced Features
1. Zoom and Pan:
   - Use "Zoom In" and "Zoom Out" buttons to adjust the view
   - Use "Reset View" to return to the default view

3. Image Information:
   - View image details in the status bar when an image is loaded

## How It Works

The application uses a combination of approaches for image processing:

1. **PIL/Pillow Approach**: Uses various modules from PIL (Python Imaging Library) including:
   - `ImageEnhance` for brightness, contrast, and saturation adjustments
   - `ImageFilter` for applying predefined and custom filters
   - `ImageOps` for operations like flipping and histogram equalization

2. **NumPy Approach** (Optional): For certain operations, NumPy is used for faster processing and more complex pixel manipulations. The application will fall back to PIL-only methods if NumPy is not available.

### Image Adjustments

- **Brightness**: Adjusted by modifying the brightness factor (-100 to +100)
- **Contrast**: Adjusted by enhancing or reducing the difference between light and dark areas (0.1x to 3.0x)
- **Saturation**: Controls the intensity of colors (0.0 = grayscale, 1.0 = normal, 2.0 = oversaturated)
- **Hue**: Shifts the color spectrum by rotating RGB channels

### Transformations

- **Rotation**: Uses PIL's rotate method with bicubic resampling for quality preservation
- **Flipping**: Mirrors the image horizontally or vertically
- **Cropping**: Interactive selection with coordinate conversion between display and actual image
- **Resizing**: Advanced control over dimensions with pixel or percentage options, preview functionality, and file size estimation

### Filters

- **Built-in Filters**: Applies PIL's predefined filters (blur, sharpen, edge detection, etc.)
- **Sepia**: Special filter that applies a warm, brownish tone to images
- **Histogram Equalization**: Enhances contrast by redistributing pixel intensities

### Advanced Features

- **Zoom & Pan**: Magnify specific areas for detailed editing and navigate around the image

- **Format Options**: Save images in various formats with format-specific settings
- **Real-time Preview Toggle**: Enable/disable live updates for better performance with complex operations

### History Management

- Maintains a history stack of image states
- Allows undoing and redoing operations
- Limits history size to prevent excessive memory usage

## Project Structure

- `image_processor.py` - Main application with GUI and event handling
- `image_utils.py` - Image processing functions and algorithms
- `README.md` - Project documentation

## Potential Future Enhancements

- Histogram visualization for image analysis

- Batch processing for multiple images
- Custom filter creation interface
- Selection tools for localized adjustments
- Advanced text annotation with font selection
- Drawing tools with customizable brushes
- Mask-based editing
- Color picker and color replacement tools
- Advanced color grading tools
- Plugin system for extensibility
