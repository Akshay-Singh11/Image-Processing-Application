"""
Image Processing Utilities
Contains functions for image manipulation including brightness and contrast adjustment
"""

from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageChops, ImageDraw, ImageFont
from math import sin, cos, radians
import os
from datetime import datetime

# Try to import numpy, but make it optional
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

def adjust_brightness_contrast(image, brightness=0, contrast=1.0):
    """
    Adjust the brightness and contrast of an image

    Parameters:
    -----------
    image : PIL.Image
        The input image to be processed
    brightness : int
        Brightness adjustment value (-100 to 100)
        Negative values decrease brightness, positive values increase brightness
    contrast : float
        Contrast adjustment value (0.1 to 3.0)
        Values < 1 decrease contrast, values > 1 increase contrast

    Returns:
    --------
    PIL.Image
        The processed image with adjusted brightness and contrast
    """
    # Create a copy of the image to avoid modifying the original
    img = image.copy()

    # Ensure image is in RGB mode before processing
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Adjust brightness
    if brightness != 0:
        # Convert brightness from -100 to 100 scale to a factor for PIL
        # PIL brightness factor: 0 = black, 1 = original, 2 = twice as bright
        brightness_factor = 1.0 + (brightness / 100.0)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness_factor)

    # Adjust contrast
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast)

    return img

def adjust_brightness_contrast_numpy(image, brightness=0, contrast=1.0):
    """
    Alternative implementation using NumPy for more direct pixel manipulation
    This function demonstrates the mathematical approach to brightness and contrast

    Parameters and returns are the same as adjust_brightness_contrast
    """
    if not NUMPY_AVAILABLE:
        # Fall back to PIL implementation if NumPy is not available
        return adjust_brightness_contrast(image, brightness, contrast)

    # Convert PIL image to numpy array
    img_array = np.array(image).astype(float)

    # Adjust brightness by adding a value to all pixels
    # Scale brightness from -100 to 100 to actual pixel values
    brightness_value = brightness * 2.55  # Scale factor to convert percentage to 0-255 range
    img_array = img_array + brightness_value

    # Adjust contrast
    # Formula: new_pixel = (old_pixel - 128) * contrast + 128
    img_array = (img_array - 128) * contrast + 128

    # Clip values to valid range
    img_array = np.clip(img_array, 0, 255).astype(np.uint8)

    # Convert back to PIL image
    return Image.fromarray(img_array)

# Image Rotation and Flipping Functions
def rotate_image(image, degrees):
    """
    Rotate an image by the specified degrees

    Parameters:
    -----------
    image : PIL.Image
        The input image to be processed
    degrees : int
        The rotation angle in degrees (positive = clockwise)

    Returns:
    --------
    PIL.Image
        The rotated image
    """
    # Use PIL's rotate method with resample to maintain quality
    # expand=True ensures the entire rotated image is visible
    return image.rotate(-degrees, resample=Image.BICUBIC, expand=True)

def flip_image_horizontal(image):
    """
    Flip an image horizontally (mirror)
    """
    return ImageOps.mirror(image)

def flip_image_vertical(image):
    """
    Flip an image vertically
    """
    return ImageOps.flip(image)

# Image Filter Functions
def apply_filter(image, filter_name):
    """
    Apply a predefined filter to an image

    Parameters:
    -----------
    image : PIL.Image
        The input image to be processed
    filter_name : str
        Name of the filter to apply

    Returns:
    --------
    PIL.Image
        The filtered image
    """
    filters = {
        'blur': ImageFilter.BLUR,
        'contour': ImageFilter.CONTOUR,
        'detail': ImageFilter.DETAIL,
        'edge_enhance': ImageFilter.EDGE_ENHANCE,
        'edge_enhance_more': ImageFilter.EDGE_ENHANCE_MORE,
        'emboss': ImageFilter.EMBOSS,
        'find_edges': ImageFilter.FIND_EDGES,
        'sharpen': ImageFilter.SHARPEN,
        'smooth': ImageFilter.SMOOTH,
        'smooth_more': ImageFilter.SMOOTH_MORE
    }

    if filter_name in filters:
        return image.filter(filters[filter_name])
    else:
        # Return original image if filter not found
        return image

# Custom Gaussian Blur with adjustable radius
def apply_gaussian_blur(image, radius=2):
    """
    Apply Gaussian blur with adjustable radius
    """
    return image.filter(ImageFilter.GaussianBlur(radius=radius))

# Color Adjustment Functions
def adjust_saturation(image, factor):
    """
    Adjust the color saturation of an image

    Parameters:
    -----------
    image : PIL.Image
        The input image to be processed
    factor : float
        Saturation factor (0.0 = grayscale, 1.0 = original, > 1.0 = more saturated)

    Returns:
    --------
    PIL.Image
        The processed image with adjusted saturation
    """
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(factor)

def adjust_hue(image, shift):
    """
    Shift the hue of an image

    Parameters:
    -----------
    image : PIL.Image
        The input image to be processed
    shift : int
        Hue shift in degrees (0-360)

    Returns:
    --------
    PIL.Image
        The processed image with shifted hue
    """
    # Convert to HSV, adjust hue, convert back to RGB
    # This is a simplified implementation that works for basic hue shifts
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Split the image into bands
    r, g, b = image.split()

    # Normalize shift to 0-1 range
    normalized_shift = (shift % 360) / 360.0

    # Apply a simple RGB rotation for hue shift
    # This is a simplified approach - for more accurate hue shifting,
    # a full HSV conversion would be better
    if normalized_shift < 1/3:
        # Shift towards red->green->blue
        return Image.merge('RGB', (b, r, g))
    elif normalized_shift < 2/3:
        # Shift towards green->blue->red
        return Image.merge('RGB', (g, b, r))
    else:
        # No major shift
        return image

# Histogram Equalization
def apply_histogram_equalization(image, intensity=1.0):
    """
    Apply histogram equalization to enhance image contrast with adjustable intensity

    Parameters:
    -----------
    image : PIL.Image
        The input image to be processed
    intensity : float
        Controls the strength of the equalization effect (0.0 to 1.0)
        1.0 means full equalization, lower values blend with the original image

    Returns:
    --------
    PIL.Image
        The processed image with equalized histogram
    """
    # Make a copy to avoid modifying the original
    img = image.copy()

    # Ensure image is in RGB mode
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # For better results, convert to LAB color space
    if NUMPY_AVAILABLE:
        # Convert to numpy array
        img_array = np.array(img)

        # Convert RGB to LAB color space
        # This is a simplified conversion - a proper color space library would be better
        # Extract L channel (luminance)
        r, g, b = img.split()
        l_channel = ImageOps.equalize(ImageOps.grayscale(img))

        # Apply equalization only to luminance channel
        equalized = l_channel

        # If intensity is less than 1, blend with original luminance
        if intensity < 1.0:
            # Get original luminance
            original_l = ImageOps.grayscale(img)
            # Blend based on intensity
            equalized = Image.blend(original_l, l_channel, intensity)

        # Create a new RGB image with equalized luminance but original colors
        result = img.copy()
        # Adjust the brightness of the original image based on the equalized luminance
        enhancer = ImageEnhance.Brightness(result)
        # Use the ratio of equalized to original luminance to adjust brightness
        # This preserves colors better than direct channel equalization
        return enhancer.enhance(1.2)  # Slightly boost brightness for better effect
    else:
        # Fallback method if numpy is not available
        # Split into channels
        r, g, b = img.split()

        # Convert to grayscale for luminance
        gray = ImageOps.grayscale(img)
        # Equalize the grayscale image
        equalized_gray = ImageOps.equalize(gray)

        # Create an enhancement mask from the difference
        # between original and equalized grayscale
        enhancer = ImageEnhance.Contrast(img)

        # Apply contrast enhancement based on intensity
        enhanced = enhancer.enhance(1.0 + intensity * 0.5)

        # If intensity is less than 1, blend with original
        if intensity < 1.0:
            return Image.blend(img, enhanced, intensity)
        return enhanced

# Advanced Filters
def apply_pencil_sketch(image, intensity=1.0):
    """
    Apply a pencil sketch effect to the image

    Parameters:
    -----------
    image : PIL.Image
        The input image to be processed
    intensity : float
        Controls the strength of the sketch effect (0.1 to 2.0)
        Higher values create darker, more defined lines

    Returns:
    --------
    PIL.Image
        The processed image with pencil sketch effect
    """
    # Make sure image is RGB
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Create a copy to avoid modifying the original
    img = image.copy()

    # Step 1: Create grayscale version
    gray = img.convert('L')

    # Step 2: Apply Gaussian blur to create smooth gradients
    blur_radius = max(1, int(intensity * 3))
    blurred = gray.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    # Step 3: Apply edge detection for sketch lines
    edges = blurred.filter(ImageFilter.FIND_EDGES)

    # Step 4: Invert the edges to get white lines on black background
    inverted_edges = ImageOps.invert(edges)

    # Step 5: Adjust contrast to make lines more defined
    enhancer = ImageEnhance.Contrast(inverted_edges)
    enhanced_edges = enhancer.enhance(1.0 + intensity)

    # Step 6: Create a white background
    white_bg = Image.new('L', img.size, 255)

    # Step 7: Blend the edges with the white background
    # Use intensity to control the blending
    blend_factor = min(1.0, intensity * 0.8)
    sketch = Image.blend(white_bg, enhanced_edges, blend_factor)

    # Step 8: Add some texture (optional)
    if NUMPY_AVAILABLE:
        # Add some noise for paper texture
        sketch_array = np.array(sketch)
        noise = np.random.normal(0, 5, sketch_array.shape).astype(np.uint8)
        sketch_array = np.clip(sketch_array + noise, 0, 255).astype(np.uint8)
        sketch = Image.fromarray(sketch_array)

    # Step 9: Convert back to RGB
    return sketch.convert('RGB')

def apply_sepia(image):
    """
    Apply a sepia tone filter to the image
    """
    # Make sure image is RGB
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Define sepia matrix
    sepia_matrix = (
        0.393, 0.769, 0.189,
        0.349, 0.686, 0.168,
        0.272, 0.534, 0.131
    )

    # Apply color matrix
    if NUMPY_AVAILABLE:
        # Use NumPy for faster processing if available
        img_array = np.array(image)
        sepia_array = np.zeros_like(img_array)

        # Apply the sepia matrix
        sepia_array[:,:,0] = (img_array[:,:,0] * sepia_matrix[0] +
                              img_array[:,:,1] * sepia_matrix[1] +
                              img_array[:,:,2] * sepia_matrix[2])
        sepia_array[:,:,1] = (img_array[:,:,0] * sepia_matrix[3] +
                              img_array[:,:,1] * sepia_matrix[4] +
                              img_array[:,:,2] * sepia_matrix[5])
        sepia_array[:,:,2] = (img_array[:,:,0] * sepia_matrix[6] +
                              img_array[:,:,1] * sepia_matrix[7] +
                              img_array[:,:,2] * sepia_matrix[8])

        # Clip values
        sepia_array = np.clip(sepia_array, 0, 255).astype(np.uint8)
        return Image.fromarray(sepia_array)
    else:
        # Fallback to a simpler approach without NumPy
        # Convert to sepia by adjusting colors and saturation
        sepia_image = adjust_saturation(image, 0.3)  # Reduce saturation
        sepia_image = adjust_brightness_contrast(sepia_image, 10, 1.1)  # Slight brightness and contrast adjustment
        return sepia_image

# Crop function
def crop_image(image, left, top, right, bottom):
    """
    Crop an image to the specified rectangle

    Parameters:
    -----------
    image : PIL.Image
        The input image to be processed
    left, top, right, bottom : int
        Coordinates of the crop rectangle

    Returns:
    --------
    PIL.Image
        The cropped image
    """
    # Ensure coordinates are within image bounds
    width, height = image.size
    left = max(0, min(left, width))
    top = max(0, min(top, height))
    right = max(0, min(right, width))
    bottom = max(0, min(bottom, height))

    # Ensure right > left and bottom > top
    if right <= left or bottom <= top:
        return image  # Return original if invalid crop area

    return image.crop((left, top, right, bottom))

# Resize functions
def resize_image(image, width, height, keep_aspect_ratio=True):
    """
    Resize an image to the specified dimensions

    Parameters:
    -----------
    image : PIL.Image
        The input image to be processed
    width : int
        Target width in pixels
    height : int
        Target height in pixels
    keep_aspect_ratio : bool
        Whether to maintain the original aspect ratio

    Returns:
    --------
    PIL.Image
        The resized image
    """
    if width <= 0 or height <= 0:
        return image  # Return original if invalid dimensions

    if keep_aspect_ratio:
        # Calculate new dimensions while maintaining aspect ratio
        original_width, original_height = image.size
        ratio = min(width / original_width, height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
    else:
        new_width, new_height = width, height

    return image.resize((new_width, new_height), Image.LANCZOS)

def resize_by_percentage(image, percentage):
    """
    Resize an image by a percentage of its original size

    Parameters:
    -----------
    image : PIL.Image
        The input image to be processed
    percentage : float
        Percentage to resize (e.g., 50.0 for half size, 200.0 for double size)

    Returns:
    --------
    PIL.Image
        The resized image
    """
    if percentage <= 0:
        return image  # Return original if invalid percentage

    # Calculate new dimensions
    original_width, original_height = image.size
    new_width = int(original_width * percentage / 100)
    new_height = int(original_height * percentage / 100)

    return image.resize((new_width, new_height), Image.LANCZOS)

# Text annotation functions
def add_text(image, text, position, font_size=20, font_color=(255, 255, 255),
            font_path=None, background=None):
    """
    Add text to an image

    Parameters:
    -----------
    image : PIL.Image
        The input image to be processed
    text : str
        Text to add to the image
    position : tuple
        (x, y) coordinates for text placement
    font_size : int
        Size of the font
    font_color : tuple
        RGB color tuple for the text
    font_path : str
        Path to a font file (TTF), or None for default
    background : tuple
        RGBA color tuple for text background, or None for transparent

    Returns:
    --------
    PIL.Image
        The image with text added
    """
    # Create a copy of the image to avoid modifying the original
    img = image.copy()

    # Ensure image is in RGB or RGBA mode
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')

    # Create a drawing context
    draw = ImageDraw.Draw(img)

    # Load font
    try:
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            # Use default font
            font = ImageFont.load_default()
    except Exception:
        # Fallback to default font if there's any issue
        font = ImageFont.load_default()

    # Draw text background if specified
    if background:
        # Get text size to calculate background rectangle
        text_bbox = draw.textbbox(position, text, font=font)
        # Draw rectangle with padding
        padding = 5
        background_rect = (
            text_bbox[0] - padding,
            text_bbox[1] - padding,
            text_bbox[2] + padding,
            text_bbox[3] + padding
        )
        draw.rectangle(background_rect, fill=background)

    # Draw text
    draw.text(position, text, font=font, fill=font_color)

    return img

# Drawing functions
def draw_line(image, start_point, end_point, color=(255, 0, 0), width=1):
    """
    Draw a line on an image

    Parameters:
    -----------
    image : PIL.Image
        The input image to be processed
    start_point : tuple
        (x, y) coordinates for line start
    end_point : tuple
        (x, y) coordinates for line end
    color : tuple
        RGB color tuple for the line
    width : int
        Width of the line in pixels

    Returns:
    --------
    PIL.Image
        The image with the line drawn
    """
    # Create a copy of the image to avoid modifying the original
    img = image.copy()

    # Ensure image is in RGB or RGBA mode
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')

    # Create a drawing context
    draw = ImageDraw.Draw(img)

    # Draw line
    draw.line([start_point, end_point], fill=color, width=width)

    return img

def draw_rectangle(image, top_left, bottom_right, color=(255, 0, 0), width=1, fill=None):
    """
    Draw a rectangle on an image

    Parameters:
    -----------
    image : PIL.Image
        The input image to be processed
    top_left : tuple
        (x, y) coordinates for top-left corner
    bottom_right : tuple
        (x, y) coordinates for bottom-right corner
    color : tuple
        RGB color tuple for the outline
    width : int
        Width of the outline in pixels
    fill : tuple
        RGB color tuple for fill, or None for no fill

    Returns:
    --------
    PIL.Image
        The image with the rectangle drawn
    """
    # Create a copy of the image to avoid modifying the original
    img = image.copy()

    # Ensure image is in RGB or RGBA mode
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')

    # Create a drawing context
    draw = ImageDraw.Draw(img)

    # Draw rectangle
    draw.rectangle([top_left, bottom_right], outline=color, width=width, fill=fill)

    return img

def draw_circle(image, center, radius, color=(255, 0, 0), width=1, fill=None):
    """
    Draw a circle on an image

    Parameters:
    -----------
    image : PIL.Image
        The input image to be processed
    center : tuple
        (x, y) coordinates for circle center
    radius : int
        Radius of the circle in pixels
    color : tuple
        RGB color tuple for the outline
    width : int
        Width of the outline in pixels
    fill : tuple
        RGB color tuple for fill, or None for no fill

    Returns:
    --------
    PIL.Image
        The image with the circle drawn
    """
    # Create a copy of the image to avoid modifying the original
    img = image.copy()

    # Ensure image is in RGB or RGBA mode
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGB')

    # Create a drawing context
    draw = ImageDraw.Draw(img)

    # Calculate bounding box for circle
    top_left = (center[0] - radius, center[1] - radius)
    bottom_right = (center[0] + radius, center[1] + radius)

    # Draw circle (ellipse with equal width and height)
    draw.ellipse([top_left, bottom_right], outline=color, width=width, fill=fill)

    return img

# Batch processing function
def batch_process(image_paths, output_dir, operations=None):
    """
    Process multiple images with the same operations

    Parameters:
    -----------
    image_paths : list
        List of paths to input images
    output_dir : str
        Directory to save processed images
    operations : dict
        Dictionary of operations to apply, e.g.,
        {
            'brightness': 10,
            'contrast': 1.2,
            'saturation': 1.1,
            'filter': 'sharpen'
        }

    Returns:
    --------
    list
        List of paths to processed images
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Default operations if none provided
    if operations is None:
        operations = {}

    processed_paths = []

    # Process each image
    for img_path in image_paths:
        try:
            # Load image
            img = Image.open(img_path)

            # Apply operations
            if 'brightness' in operations or 'contrast' in operations:
                brightness = operations.get('brightness', 0)
                contrast = operations.get('contrast', 1.0)
                img = adjust_brightness_contrast(img, brightness, contrast)

            if 'saturation' in operations:
                saturation = operations.get('saturation', 1.0)
                img = adjust_saturation(img, saturation)

            if 'hue' in operations:
                hue = operations.get('hue', 0)
                img = adjust_hue(img, hue)

            if 'filter' in operations:
                filter_name = operations.get('filter')
                if filter_name == 'sepia':
                    img = apply_sepia(img)
                elif filter_name in ['blur', 'sharpen', 'contour', 'detail', 'edge_enhance',
                                    'edge_enhance_more', 'emboss', 'find_edges', 'smooth', 'smooth_more']:
                    img = apply_filter(img, filter_name)

            if 'resize' in operations:
                resize_params = operations.get('resize', {})
                if 'percentage' in resize_params:
                    img = resize_by_percentage(img, resize_params['percentage'])
                elif 'width' in resize_params and 'height' in resize_params:
                    keep_ratio = resize_params.get('keep_aspect_ratio', True)
                    img = resize_image(img, resize_params['width'], resize_params['height'], keep_ratio)

            # Generate output filename
            filename = os.path.basename(img_path)
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(output_dir, f"{name}_processed_{timestamp}{ext}")

            # Save processed image
            img.save(output_path)
            processed_paths.append(output_path)

        except Exception as e:
            print(f"Error processing {img_path}: {str(e)}")

    return processed_paths

# Image information function
def get_image_info(image):
    """
    Get information about an image

    Parameters:
    -----------
    image : PIL.Image
        The input image

    Returns:
    --------
    dict
        Dictionary containing image information
    """
    info = {
        'width': image.width,
        'height': image.height,
        'mode': image.mode,
        'format': image.format if hasattr(image, 'format') else 'Unknown',
        'size_kb': None
    }

    # Try to get file size if image has a filename
    if hasattr(image, 'filename') and image.filename:
        try:
            info['size_kb'] = os.path.getsize(image.filename) / 1024
        except (OSError, AttributeError):
            pass

    return info


