#!/usr/bin/env python3
"""
Digital Image Processing Project - Main Application
Focuses on brightness and contrast adjustment with a simple GUI interface
"""

import tkinter as tk
from tkinter import filedialog, Scale, Button, Label, Frame, StringVar, IntVar, DoubleVar, BooleanVar, Radiobutton, Checkbutton, Canvas, Scrollbar, Entry
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk, ImageOps, ImageFilter, ImageDraw, ImageEnhance, ImageChops
import tkinter.font as tkFont
import os
from image_utils import (
    adjust_brightness_contrast, rotate_image, flip_image_horizontal,
    flip_image_vertical, adjust_saturation, adjust_hue,
    apply_histogram_equalization, apply_sepia, apply_pencil_sketch, crop_image, resize_image,
    resize_by_percentage, get_image_info
)

# No Layer class needed as we're removing layer functionality

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Image Processing Application")
        self.root.geometry("1200x750")

        # Set application theme colors - Modern Color Scheme
        self.bg_color = "#f8f9fa"  # Light background
        self.accent_color = "#6c5ce7"  # Purple accent
        self.text_color = "#2d3436"  # Dark text
        self.highlight_color = "#a29bfe"  # Lighter purple for highlights
        self.secondary_color = "#00b894"  # Mint green for secondary elements
        self.warning_color = "#e17055"  # Coral for warnings/delete buttons
        self.success_color = "#00cec9"  # Teal for success indicators
        self.card_bg = "#ffffff"  # White for card backgrounds
        self.border_color = "#dfe6e9"  # Light gray for borders
        self.shadow_color = "#dddddd"  # Shadow color for cards

        # Configure root window
        self.root.configure(bg=self.bg_color)

        # Create custom fonts - More modern fonts with smaller sizes
        self.header_font = tkFont.Font(family="Segoe UI", size=16, weight="bold")
        self.subheader_font = tkFont.Font(family="Segoe UI", size=12, weight="bold")
        self.normal_font = tkFont.Font(family="Segoe UI", size=10)
        self.button_font = tkFont.Font(family="Segoe UI", size=10, weight="bold")

        # Create custom styles for buttons
        self.create_button_styles()

        # Initialize variables
        self.original_image = None
        self.processed_image = None
        self.current_brightness = 0
        self.current_contrast = 1.0
        self.current_saturation = 1.0
        self.current_hue = 0

        # Initialize filter variables
        self.current_filter = StringVar(value="none")
        self.filter_intensity = DoubleVar(value=1.0)
        self.histogram_eq_var = BooleanVar(value=False)
        self.compare_var = BooleanVar(value=False)

        # History for undo/redo
        self.history = []
        self.history_position = -1
        self.max_history = 10  # Maximum number of states to store

        # Crop mode variables
        self.crop_mode = False
        self.crop_start_x = 0
        self.crop_start_y = 0
        self.crop_end_x = 0
        self.crop_end_y = 0

        # Zoom and pan variables
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.panning = False

        # Real-time preview toggle
        self.real_time_preview = True

        # Removed stickers and text variables

        # Setup UI first
        self.setup_ui()

        # Setup drag and drop after UI is created
        self.setup_drag_drop()

    def setup_ui(self):
        # Main frames
        # Create a frame to hold the scrollbar and canvas with fixed dimensions
        control_container = Frame(self.root, width=300, height=750, bg=self.bg_color)
        control_container.pack(side=tk.LEFT, fill=tk.BOTH)
        control_container.pack_propagate(False)  # Prevent the frame from shrinking

        # Set minimum size to ensure scrolling works properly
        self.root.update()
        self.root.minsize(width=1000, height=750)

        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(control_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tab frames
        self.file_tab = Frame(self.notebook, bg=self.bg_color)
        self.adjust_tab = Frame(self.notebook, bg=self.bg_color)
        self.filter_tab = Frame(self.notebook, bg=self.bg_color)  # New Filter tab
        self.transform_tab = Frame(self.notebook, bg=self.bg_color)
        self.advanced_tab = Frame(self.notebook, bg=self.bg_color)

        # Add tabs to notebook
        self.notebook.add(self.file_tab, text="File")
        self.notebook.add(self.adjust_tab, text="Adjust")
        self.notebook.add(self.filter_tab, text="Filters")  # Add Filter tab
        self.notebook.add(self.transform_tab, text="Transform")
        self.notebook.add(self.advanced_tab, text="Advanced")

        # Configure tab style
        style = ttk.Style()
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.bg_color, padding=[8, 3], font=("Segoe UI", 10))
        style.map("TNotebook.Tab", background=[('selected', self.accent_color)], foreground=[('selected', 'white')])

        # Add scrollable frame to each tab
        self.setup_scrollable_frame(self.file_tab, "file_frame")
        self.setup_scrollable_frame(self.adjust_tab, "adjust_frame")
        self.setup_scrollable_frame(self.filter_tab, "filter_frame")  # Add scrollable frame for filter tab
        self.setup_scrollable_frame(self.transform_tab, "transform_frame")
        self.setup_scrollable_frame(self.advanced_tab, "advanced_frame")

        # Image frame
        self.image_frame = Frame(self.root, width=900, height=750, bg=self.bg_color)
        self.image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Control elements - setup each tab's content
        self.setup_control_panel()

        # Image display areas with improved styling
        self.original_label = Label(self.image_frame, text="Original Image",
                                   font=self.subheader_font, bg=self.bg_color, fg=self.text_color)
        self.original_label.grid(row=0, column=0, padx=10, pady=5)

        self.processed_label = Label(self.image_frame, text="Processed Image",
                                    font=self.subheader_font, bg=self.bg_color, fg=self.text_color)
        self.processed_label.grid(row=0, column=1, padx=10, pady=5)

        # Image canvases with border and shadow effect
        self.original_frame = Frame(self.image_frame, bd=2, relief=tk.GROOVE, bg=self.accent_color)
        self.original_frame.grid(row=1, column=0, padx=10, pady=10)

        self.original_canvas = Label(self.original_frame, bg="#222222", width=450, height=500)
        self.original_canvas.pack(padx=1, pady=1)

        self.processed_frame = Frame(self.image_frame, bd=2, relief=tk.GROOVE, bg=self.accent_color)
        self.processed_frame.grid(row=1, column=1, padx=10, pady=10)

        self.processed_canvas = Label(self.processed_frame, bg="#222222", width=450, height=500)
        self.processed_canvas.pack(padx=1, pady=1)

        # Add mouse events for crop functionality
        self.processed_canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.processed_canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.processed_canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # Status bar with improved styling
        self.status_bar = Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN,
                               anchor=tk.W, bg=self.accent_color, fg="white",
                               font=self.normal_font, padx=10, pady=3)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Add keyboard shortcuts
        self.setup_keyboard_shortcuts()

    def setup_scrollable_frame(self, parent, name):
        """Create a scrollable frame inside a parent widget"""
        # Create a container frame to hold the canvas and scrollbar
        container = Frame(parent, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True)

        # Force the container to maintain its size and not shrink
        container.pack_propagate(False)

        # Create a canvas for scrolling with increased height
        canvas = Canvas(container, bg=self.bg_color, highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas with enhanced styling and always visible
        scrollbar = Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview,
                             width=24, bd=0, troughcolor=self.highlight_color,
                             activebackground=self.accent_color)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Force the scrollbar to always show
        def always_show_scrollbar(*args):
            # Set the scrollbar to always show a minimum position
            if args[0] == 0.0 and args[1] == 1.0:
                # Even when everything is visible, show a bit of the scrollbar
                scrollbar.set(0.0, 0.9)
            else:
                scrollbar.set(*args)

        # Use our custom scrollbar setter instead of the default one
        canvas.configure(yscrollcommand=always_show_scrollbar)

        # No scroll indicator needed for a cleaner interface

        # Create a frame inside the canvas for the controls
        frame = Frame(canvas, bg=self.bg_color, padx=10, pady=10)
        frame_window = canvas.create_window((0, 0), window=frame, anchor="nw")

        # Function to update the scroll region when the frame size changes
        def update_scrollregion(_=None):
            # Update the scrollregion to encompass the inner frame
            canvas.configure(scrollregion=canvas.bbox("all"))

        # Bind the update function to the frame's size changes
        frame.bind("<Configure>", update_scrollregion)

        # Make sure the frame expands to the width of the canvas
        def configure_canvas(event):
            # Set the frame width to match the canvas width
            canvas.itemconfig(frame_window, width=event.width)

        canvas.bind('<Configure>', configure_canvas)

        # Store references to the canvas and frame
        setattr(self, f"{name}_canvas", canvas)
        setattr(self, f"{name}", frame)

        # Add mousewheel scrolling to multiple widgets
        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", lambda event, c=canvas: self._on_mousewheel(event, c))
            widget.bind("<Button-4>", lambda event, c=canvas: self._on_mousewheel_linux(event, c, -1))
            widget.bind("<Button-5>", lambda event, c=canvas: self._on_mousewheel_linux(event, c, 1))

        # Bind mousewheel to canvas and frame
        bind_mousewheel(canvas)
        bind_mousewheel(frame)

        # Also bind to the parent and container for better coverage
        bind_mousewheel(parent)
        bind_mousewheel(container)

        # Force an initial update of the scroll region
        canvas.update_idletasks()
        update_scrollregion()

    def _on_mousewheel(self, event, canvas):
        """Handle mousewheel scrolling on Windows with increased speed"""
        # Scroll direction depends on delta value
        # Increase scroll speed by multiplying the scroll units by 3
        scroll_speed = 3
        canvas.yview_scroll(int(-1 * (event.delta / 120) * scroll_speed), "units")

    def _on_mousewheel_linux(self, _, canvas, direction):
        """Handle mousewheel scrolling on Linux/Mac with increased speed"""
        # Increase scroll speed by multiplying the scroll units by 3
        scroll_speed = 3
        canvas.yview_scroll(direction * scroll_speed, "units")

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common operations"""
        self.root.bind("<Control-o>", lambda _: self.load_image())
        self.root.bind("<Control-s>", lambda _: self.save_image())
        self.root.bind("<Control-z>", lambda _: self.undo())
        self.root.bind("<Control-y>", lambda _: self.redo())
        self.root.bind("<Control-r>", lambda _: self.reset_adjustments())

    def create_button_styles(self):
        """Create custom button styles for a more modern look"""
        # Define a function to create modern-looking buttons with animations
        def create_modern_button(parent, text, command, width=15, bg=None, fg=None, icon=None, is_important=False, **kwargs):
            if bg is None:
                bg = self.accent_color
            if fg is None:
                fg = "white"

            # Create a frame to hold the button (for border effect)
            btn_frame = Frame(parent, bg=self.border_color, padx=1, pady=1)

            # Create the actual button
            btn = Button(btn_frame, text=text, command=command, width=width,
                        bg=bg, fg=fg, font=self.button_font,
                        activebackground=self.highlight_color,
                        relief=tk.FLAT, bd=0, **kwargs)
            btn.pack(padx=1, pady=1)

            # Store original colors for animations
            btn.original_bg = bg
            btn.original_fg = fg
            btn.highlight_bg = self.highlight_color
            btn.is_pulsing = False

            # Add hover effect with smooth transition
            def on_enter(e):
                # Start color transition animation
                animate_color_transition(btn, btn.original_bg, btn.highlight_bg, steps=10)

                # Scale effect (slight grow)
                btn.config(font=(self.button_font['family'], self.button_font['size'] + 1, self.button_font['weight']))

                # If it's an important button, add a glow effect
                if is_important:
                    btn_frame.config(padx=2, pady=2, bg=self.secondary_color)

            def on_leave(e):
                # Reverse color transition animation
                animate_color_transition(btn, btn.highlight_bg, btn.original_bg, steps=10)

                # Reset scale
                btn.config(font=self.button_font)

                # Reset frame
                btn_frame.config(padx=1, pady=1, bg=self.border_color)

            def animate_color_transition(widget, start_color, end_color, steps=10, current_step=0):
                # Convert hex colors to RGB
                start_r = int(start_color[1:3], 16)
                start_g = int(start_color[3:5], 16)
                start_b = int(start_color[5:7], 16)

                end_r = int(end_color[1:3], 16)
                end_g = int(end_color[3:5], 16)
                end_b = int(end_color[5:7], 16)

                # Calculate the color for the current step
                if current_step <= steps:
                    # Calculate the intermediate color
                    r = start_r + int((end_r - start_r) * (current_step / steps))
                    g = start_g + int((end_g - start_g) * (current_step / steps))
                    b = start_b + int((end_b - start_b) * (current_step / steps))

                    # Convert back to hex
                    color = f"#{r:02x}{g:02x}{b:02x}"

                    # Apply the color
                    widget.config(background=color)

                    # Schedule the next step
                    if current_step < steps:
                        widget.after(20, lambda: animate_color_transition(widget, start_color, end_color, steps, current_step + 1))

            # Add pulsing animation for important buttons
            def start_pulse_animation():
                if is_important and not btn.is_pulsing:
                    btn.is_pulsing = True
                    pulse_animation(btn)

            def pulse_animation(widget, direction=1, step=0):
                if not widget.is_pulsing:
                    return

                # Pulse effect using opacity/brightness
                if direction > 0:  # Getting brighter
                    factor = 0.7 + (0.3 * (step / 10))  # 0.7 to 1.0
                else:  # Getting dimmer
                    factor = 1.0 - (0.3 * (step / 10))  # 1.0 to 0.7

                # Adjust color brightness
                r = int(int(widget.original_bg[1:3], 16) * factor)
                g = int(int(widget.original_bg[3:5], 16) * factor)
                b = int(int(widget.original_bg[5:7], 16) * factor)

                # Ensure values are in valid range
                r = min(255, max(0, r))
                g = min(255, max(0, g))
                b = min(255, max(0, b))

                color = f"#{r:02x}{g:02x}{b:02x}"
                widget.config(background=color)

                # Continue animation
                if step >= 10:
                    # Reverse direction
                    widget.after(50, lambda: pulse_animation(widget, -direction, 0))
                else:
                    widget.after(50, lambda: pulse_animation(widget, direction, step + 1))

            # Start pulse for important buttons
            if is_important:
                btn.after(1000, start_pulse_animation)

            # Bind events
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

            # Add icon if provided
            if icon:
                btn.config(text=f"{icon} {text}")

            return btn_frame

        # Store the function as an attribute for later use
        self.create_modern_button = create_modern_button

    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        # Simple implementation without using a tooltip class
        def enter(_):
            # Create a toplevel window
            try:
                x, y, _, _ = widget.bbox("insert")
                x += widget.winfo_rootx() + 25
                y += widget.winfo_rooty() + 25

                # Create the tooltip window
                self.tooltip = tk.Toplevel(widget)
                self.tooltip.wm_overrideredirect(True)
                self.tooltip.wm_geometry(f"+{x}+{y}")

                # Add a label with the tooltip text
                label = Label(self.tooltip, text=text, justify=tk.LEFT,
                             background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                             font=("Arial", "8", "normal"))
                label.pack(ipadx=3, ipady=2)
            except Exception:
                # If we can't get the widget position, don't show the tooltip
                pass

        def leave(_):
            try:
                if hasattr(self, "tooltip") and self.tooltip is not None:
                    self.tooltip.destroy()
                    self.tooltip = None
            except Exception:
                # If there's an error destroying the tooltip, just ignore it
                pass

        # Bind events to the widget
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def setup_adjust_tab(self):
        """Setup the Adjust tab with brightness, contrast, saturation, and hue controls"""
        # Basic Adjustments Section
        basic_section = Frame(self.adjust_frame, bg=self.bg_color)
        basic_section.pack(fill=tk.X, padx=5, pady=5)

        # Section header
        header = Label(basic_section, text="Basic Adjustments", font=self.header_font,
                      bg=self.bg_color, fg=self.accent_color)
        header.pack(pady=10, anchor=tk.W)

        # Brightness control
        brightness_frame = Frame(basic_section, bg=self.bg_color)
        brightness_frame.pack(fill=tk.X, pady=5)

        Label(brightness_frame, text="Brightness", font=self.normal_font,
             bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)

        self.brightness_slider = Scale(
            brightness_frame, from_=-100, to=100, orient=tk.HORIZONTAL,
            command=self.update_image, length=180, bg=self.bg_color,
            highlightthickness=0, troughcolor=self.highlight_color,
            activebackground=self.accent_color
        )
        self.brightness_slider.set(0)
        self.brightness_slider.pack(fill=tk.X)
        self.create_tooltip(self.brightness_slider, "Adjust image brightness (-100 to +100)")

        # Contrast control
        contrast_frame = Frame(basic_section, bg=self.bg_color)
        contrast_frame.pack(fill=tk.X, pady=5)

        Label(contrast_frame, text="Contrast", font=self.normal_font,
             bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)

        self.contrast_slider = Scale(
            contrast_frame, from_=0.1, to=3.0, orient=tk.HORIZONTAL,
            command=self.update_image, resolution=0.1, length=180,
            bg=self.bg_color, highlightthickness=0,
            troughcolor=self.highlight_color, activebackground=self.accent_color
        )
        self.contrast_slider.set(1.0)
        self.contrast_slider.pack(fill=tk.X)
        self.create_tooltip(self.contrast_slider, "Adjust image contrast (0.1 to 3.0)")

        # Color Adjustments Section
        color_section = Frame(self.adjust_frame, bg=self.bg_color)
        color_section.pack(fill=tk.X, padx=5, pady=15)

        # Section header
        color_header = Label(color_section, text="Color Adjustments", font=self.header_font,
                           bg=self.bg_color, fg=self.accent_color)
        color_header.pack(pady=10, anchor=tk.W)

        # Saturation control
        saturation_frame = Frame(color_section, bg=self.bg_color)
        saturation_frame.pack(fill=tk.X, pady=5)

        Label(saturation_frame, text="Saturation", font=self.normal_font,
             bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)

        self.saturation_slider = Scale(
            saturation_frame, from_=0.0, to=2.0, orient=tk.HORIZONTAL,
            command=self.update_image, resolution=0.1, length=180,
            bg=self.bg_color, highlightthickness=0,
            troughcolor=self.highlight_color, activebackground=self.accent_color
        )
        self.saturation_slider.set(1.0)
        self.saturation_slider.pack(fill=tk.X)
        self.create_tooltip(self.saturation_slider, "Adjust color saturation (0.0 to 2.0)")

        # Hue control
        hue_frame = Frame(color_section, bg=self.bg_color)
        hue_frame.pack(fill=tk.X, pady=5)

        Label(hue_frame, text="Hue Shift", font=self.normal_font,
             bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)

        self.hue_slider = Scale(
            hue_frame, from_=0, to=360, orient=tk.HORIZONTAL,
            command=self.update_image, length=180,
            bg=self.bg_color, highlightthickness=0,
            troughcolor=self.highlight_color, activebackground=self.accent_color
        )
        self.hue_slider.set(0)
        self.hue_slider.pack(fill=tk.X)
        self.create_tooltip(self.hue_slider, "Shift image hue (0° to 360°)")

    def setup_transform_tab(self):
        """Setup the Transform tab with rotation, flip, crop, and resize controls"""
        # Transformations Section
        transform_section = Frame(self.transform_frame, bg=self.bg_color)
        transform_section.pack(fill=tk.X, padx=5, pady=5)

        # Section header
        header = Label(transform_section, text="Transformations", font=self.header_font,
                      bg=self.bg_color, fg=self.accent_color)
        header.pack(pady=10, anchor=tk.W)

        # Rotation buttons
        rotation_frame = Frame(transform_section, bg=self.bg_color)
        rotation_frame.pack(fill=tk.X, pady=10)

        Label(rotation_frame, text="Rotation", font=self.subheader_font,
             bg=self.bg_color, fg=self.text_color).pack(pady=5, anchor=tk.W)

        rotation_btns = Frame(rotation_frame, bg=self.bg_color)
        rotation_btns.pack(fill=tk.X, pady=5)

        rotate_left = Button(rotation_btns, text="Rotate Left", command=lambda: self.rotate_image(-90),
                            width=9, bg=self.bg_color, activebackground=self.highlight_color,
                            font=self.normal_font)
        rotate_left.pack(side=tk.LEFT, padx=2)
        self.create_tooltip(rotate_left, "Rotate image 90° counterclockwise")

        rotate_right = Button(rotation_btns, text="Rotate Right", command=lambda: self.rotate_image(90),
                             width=9, bg=self.bg_color, activebackground=self.highlight_color,
                             font=self.normal_font)
        rotate_right.pack(side=tk.RIGHT, padx=2)
        self.create_tooltip(rotate_right, "Rotate image 90° clockwise")

        # Flip buttons
        flip_frame = Frame(transform_section, bg=self.bg_color)
        flip_frame.pack(fill=tk.X, pady=10)

        Label(flip_frame, text="Flip", font=self.subheader_font,
             bg=self.bg_color, fg=self.text_color).pack(pady=5, anchor=tk.W)

        flip_btns = Frame(flip_frame, bg=self.bg_color)
        flip_btns.pack(fill=tk.X, pady=5)

        flip_h = Button(flip_btns, text="Flip Horiz", command=self.flip_horizontal,
                       width=9, bg=self.bg_color, activebackground=self.highlight_color,
                       font=self.normal_font)
        flip_h.pack(side=tk.LEFT, padx=2)
        self.create_tooltip(flip_h, "Flip image horizontally")

        flip_v = Button(flip_btns, text="Flip Vert", command=self.flip_vertical,
                       width=9, bg=self.bg_color, activebackground=self.highlight_color,
                       font=self.normal_font)
        flip_v.pack(side=tk.RIGHT, padx=2)
        self.create_tooltip(flip_v, "Flip image vertically")

        # Crop button
        crop_frame = Frame(transform_section, bg=self.bg_color)
        crop_frame.pack(fill=tk.X, pady=10)

        Label(crop_frame, text="Crop", font=self.subheader_font,
             bg=self.bg_color, fg=self.text_color).pack(pady=5, anchor=tk.W)

        crop_btn = Button(crop_frame, text="Toggle Crop Mode", command=self.toggle_crop_mode,
                         width=20, bg=self.bg_color, activebackground=self.highlight_color,
                         font=self.normal_font)
        crop_btn.pack(pady=5)
        self.create_tooltip(crop_btn, "Click and drag on the image to select crop area")

        # Resize Section
        resize_section = Frame(self.transform_frame, bg=self.bg_color)
        resize_section.pack(fill=tk.X, padx=5, pady=15)

        # Section header
        resize_header = Label(resize_section, text="Resize", font=self.header_font,
                            bg=self.bg_color, fg=self.accent_color)
        resize_header.pack(pady=10, anchor=tk.W)

        # Current size display
        self.current_size_label = Label(resize_section, text="Current size: No image loaded",
                                      font=self.normal_font, bg=self.bg_color, fg=self.text_color)
        self.current_size_label.pack(pady=2, anchor=tk.W)

        # Resize method selection
        method_frame = Frame(resize_section, bg=self.bg_color)
        method_frame.pack(fill=tk.X, pady=5)

        self.resize_method = StringVar(value="pixels")
        Radiobutton(method_frame, text="Pixels", variable=self.resize_method,
                   value="pixels", command=self.toggle_resize_method,
                   bg=self.bg_color, font=self.normal_font).pack(side=tk.LEFT, padx=10)
        Radiobutton(method_frame, text="Percentage", variable=self.resize_method,
                   value="percentage", command=self.toggle_resize_method,
                   bg=self.bg_color, font=self.normal_font).pack(side=tk.RIGHT, padx=10)

        # Pixel dimensions frame
        self.pixel_frame = Frame(resize_section, bg=self.bg_color)
        self.pixel_frame.pack(fill=tk.X, pady=5)

        # Width and height inputs
        Label(self.pixel_frame, text="Width:", bg=self.bg_color,
             fg=self.text_color, font=self.normal_font).pack(side=tk.LEFT, padx=2)
        self.width_entry = Entry(self.pixel_frame, width=5, font=self.normal_font)
        self.width_entry.pack(side=tk.LEFT, padx=2)
        Label(self.pixel_frame, text="px", bg=self.bg_color,
             fg=self.text_color, font=self.normal_font).pack(side=tk.LEFT)

        Label(self.pixel_frame, text="Height:", bg=self.bg_color,
             fg=self.text_color, font=self.normal_font).pack(side=tk.LEFT, padx=2)
        self.height_entry = Entry(self.pixel_frame, width=5, font=self.normal_font)
        self.height_entry.pack(side=tk.LEFT, padx=2)
        Label(self.pixel_frame, text="px", bg=self.bg_color,
             fg=self.text_color, font=self.normal_font).pack(side=tk.LEFT)

        # Percentage frame (hidden initially)
        self.percentage_frame = Frame(resize_section, bg=self.bg_color)

        Label(self.percentage_frame, text="Scale:", bg=self.bg_color,
             fg=self.text_color, font=self.normal_font).pack(side=tk.LEFT, padx=2)
        self.percentage_entry = Entry(self.percentage_frame, width=5, font=self.normal_font)
        self.percentage_entry.insert(0, "100")
        self.percentage_entry.pack(side=tk.LEFT, padx=2)
        Label(self.percentage_frame, text="%", bg=self.bg_color,
             fg=self.text_color, font=self.normal_font).pack(side=tk.LEFT)

        # Keep aspect ratio checkbox
        aspect_frame = Frame(resize_section, bg=self.bg_color)
        aspect_frame.pack(fill=tk.X, pady=5)

        self.keep_aspect_var = tk.BooleanVar(value=True)
        aspect_check = Checkbutton(aspect_frame, text="Keep Aspect Ratio",
                                 variable=self.keep_aspect_var,
                                 command=self.update_linked_dimensions,
                                 bg=self.bg_color, font=self.normal_font)
        aspect_check.pack(anchor=tk.W)
        self.create_tooltip(aspect_check, "Maintain original width-to-height ratio")

        # Preview info
        info_frame = Frame(resize_section, bg=self.bg_color)
        info_frame.pack(fill=tk.X, pady=5)

        self.new_size_label = Label(info_frame, text="New size: -",
                                  font=self.normal_font, bg=self.bg_color, fg=self.text_color)
        self.new_size_label.pack(pady=2, anchor=tk.W)

        self.file_size_label = Label(info_frame, text="Estimated file size: -",
                                   font=self.normal_font, bg=self.bg_color, fg=self.text_color)
        self.file_size_label.pack(pady=2, anchor=tk.W)

        # Buttons
        button_frame = Frame(resize_section, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=10)

        preview_btn = Button(button_frame, text="Preview", command=self.preview_resize,
                            width=9, bg=self.bg_color, activebackground=self.highlight_color,
                            font=self.normal_font)
        preview_btn.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(preview_btn, "Preview the resize without applying")

        apply_btn = Button(button_frame, text="Apply", command=self.apply_resize,
                          width=9, bg=self.accent_color, fg="white",
                          activebackground=self.highlight_color, font=self.normal_font)
        apply_btn.pack(side=tk.RIGHT, padx=5)
        self.create_tooltip(apply_btn, "Apply the resize to the image")

    # Filter tab has been removed

    # Filter-related methods have been removed

    # Filter-related scrollable frames method has been removed

    # Filter-related setup methods have been removed

    # Artistic filters setup method has been removed

    # Edge filters setup method has been removed

    # Filter preset method has been removed

    def apply_filter(self, filter_name):
        """Apply the selected filter to the image"""
        if self.processed_image:
            # Update the current filter
            self.current_filter.set(filter_name)

            # Update the image with the new filter
            self.update_image("force")

            # Add to history for undo/redo
            self.add_to_history()

            # Update status bar
            self.status_bar.config(text=f"Applied filter: {filter_name}")

            # Update current filter label with a more user-friendly name
            filter_display_name = filter_name.replace("_", " ").title()
            self.current_filter_label.config(text=f"Current Filter: {filter_display_name}")

    def reset_filter(self):
        """Reset all filters"""
        if self.processed_image:
            # Reset filter to none
            self.current_filter.set("none")

            # Reset filter intensity
            self.filter_intensity.set(1.0)

            # Update the image
            self.update_image("force")

            # Add to history for undo/redo
            self.add_to_history()

            # Update status bar
            self.status_bar.config(text="Filters reset")

            # Update current filter label
            self.current_filter_label.config(text="No filter selected")

    def toggle_compare_view(self):
        """Toggle between before and after view for filter comparison"""
        if not self.processed_image or not self.original_image:
            return

        # Toggle the compare mode
        self.compare_var.set(not self.compare_var.get())

        # If compare mode is on, show split view
        if self.compare_var.get():
            # Create a composite image with original on left, processed on right
            width, height = self.processed_image.size
            split_point = width // 2

            # Create a new image for the comparison
            compare_img = Image.new('RGB', (width, height))

            # Paste original image on left half
            left_half = self.original_image.crop((0, 0, split_point, height))
            compare_img.paste(left_half, (0, 0))

            # Paste processed image on right half
            right_half = self.processed_image.crop((split_point, 0, width, height))
            compare_img.paste(right_half, (split_point, 0))

            # Draw a dividing line
            draw = ImageDraw.Draw(compare_img)
            draw.line([(split_point, 0), (split_point, height)], fill=(255, 255, 255), width=2)

            # Add labels
            font_size = max(10, height // 30)
            try:
                from PIL import ImageFont
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = None

            # Add "Before" and "After" labels
            draw.text((10, 10), "Before", fill=(255, 255, 255), font=font)
            draw.text((split_point + 10, 10), "After", fill=(255, 255, 255), font=font)

            # Display the comparison image
            self.display_image_object(compare_img)

            # Update status bar
            self.status_bar.config(text="Compare mode: Before/After view")
        else:
            # Return to normal view
            self.display_image()
            self.status_bar.config(text="Normal view restored")

    def apply_filter_preset(self, preset):
        """Apply a predefined filter preset"""
        if not self.processed_image:
            return

        # Reset any current filter
        self.current_filter.set("none")

        # Start with the original image
        img = self.original_image.copy()

        # Apply each filter in the preset sequence
        for filter_name, intensity in preset["filters"]:
            # Set the current filter and intensity
            self.current_filter.set(filter_name)
            self.filter_intensity.set(intensity)

            # Apply this filter
            self.update_image("force")

            # Get the result for the next filter
            img = self.processed_image.copy()

        # Update the display
        self.processed_image = img
        self.display_image()

        # Update status bar
        self.status_bar.config(text=f"Applied preset: {preset['name']}")

        # Update current filter label
        self.current_filter_label.config(text=f"Preset: {preset['name']}")

        # Add to history
        self.add_to_history()

    def save_filter_preset(self):
        """Save the current filter settings as a preset"""
        if not self.processed_image or self.current_filter.get() == "none":
            messagebox.showinfo("No Filter Active", "Please apply a filter before saving a preset.")
            return

        # Ask for preset name
        preset_name = simpledialog.askstring("Save Preset", "Enter a name for this preset:")
        if not preset_name:
            return

        # Create a preset with current filter and intensity
        # Commented out as it's not used in this demo
        # preset = {
        #     "name": preset_name,
        #     "filters": [(self.current_filter.get(), self.filter_intensity.get())]
        # }

        # Add the preset to the list (in a real app, this would be saved to a file)
        messagebox.showinfo("Preset Saved", f"Filter preset '{preset_name}' has been saved.")

        # In a real implementation, you would add this to the preset buttons
        # For this demo, we'll just show a message

    def update_filter_intensity(self, *_):
        """Update the filter intensity"""
        if self.processed_image and self.current_filter.get() != "none":
            # Update the image with the new intensity
            self.update_image("force")

            # Add to history for undo/redo
            self.add_to_history()

    def apply_histogram_eq(self):
        """Apply histogram equalization to the image"""
        if self.processed_image:
            try:
                # Apply histogram equalization with default intensity
                intensity = 1.0  # Full effect
                self.processed_image = apply_histogram_equalization(self.processed_image, intensity)

                # Update the display
                self.update_display_image()

                # Add to history
                self.add_to_history()

                # Update UI
                self.histogram_eq_var.set(True)
                self.status_bar.config(text="Applied histogram equalization")
            except Exception as e:
                # Show detailed error message
                error_msg = f"Failed to apply histogram equalization: {str(e)}"
                print(error_msg)  # Print to console for debugging
                messagebox.showerror("Error", error_msg)

    def apply_sepia(self):
        """Apply sepia tone effect to the image"""
        if self.processed_image:
            try:
                # Apply sepia tone
                self.processed_image = apply_sepia(self.processed_image)

                # Update the display
                self.update_display_image()

                # Add to history
                self.add_to_history()
                self.status_bar.config(text="Applied sepia tone effect")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to apply sepia tone: {str(e)}")

    def setup_special_effects(self):
        """Setup special effects section"""
        # Special effects section
        effects_frame = Frame(self.filter_frame, bg=self.bg_color)
        effects_frame.pack(fill=tk.X, pady=10, padx=5)

        Label(effects_frame, text="Special Effects", font=self.subheader_font,
             bg=self.bg_color, fg=self.text_color).pack(pady=5, anchor=tk.W)

        # Histogram equalization button
        hist_btn = self.create_modern_button(effects_frame, text="Histogram Equalization",
                                          command=self.apply_histogram_eq, width=20,
                                          bg=self.secondary_color)
        hist_btn.pack(pady=5)
        self.create_tooltip(hist_btn, "Enhance contrast by equalizing the image histogram")

        # Sepia button
        sepia_btn = self.create_modern_button(effects_frame, text="Sepia Tone",
                                          command=self.apply_sepia, width=20,
                                          bg=self.secondary_color)
        sepia_btn.pack(pady=5)
        self.create_tooltip(sepia_btn, "Apply a vintage sepia tone effect")

    def setup_filter_tab(self):
        """Setup the Filter tab with various image filters"""
        # Create variables for selected filter
        self.current_filter = StringVar(value="none")
        self.filter_intensity = DoubleVar(value=1.0)

        # No scroll hint needed

        # Basic Filters Section with enhanced styling
        basic_section = Frame(self.filter_frame, bg=self.bg_color)
        basic_section.pack(fill=tk.X, padx=5, pady=5)

        # Create a decorative header with icon
        basic_header_frame = Frame(basic_section, bg=self.bg_color)
        basic_header_frame.pack(fill=tk.X, pady=5)

        # Add decorative icon (size 16)
        basic_icon = Label(basic_header_frame, text="🔍", font=("Segoe UI Emoji", 16),
                          bg=self.bg_color, fg=self.accent_color)
        basic_icon.pack(side=tk.LEFT, padx=(0, 10))

        # Section header
        basic_header = Label(basic_header_frame, text="Basic Filters", font=("Segoe UI", 10, "bold"),
                           bg=self.bg_color, fg=self.accent_color)
        basic_header.pack(side=tk.LEFT, pady=10)

        # Create a grid for basic filter buttons
        basic_grid = Frame(basic_section, bg=self.bg_color)
        basic_grid.pack(fill=tk.X, pady=5)

        # Define main filter categories with their sub-filters
        self.filter_categories = {
            "color": {
                "display": "Color Filters",
                "icon": "🎨",
                "sub_filters": [
                    {"name": "grayscale", "display": "Grayscale", "icon": "⚫"},
                    {"name": "sepia", "display": "Sepia Tone", "icon": "🧴"},
                    {"name": "invert", "display": "Negative", "icon": "🔄"},
                ]
            },
            "adjust": {
                "display": "Adjustments",
                "icon": "☀️",
                "sub_filters": [
                    {"name": "brightness", "display": "Brightness+", "icon": "☀️"},
                    {"name": "contrast", "display": "Contrast+", "icon": "◐"},
                    {"name": "saturation", "display": "Saturation+", "icon": "🌈"}
                ]
            }
        }

        # Create main category buttons in a grid
        self.sub_filter_frames = {}
        row = 0
        for category_key, category_info in self.filter_categories.items():
            # Create a frame for the category with enhanced visual appeal
            # Create shadow frame first (positioned slightly offset)
            shadow_frame = Frame(basic_grid, bg=self.shadow_color, padx=3, pady=3, bd=0)
            shadow_frame.grid(row=row, column=0, columnspan=2, padx=1, pady=1, sticky="nsew")

            # Create actual category frame on top of shadow with gradient-like effect
            category_frame = Frame(basic_grid, bg=self.card_bg, padx=5, pady=5, bd=1, relief=tk.RAISED)
            category_frame.grid(row=row, column=0, columnspan=2, padx=1, pady=1, sticky="nsew", ipadx=2, ipady=2)

            # Add a colored accent bar for visual interest
            accent_bar = Frame(category_frame, height=2, bg=self.accent_color)
            accent_bar.pack(fill=tk.X, pady=(0, 5))

            # Category icon (smaller size)
            icon_label = Label(category_frame, text=category_info["icon"], font=("Segoe UI Emoji", 4),
                             bg=self.card_bg, fg=self.accent_color)
            icon_label.pack(side=tk.LEFT, padx=(5, 10))

            # Category name
            name_label = Label(category_frame, text=category_info["display"], font=self.subheader_font,
                             bg=self.card_bg, fg=self.text_color)
            name_label.pack(side=tk.LEFT, pady=2)

            # Create a frame for sub-filters (initially hidden)
            sub_frame = Frame(basic_grid, bg=self.bg_color)
            sub_frame.grid(row=row+1, column=0, columnspan=2, sticky="nsew")
            sub_frame.grid_remove()  # Hide initially
            self.sub_filter_frames[category_key] = sub_frame

            # Create sub-filter buttons
            for i, filter_info in enumerate(category_info["sub_filters"]):
                sub_col = i % 2
                sub_row = i // 2

                # Create a frame for the sub-filter with enhanced styling
                filter_frame = Frame(sub_frame, bg=self.card_bg, padx=3, pady=3, bd=1, relief=tk.RAISED)
                filter_frame.grid(row=sub_row, column=sub_col, padx=2, pady=2, sticky="nsew", ipadx=2, ipady=2)

                # Add a subtle colored indicator on the left side
                indicator = Frame(filter_frame, width=3, bg=self.secondary_color)
                indicator.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 3))

                # Create a container for the filter content
                content_container = Frame(filter_frame, bg=self.card_bg)
                content_container.pack(fill=tk.BOTH, expand=True)

                # Filter icon (size 16)
                sub_icon_label = Label(content_container, text=filter_info["icon"], font=("Segoe UI Emoji", 16),
                                 bg=self.card_bg, fg=self.accent_color)
                sub_icon_label.pack(pady=(2, 0))

                # Filter name
                sub_name_label = Label(content_container, text=filter_info["display"], font=self.normal_font,
                                 bg=self.card_bg, fg=self.text_color)
                sub_name_label.pack(pady=(0, 2))

                # Make the whole frame clickable to apply filter
                filter_frame.bind("<Button-1>", lambda e, f=filter_info["name"]: self.apply_filter(f))
                sub_icon_label.bind("<Button-1>", lambda e, f=filter_info["name"]: self.apply_filter(f))
                sub_name_label.bind("<Button-1>", lambda e, f=filter_info["name"]: self.apply_filter(f))

                # Hover effect for sub-filter
                def on_enter_sub(e, frame=filter_frame):
                    frame.config(bg=self.highlight_color)
                    for widget in frame.winfo_children():
                        widget.config(bg=self.highlight_color)

                def on_leave_sub(e, frame=filter_frame):
                    frame.config(bg=self.card_bg)
                    for widget in frame.winfo_children():
                        widget.config(bg=self.card_bg)

                filter_frame.bind("<Enter>", on_enter_sub)
                filter_frame.bind("<Leave>", on_leave_sub)

            # Make the category frame clickable to toggle sub-filters
            def toggle_sub_filters(e, key=category_key):
                sub_frame = self.sub_filter_frames[key]
                if sub_frame.winfo_ismapped():
                    sub_frame.grid_remove()
                else:
                    # Hide all other sub-filter frames first
                    for k, frame in self.sub_filter_frames.items():
                        if k != key:
                            frame.grid_remove()
                    sub_frame.grid()

            category_frame.bind("<Button-1>", toggle_sub_filters)
            icon_label.bind("<Button-1>", toggle_sub_filters)
            name_label.bind("<Button-1>", toggle_sub_filters)

            # Hover effect for category
            def on_enter(e, frame=category_frame):
                frame.config(bg=self.highlight_color)
                for widget in frame.winfo_children():
                    widget.config(bg=self.highlight_color)

            def on_leave(e, frame=category_frame):
                frame.config(bg=self.card_bg)
                for widget in frame.winfo_children():
                    widget.config(bg=self.card_bg)

            category_frame.bind("<Enter>", on_enter)
            category_frame.bind("<Leave>", on_leave)

            row += 2  # Increment row for next category (including space for sub-filters)
            icon_label.bind("<Enter>", on_enter)
            icon_label.bind("<Leave>", on_leave)
            name_label.bind("<Enter>", on_enter)
            name_label.bind("<Leave>", on_leave)

        # Advanced Filters Section
        advanced_section = Frame(self.filter_frame, bg=self.bg_color)
        advanced_section.pack(fill=tk.X, padx=5, pady=15)

        # Create a decorative header with icon
        advanced_header_frame = Frame(advanced_section, bg=self.bg_color)
        advanced_header_frame.pack(fill=tk.X, pady=5)

        # Add decorative icon (size 16)
        advanced_icon = Label(advanced_header_frame, text="⚙️", font=("Segoe UI Emoji", 16),
                          bg=self.bg_color, fg=self.accent_color)
        advanced_icon.pack(side=tk.LEFT, padx=(0, 10))

        # Section header
        advanced_header = Label(advanced_header_frame, text="Advanced Filters", font=("Segoe UI", 10, "bold"),
                              bg=self.bg_color, fg=self.accent_color)
        advanced_header.pack(side=tk.LEFT, pady=10)

        # Define advanced filter categories with their sub-filters
        self.advanced_filter_categories = {
            "blur": {
                "display": "Blur Filters",
                "icon": "🌫️",
                "sub_filters": [
                    {"name": "gaussian_blur", "display": "Gaussian Blur", "icon": "🌫️"},
                    {"name": "median_blur", "display": "Median Blur", "icon": "🧩"},
                ]
            },
            "enhance": {
                "display": "Enhancement",
                "icon": "✨",
                "sub_filters": [
                    {"name": "sharpen", "display": "Sharpen", "icon": "✨"},
                    {"name": "edge_detection", "display": "Edge Detection", "icon": "📐"},
                    {"name": "emboss", "display": "Emboss", "icon": "🗿"},
                    {"name": "threshold", "display": "Threshold", "icon": "⬛"}
                ]
            }
        }

        # Create a grid for advanced filter buttons
        advanced_grid = Frame(advanced_section, bg=self.bg_color)
        advanced_grid.pack(fill=tk.X, pady=5)

        # Create main category buttons in a grid
        self.advanced_sub_filter_frames = {}
        row = 0
        for category_key, category_info in self.advanced_filter_categories.items():
            # Create a frame for the category (ultra-compact size with shadow effect)
            # Create shadow frame first (positioned slightly offset)
            shadow_frame = Frame(advanced_grid, bg=self.shadow_color, padx=3, pady=3, bd=0)
            shadow_frame.grid(row=row, column=0, columnspan=2, padx=1, pady=1, sticky="nsew")

            # Create actual category frame on top of shadow
            category_frame = Frame(advanced_grid, bg=self.card_bg, padx=3, pady=3, bd=1, relief=tk.RAISED)
            category_frame.grid(row=row, column=0, columnspan=2, padx=1, pady=1, sticky="nsew", ipadx=1, ipady=1)

            # Category icon (size 16)
            icon_label = Label(category_frame, text=category_info["icon"], font=("Segoe UI Emoji", 16),
                             bg=self.card_bg, fg=self.accent_color)
            icon_label.pack(side=tk.LEFT, padx=(5, 10))

            # Category name
            name_label = Label(category_frame, text=category_info["display"], font=("Segoe UI", 10, "bold"),
                             bg=self.card_bg, fg=self.text_color)
            name_label.pack(side=tk.LEFT, pady=2)

            # Create a frame for sub-filters (initially hidden)
            sub_frame = Frame(advanced_grid, bg=self.bg_color)
            sub_frame.grid(row=row+1, column=0, columnspan=2, sticky="nsew")
            sub_frame.grid_remove()  # Hide initially
            self.advanced_sub_filter_frames[category_key] = sub_frame

            # Create sub-filter buttons
            for i, filter_info in enumerate(category_info["sub_filters"]):
                sub_col = i % 2
                sub_row = i // 2

                # Create a frame for the sub-filter
                filter_frame = Frame(sub_frame, bg=self.card_bg, padx=3, pady=3, bd=1, relief=tk.RAISED)
                filter_frame.grid(row=sub_row, column=sub_col, padx=1, pady=1, sticky="nsew", ipadx=1, ipady=1)

                # Filter icon (size 16)
                sub_icon_label = Label(filter_frame, text=filter_info["icon"], font=("Segoe UI Emoji", 16),
                                 bg=self.card_bg, fg=self.accent_color)
                sub_icon_label.pack(pady=0)

                # Filter name
                sub_name_label = Label(filter_frame, text=filter_info["display"], font=self.normal_font,
                                 bg=self.card_bg, fg=self.text_color)
                sub_name_label.pack(pady=0)

                # Make the whole frame clickable to apply filter
                filter_frame.bind("<Button-1>", lambda e, f=filter_info["name"]: self.apply_filter(f))
                sub_icon_label.bind("<Button-1>", lambda e, f=filter_info["name"]: self.apply_filter(f))
                sub_name_label.bind("<Button-1>", lambda e, f=filter_info["name"]: self.apply_filter(f))

                # Hover effect for sub-filter
                def on_enter_sub(e, frame=filter_frame):
                    frame.config(bg=self.highlight_color)
                    for widget in frame.winfo_children():
                        widget.config(bg=self.highlight_color)

                def on_leave_sub(e, frame=filter_frame):
                    frame.config(bg=self.card_bg)
                    for widget in frame.winfo_children():
                        widget.config(bg=self.card_bg)

                filter_frame.bind("<Enter>", on_enter_sub)
                filter_frame.bind("<Leave>", on_leave_sub)

            # Make the category frame clickable to toggle sub-filters
            def toggle_advanced_sub_filters(e, key=category_key):
                sub_frame = self.advanced_sub_filter_frames[key]
                if sub_frame.winfo_ismapped():
                    sub_frame.grid_remove()
                else:
                    # Hide all other sub-filter frames first
                    for k, frame in self.advanced_sub_filter_frames.items():
                        if k != key:
                            frame.grid_remove()
                    sub_frame.grid()

            category_frame.bind("<Button-1>", toggle_advanced_sub_filters)
            icon_label.bind("<Button-1>", toggle_advanced_sub_filters)
            name_label.bind("<Button-1>", toggle_advanced_sub_filters)

            # Hover effect for category
            def on_enter(e, frame=category_frame):
                frame.config(bg=self.highlight_color)
                for widget in frame.winfo_children():
                    widget.config(bg=self.highlight_color)

            def on_leave(e, frame=category_frame):
                frame.config(bg=self.card_bg)
                for widget in frame.winfo_children():
                    widget.config(bg=self.card_bg)

            category_frame.bind("<Enter>", on_enter)
            category_frame.bind("<Leave>", on_leave)
            icon_label.bind("<Enter>", on_enter)
            icon_label.bind("<Leave>", on_leave)
            name_label.bind("<Enter>", on_enter)
            name_label.bind("<Leave>", on_leave)

            row += 2  # Increment row for next category (including space for sub-filters)
            icon_label.bind("<Enter>", on_enter)
            icon_label.bind("<Leave>", on_leave)
            name_label.bind("<Enter>", on_enter)
            name_label.bind("<Leave>", on_leave)

        # Effects Section with decorative elements
        effects_section = Frame(self.filter_frame, bg=self.bg_color)
        effects_section.pack(fill=tk.X, padx=5, pady=15)

        # Create a decorative header with icon
        effects_header_frame = Frame(effects_section, bg=self.bg_color)
        effects_header_frame.pack(fill=tk.X, pady=5)

        # Add decorative icon (size 16)
        effects_icon = Label(effects_header_frame, text="🎨", font=("Segoe UI Emoji", 16),
                           bg=self.bg_color, fg=self.accent_color)
        effects_icon.pack(side=tk.LEFT, padx=(0, 10))

        # Section header with gradient effect
        effects_header = Label(effects_header_frame, text="Effects & Transformations", font=("Segoe UI", 10, "bold"),
                             bg=self.bg_color, fg=self.accent_color)
        effects_header.pack(side=tk.LEFT, pady=10)

        # Add a decorative line under the header
        header_line = Frame(effects_section, height=2, bg=self.accent_color)
        header_line.pack(fill=tk.X, pady=(0, 10))

        # Description text
        effects_desc = Label(effects_section, text="Apply artistic effects and transformations to your image",
                           font=self.normal_font, bg=self.bg_color, fg=self.text_color, justify=tk.LEFT)
        effects_desc.pack(anchor=tk.W, pady=(0, 10))

        # Define effects filter categories with their sub-filters
        self.effects_filter_categories = {
            "enhance": {
                "display": "Enhancement Effects",
                "icon": "📊",
                "sub_filters": [
                    {"name": "histogram_eq", "display": "Histogram Eq.", "icon": "📊",
                     "desc": "Enhance contrast by equalizing the image histogram"},
                    {"name": "color_balance", "display": "Color Balance", "icon": "🎨",
                     "desc": "Adjust the balance between color channels"},
                    {"name": "vignette", "display": "Vignette", "icon": "🔍",
                     "desc": "Add a soft dark border around the edges"},
                ]
            },
            "artistic": {
                "display": "Artistic Effects",
                "icon": "🖼️",
                "sub_filters": [
                    {"name": "cartoonify", "display": "Cartoonify", "icon": "🖼️",
                     "desc": "Transform your image into a cartoon-like style"},
                    {"name": "oil_painting", "display": "Oil Painting", "icon": "🖌️",
                     "desc": "Create an oil painting effect with textured appearance"},
                    {"name": "pencil_sketch", "display": "Pencil Sketch", "icon": "✏️",
                     "desc": "Convert your image to a hand-drawn pencil sketch"}
                ]
            }
        }

        # Create a grid for effects filter cards
        effects_grid = Frame(effects_section, bg=self.bg_color)
        effects_grid.pack(fill=tk.X, pady=5)

        # Create main category buttons in a grid
        self.effects_sub_filter_frames = {}
        row = 0
        for category_key, category_info in self.effects_filter_categories.items():
            # Create a frame for the category (ultra-compact size with shadow effect)
            # Create shadow frame first (positioned slightly offset)
            shadow_frame = Frame(effects_grid, bg=self.shadow_color, padx=3, pady=3, bd=0)
            shadow_frame.grid(row=row, column=0, columnspan=2, padx=1, pady=1, sticky="nsew")

            # Create actual category frame on top of shadow
            category_frame = Frame(effects_grid, bg=self.card_bg, padx=3, pady=3, bd=1, relief=tk.RAISED)
            category_frame.grid(row=row, column=0, columnspan=2, padx=1, pady=1, sticky="nsew", ipadx=1, ipady=1)

            # Add a colored border on the left side for visual interest (thinner)
            left_border = Frame(category_frame, width=2, bg=self.accent_color)
            left_border.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

            # Create content frame
            content_frame = Frame(category_frame, bg=self.card_bg)
            content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Category icon (size 16)
            icon_label = Label(content_frame, text=category_info["icon"], font=("Segoe UI Emoji", 16),
                             bg=self.card_bg, fg=self.accent_color)
            icon_label.pack(side=tk.LEFT, padx=(0, 5))

            # Category name
            name_label = Label(content_frame, text=category_info["display"], font=("Segoe UI", 10, "bold"),
                             bg=self.card_bg, fg=self.text_color)
            name_label.pack(side=tk.LEFT, pady=2)

            # Create a frame for sub-filters (initially hidden)
            sub_frame = Frame(effects_grid, bg=self.bg_color)
            sub_frame.grid(row=row+1, column=0, columnspan=2, sticky="nsew")
            sub_frame.grid_remove()  # Hide initially
            self.effects_sub_filter_frames[category_key] = sub_frame

            # Create sub-filter buttons
            for i, filter_info in enumerate(category_info["sub_filters"]):
                sub_col = i % 2
                sub_row = i // 2

                # Create a frame for the sub-filter
                filter_frame = Frame(sub_frame, bg=self.card_bg, padx=4, pady=4, bd=0)
                filter_frame.grid(row=sub_row, column=sub_col, padx=2, pady=2, sticky="nsew")

                # Add a colored border on the left side for visual interest (thinner)
                sub_left_border = Frame(filter_frame, width=2, bg=self.accent_color)
                sub_left_border.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

                # Create content frame
                sub_content_frame = Frame(filter_frame, bg=self.card_bg)
                sub_content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                # Create top frame for icon and name
                top_frame = Frame(sub_content_frame, bg=self.card_bg)
                top_frame.pack(fill=tk.X, anchor=tk.W)

                # Filter icon (size 16)
                sub_icon_label = Label(top_frame, text=filter_info["icon"], font=("Segoe UI Emoji", 16),
                                 bg=self.card_bg, fg=self.accent_color)
                sub_icon_label.pack(side=tk.LEFT, padx=(0, 5))

                # Filter name
                sub_name_label = Label(top_frame, text=filter_info["display"], font=self.normal_font,
                                 bg=self.card_bg, fg=self.text_color)
                sub_name_label.pack(side=tk.LEFT)

                # Filter description
                desc_label = Label(sub_content_frame, text=filter_info["desc"], font=self.normal_font,
                                 bg=self.card_bg, fg=self.text_color, wraplength=120, justify=tk.LEFT)
                desc_label.pack(fill=tk.X, pady=(2, 5), anchor=tk.W)

                # Apply button
                apply_btn = Button(sub_content_frame, text="Apply", font=self.button_font,
                                 bg=self.accent_color, fg="white", bd=0, padx=10, pady=2,
                                 command=lambda f=filter_info["name"]: self.apply_filter(f))
                apply_btn.pack(anchor=tk.W)

            # Make the category frame clickable to toggle sub-filters
            def toggle_effects_sub_filters(e, key=category_key):
                sub_frame = self.effects_sub_filter_frames[key]
                if sub_frame.winfo_ismapped():
                    sub_frame.grid_remove()
                else:
                    # Hide all other sub-filter frames first
                    for k, frame in self.effects_sub_filter_frames.items():
                        if k != key:
                            frame.grid_remove()
                    sub_frame.grid()

            category_frame.bind("<Button-1>", toggle_effects_sub_filters)
            content_frame.bind("<Button-1>", toggle_effects_sub_filters)
            icon_label.bind("<Button-1>", toggle_effects_sub_filters)
            name_label.bind("<Button-1>", toggle_effects_sub_filters)

            # Hover effect for category
            def on_enter(e, frame=category_frame, border=left_border):
                frame.config(bg=self.highlight_color)
                border.config(bg=self.secondary_color)
                for widget in frame.winfo_children():
                    if widget != border:
                        widget.config(bg=self.highlight_color)
                content_frame.config(bg=self.highlight_color)
                icon_label.config(bg=self.highlight_color)
                name_label.config(bg=self.highlight_color)

            def on_leave(e, frame=category_frame, border=left_border):
                frame.config(bg=self.card_bg)
                border.config(bg=self.accent_color)
                for widget in frame.winfo_children():
                    if widget != border:
                        widget.config(bg=self.card_bg)
                content_frame.config(bg=self.card_bg)
                icon_label.config(bg=self.card_bg)
                name_label.config(bg=self.card_bg)

            # Bind hover events
            for widget in [category_frame, content_frame, icon_label, name_label]:
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)

        # Morphological Section with decorative elements
        morph_section = Frame(self.filter_frame, bg=self.bg_color)
        morph_section.pack(fill=tk.X, padx=5, pady=15)

        # Create a decorative header with icon
        morph_header_frame = Frame(morph_section, bg=self.bg_color)
        morph_header_frame.pack(fill=tk.X, pady=5)

        # Add decorative icon (size 16)
        morph_icon = Label(morph_header_frame, text="🔄", font=("Segoe UI Emoji", 16),
                          bg=self.bg_color, fg=self.accent_color)
        morph_icon.pack(side=tk.LEFT, padx=(0, 10))

        # Section header with gradient effect
        morph_header = Label(morph_header_frame, text="Morphological Transformations", font=("Segoe UI", 10, "bold"),
                           bg=self.bg_color, fg=self.accent_color)
        morph_header.pack(side=tk.LEFT, pady=10)

        # Add a decorative line under the header
        morph_line = Frame(morph_section, height=2, bg=self.accent_color)
        morph_line.pack(fill=tk.X, pady=(0, 10))

        # Description text
        morph_desc = Label(morph_section, text="Apply mathematical morphology operations to your image",
                          font=self.normal_font, bg=self.bg_color, fg=self.text_color, justify=tk.LEFT)
        morph_desc.pack(anchor=tk.W, pady=(0, 10))

        # Define morphological filter categories with their sub-filters
        self.morph_filter_categories = {
            "basic": {
                "display": "Basic Morphology",
                "icon": "➖",
                "sub_filters": [
                    {"name": "erosion", "display": "Erosion", "icon": "➖",
                     "desc": "Shrinks bright regions and enlarges dark regions"},
                    {"name": "dilation", "display": "Dilation", "icon": "➕",
                     "desc": "Enlarges bright regions and shrinks dark regions"},
                ]
            },
            "compound": {
                "display": "Compound Operations",
                "icon": "⭕",
                "sub_filters": [
                    {"name": "opening", "display": "Opening", "icon": "⭕",
                     "desc": "Erosion followed by dilation, removes small bright spots"},
                    {"name": "closing", "display": "Closing", "icon": "⚫",
                     "desc": "Dilation followed by erosion, removes small dark holes"}
                ]
            }
        }

        # Create a grid for morphological filter cards
        morph_grid = Frame(morph_section, bg=self.bg_color)
        morph_grid.pack(fill=tk.X, pady=5)

        # Create main category buttons in a grid
        self.morph_sub_filter_frames = {}
        row = 0
        for category_key, category_info in self.morph_filter_categories.items():
            # Create a frame for the category (ultra-compact size with shadow effect)
            # Create shadow frame first (positioned slightly offset)
            shadow_frame = Frame(morph_grid, bg=self.shadow_color, padx=3, pady=3, bd=0)
            shadow_frame.grid(row=row, column=0, columnspan=2, padx=1, pady=1, sticky="nsew")

            # Create actual category frame on top of shadow
            category_frame = Frame(morph_grid, bg=self.card_bg, padx=3, pady=3, bd=1, relief=tk.RAISED)
            category_frame.grid(row=row, column=0, columnspan=2, padx=1, pady=1, sticky="nsew", ipadx=1, ipady=1)

            # Add a colored border on the left side for visual interest (thinner)
            left_border = Frame(category_frame, width=2, bg=self.secondary_color)
            left_border.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

            # Create content frame
            content_frame = Frame(category_frame, bg=self.card_bg)
            content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Category icon (size 16)
            icon_label = Label(content_frame, text=category_info["icon"], font=("Segoe UI Emoji", 16),
                             bg=self.card_bg, fg=self.secondary_color)
            icon_label.pack(side=tk.LEFT, padx=(0, 5))

            # Category name
            name_label = Label(content_frame, text=category_info["display"], font=("Segoe UI", 10, "bold"),
                             bg=self.card_bg, fg=self.text_color)
            name_label.pack(side=tk.LEFT, pady=2)

            # Create a frame for sub-filters (initially hidden)
            sub_frame = Frame(morph_grid, bg=self.bg_color)
            sub_frame.grid(row=row+1, column=0, columnspan=2, sticky="nsew")
            sub_frame.grid_remove()  # Hide initially
            self.morph_sub_filter_frames[category_key] = sub_frame

            # Create sub-filter buttons
            for i, filter_info in enumerate(category_info["sub_filters"]):
                sub_col = i % 2
                sub_row = i // 2

                # Create a frame for the sub-filter
                filter_frame = Frame(sub_frame, bg=self.card_bg, padx=4, pady=4, bd=0)
                filter_frame.grid(row=sub_row, column=sub_col, padx=2, pady=2, sticky="nsew")

                # Add a colored border on the left side for visual interest (thinner)
                sub_left_border = Frame(filter_frame, width=2, bg=self.secondary_color)
                sub_left_border.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

                # Create content frame
                sub_content_frame = Frame(filter_frame, bg=self.card_bg)
                sub_content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                # Create top frame for icon and name
                top_frame = Frame(sub_content_frame, bg=self.card_bg)
                top_frame.pack(fill=tk.X, anchor=tk.W)

                # Filter icon (size 16)
                sub_icon_label = Label(top_frame, text=filter_info["icon"], font=("Segoe UI Emoji", 16),
                                 bg=self.card_bg, fg=self.secondary_color)
                sub_icon_label.pack(side=tk.LEFT, padx=(0, 5))

                # Filter name
                sub_name_label = Label(top_frame, text=filter_info["display"], font=self.normal_font,
                                 bg=self.card_bg, fg=self.text_color)
                sub_name_label.pack(side=tk.LEFT)

                # Filter description
                desc_label = Label(sub_content_frame, text=filter_info["desc"], font=self.normal_font,
                                 bg=self.card_bg, fg=self.text_color, wraplength=120, justify=tk.LEFT)
                desc_label.pack(fill=tk.X, pady=(2, 5), anchor=tk.W)

                # Apply button
                apply_btn = Button(sub_content_frame, text="Apply", font=self.button_font,
                                 bg=self.secondary_color, fg="white", bd=0, padx=10, pady=2,
                                 command=lambda f=filter_info["name"]: self.apply_filter(f))
                apply_btn.pack(anchor=tk.W)

                # Make the whole frame clickable to apply filter
                filter_frame.bind("<Button-1>", lambda e, f=filter_info["name"]: self.apply_filter(f))
                sub_icon_label.bind("<Button-1>", lambda e, f=filter_info["name"]: self.apply_filter(f))
                sub_name_label.bind("<Button-1>", lambda e, f=filter_info["name"]: self.apply_filter(f))
                desc_label.bind("<Button-1>", lambda e, f=filter_info["name"]: self.apply_filter(f))

                # Hover effect for sub-filter
                def on_enter_sub(e, frame=filter_frame, border=sub_left_border, btn=apply_btn):
                    frame.config(bg=self.highlight_color)
                    border.config(bg=self.accent_color)
                    for widget in frame.winfo_children():
                        if widget != border:
                            widget.config(bg=self.highlight_color)
                    sub_content_frame.config(bg=self.highlight_color)
                    top_frame.config(bg=self.highlight_color)
                    sub_icon_label.config(bg=self.highlight_color)
                    sub_name_label.config(bg=self.highlight_color)
                    desc_label.config(bg=self.highlight_color)
                    btn.config(bg=self.accent_color)

                def on_leave_sub(e, frame=filter_frame, border=sub_left_border, btn=apply_btn):
                    frame.config(bg=self.card_bg)
                    border.config(bg=self.secondary_color)
                    for widget in frame.winfo_children():
                        if widget != border:
                            widget.config(bg=self.card_bg)
                    sub_content_frame.config(bg=self.card_bg)
                    top_frame.config(bg=self.card_bg)
                    sub_icon_label.config(bg=self.card_bg)
                    sub_name_label.config(bg=self.card_bg)
                    desc_label.config(bg=self.card_bg)
                    btn.config(bg=self.secondary_color)

                filter_frame.bind("<Enter>", on_enter_sub)
                filter_frame.bind("<Leave>", on_leave_sub)

            # Make the category frame clickable to toggle sub-filters
            def toggle_morph_sub_filters(e, key=category_key):
                sub_frame = self.morph_sub_filter_frames[key]
                if sub_frame.winfo_ismapped():
                    sub_frame.grid_remove()
                else:
                    # Hide all other sub-filter frames first
                    for k, frame in self.morph_sub_filter_frames.items():
                        if k != key:
                            frame.grid_remove()
                    sub_frame.grid()

            category_frame.bind("<Button-1>", toggle_morph_sub_filters)
            content_frame.bind("<Button-1>", toggle_morph_sub_filters)
            icon_label.bind("<Button-1>", toggle_morph_sub_filters)
            name_label.bind("<Button-1>", toggle_morph_sub_filters)

            # Hover effect for category
            def on_enter(e, frame=category_frame, border=left_border):
                frame.config(bg=self.highlight_color)
                border.config(bg=self.accent_color)
                for widget in frame.winfo_children():
                    if widget != border:
                        widget.config(bg=self.highlight_color)
                content_frame.config(bg=self.highlight_color)
                icon_label.config(bg=self.highlight_color)
                name_label.config(bg=self.highlight_color)

            def on_leave(e, frame=category_frame, border=left_border):
                frame.config(bg=self.card_bg)
                border.config(bg=self.secondary_color)
                for widget in frame.winfo_children():
                    if widget != border:
                        widget.config(bg=self.card_bg)
                content_frame.config(bg=self.card_bg)
                icon_label.config(bg=self.card_bg)
                name_label.config(bg=self.card_bg)

            # Bind hover events
            for widget in [category_frame, content_frame, icon_label, name_label]:
                widget.bind("<Enter>", on_enter)
                widget.bind("<Leave>", on_leave)

            row += 2  # Increment row for next category (including space for sub-filters)

        # Filter Controls Section
        filter_controls_frame = Frame(self.filter_frame, bg=self.bg_color)
        filter_controls_frame.pack(fill=tk.X, padx=5, pady=15)

        # Filter Intensity Slider
        intensity_frame = Frame(filter_controls_frame, bg=self.bg_color)
        intensity_frame.pack(fill=tk.X, pady=5)

        Label(intensity_frame, text="Filter Intensity", font=self.subheader_font,
             bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)

        intensity_slider = Scale(
            intensity_frame, from_=0.1, to=2.0, orient=tk.HORIZONTAL,
            variable=self.filter_intensity, resolution=0.1, length=250,
            command=self.update_filter_intensity,
            bg=self.bg_color, highlightthickness=0,
            troughcolor=self.highlight_color, activebackground=self.accent_color
        )

        # Filter Actions Frame
        filter_actions_frame = Frame(filter_controls_frame, bg=self.bg_color)
        filter_actions_frame.pack(fill=tk.X, pady=10)

        # Current Filter Display
        self.current_filter_label = Label(filter_actions_frame,
                                        text="No filter selected",
                                        font=self.subheader_font,
                                        bg=self.bg_color, fg=self.accent_color)
        self.current_filter_label.pack(side=tk.LEFT, anchor=tk.W, padx=(0, 10))

        # Clear Filter Button
        clear_filter_btn = Button(filter_actions_frame, text="Clear Filter",
                                 command=self.reset_filter,
                                 bg=self.secondary_color, fg="white",
                                 font=self.button_font, bd=0, padx=10, pady=5)
        clear_filter_btn.pack(side=tk.RIGHT)

        # Compare Button (Toggle Before/After View)
        self.compare_var = BooleanVar(value=False)
        compare_btn = Button(filter_actions_frame, text="Compare (Before/After)",
                            command=self.toggle_compare_view,
                            bg=self.accent_color, fg="white",
                            font=self.button_font, bd=0, padx=10, pady=5)
        compare_btn.pack(side=tk.RIGHT, padx=10)

        # Filter Presets Section
        presets_frame = Frame(filter_controls_frame, bg=self.bg_color)
        presets_frame.pack(fill=tk.X, pady=10)

        Label(presets_frame, text="Filter Presets", font=self.subheader_font,
             bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W, pady=(0, 5))

        # Preset Buttons Frame
        preset_buttons_frame = Frame(presets_frame, bg=self.bg_color)
        preset_buttons_frame.pack(fill=tk.X)

        # Add some preset filter combinations
        presets = [
            {"name": "Vintage", "filters": [("sepia", 0.8), ("vignette", 1.2)]},
            {"name": "Dramatic", "filters": [("contrast", 1.5), ("brightness", 0.8)]},
            {"name": "Sketch", "filters": [("pencil_sketch", 1.0)]},
            {"name": "Vibrant", "filters": [("saturation", 1.5), ("brightness", 1.2)]}
        ]

        # Create preset buttons
        for i, preset in enumerate(presets):
            preset_btn = Button(preset_buttons_frame, text=preset["name"],
                              command=lambda p=preset: self.apply_filter_preset(p),
                              bg=self.card_bg, fg=self.text_color,
                              font=self.button_font, bd=1, padx=10, pady=5)
            preset_btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            preset_buttons_frame.columnconfigure(i, weight=1)

        # Save Preset Button
        save_preset_btn = Button(presets_frame, text="Save Current as Preset",
                               command=self.save_filter_preset,
                               bg=self.bg_color, fg=self.accent_color,
                               font=self.button_font, bd=1, padx=10, pady=5)
        save_preset_btn.pack(anchor=tk.E, pady=5)
        intensity_slider.set(1.0)
        intensity_slider.pack(fill=tk.X, pady=5)
        self.create_tooltip(intensity_slider, "Adjust the intensity of the selected filter (0.1 to 2.0)")

        # Reset Filter Button
        reset_filter_btn = Button(intensity_frame, text="Reset Filter", command=self.reset_filter,
                                width=15, bg=self.warning_color, fg="white",
                                activebackground="#c0392b", font=self.normal_font)
        reset_filter_btn.pack(pady=10)
        self.create_tooltip(reset_filter_btn, "Remove all filters and return to original image")

    def setup_advanced_tab(self):
        """Setup the Advanced tab with zoom/pan controls"""
        # Zoom and Pan Section
        zoom_section = Frame(self.advanced_frame, bg=self.bg_color)
        zoom_section.pack(fill=tk.X, padx=5, pady=5)

        # Section header
        header = Label(zoom_section, text="Zoom & Pan", font=self.header_font,
                      bg=self.bg_color, fg=self.accent_color)
        header.pack(pady=10, anchor=tk.W)

        # Zoom controls
        zoom_frame = Frame(zoom_section, bg=self.bg_color)
        zoom_frame.pack(fill=tk.X, pady=10)

        zoom_btns = Frame(zoom_frame, bg=self.bg_color)
        zoom_btns.pack(fill=tk.X, pady=5)

        zoom_in = Button(zoom_btns, text="Zoom In", command=lambda: self.zoom(1.25),
                        width=9, bg=self.bg_color, activebackground=self.highlight_color,
                        font=self.normal_font)
        zoom_in.pack(side=tk.LEFT, padx=2)
        self.create_tooltip(zoom_in, "Zoom in on the image")

        zoom_out = Button(zoom_btns, text="Zoom Out", command=lambda: self.zoom(0.8),
                         width=9, bg=self.bg_color, activebackground=self.highlight_color,
                         font=self.normal_font)
        zoom_out.pack(side=tk.RIGHT, padx=2)
        self.create_tooltip(zoom_out, "Zoom out from the image")

        reset_view = Button(zoom_frame, text="Reset View", command=self.reset_view,
                           width=20, bg=self.bg_color, activebackground=self.highlight_color,
                           font=self.normal_font)
        reset_view.pack(pady=5)
        self.create_tooltip(reset_view, "Reset zoom and pan to default")

    def _on_mousewheel(self, event, canvas):
        """Handle mousewheel scrolling on a canvas"""
        # Only scroll if mouse is over the canvas
        x, y = canvas.winfo_pointerxy()
        widget_under_mouse = canvas.winfo_containing(x, y)
        if widget_under_mouse and (widget_under_mouse == canvas or
                                  canvas.winfo_ismapped() and
                                  widget_under_mouse.winfo_toplevel() == canvas.winfo_toplevel()):
            # Scroll direction depends on platform
            if hasattr(event, 'delta'):
                # Windows platform
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif hasattr(event, 'num'):
                # Unix platform
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")

    def setup_control_panel(self):
        # Setup each tab with its controls
        self.setup_file_tab()
        self.setup_adjust_tab()
        self.setup_filter_tab()  # Add filter tab setup
        self.setup_transform_tab()
        self.setup_advanced_tab()

    def setup_file_tab(self):
        """Setup the File tab with file operations and history controls"""
        # File Operations Section
        file_section = Frame(self.file_frame, bg=self.bg_color)
        file_section.pack(fill=tk.X, padx=5, pady=5)

        # Section header with animation
        header_frame = Frame(file_section, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=10)

        header = Label(header_frame, text="File Operations", font=self.header_font,
                      bg=self.bg_color, fg=self.accent_color)
        header.pack(side=tk.LEFT, anchor=tk.W)

        # Add a small animated icon next to the header
        self.file_icon_index = 0
        self.file_icons = ["📁", "📂", "📄", "📝"]
        self.file_icon_label = Label(header_frame, text=self.file_icons[0], font=("Segoe UI Emoji", 18),
                                    bg=self.bg_color, fg=self.accent_color)
        self.file_icon_label.pack(side=tk.LEFT, padx=10)
        self.animate_file_icon()

        # File operation buttons with modern styling and animations
        file_btns = Frame(file_section, bg=self.bg_color)
        file_btns.pack(fill=tk.X, pady=10)

        # Open button with icon and animation
        open_btn = self.create_modern_button(file_btns, text="Open Image", command=self.load_image,
                                          width=12, icon="📂", is_important=True,
                                          bg=self.secondary_color)
        open_btn.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(open_btn, "Open an image file (Ctrl+O)")

        # Save button with icon and animation
        save_btn = self.create_modern_button(file_btns, text="Save Image", command=self.save_image,
                                          width=12, icon="💾", is_important=True,
                                          bg=self.accent_color)
        save_btn.pack(side=tk.RIGHT, padx=5)
        self.create_tooltip(save_btn, "Save the processed image (Ctrl+S)")

        # Export options with card-style background
        export_frame = Frame(file_section, bg=self.card_bg, bd=1, relief=tk.RAISED, padx=10, pady=10)
        export_frame.pack(fill=tk.X, pady=10)

        # Add a subtle gradient effect to the export frame
        gradient_canvas = Canvas(export_frame, height=5, bg=self.card_bg, highlightthickness=0)
        gradient_canvas.pack(fill=tk.X, side=tk.TOP)

        # Create gradient
        for i in range(100):
            # Calculate gradient color
            r = int(int(self.accent_color[1:3], 16) * (1 - i/100) + int(self.card_bg[1:3], 16) * (i/100))
            g = int(int(self.accent_color[3:5], 16) * (1 - i/100) + int(self.card_bg[3:5], 16) * (i/100))
            b = int(int(self.accent_color[5:7], 16) * (1 - i/100) + int(self.card_bg[5:7], 16) * (i/100))
            color = f"#{r:02x}{g:02x}{b:02x}"
            gradient_canvas.create_line(i*5, 0, i*5, 5, fill=color)

        Label(export_frame, text="Export Options", font=self.subheader_font,
             bg=self.card_bg, fg=self.text_color).pack(pady=5, anchor=tk.W)

        # Export buttons with icons and animations
        export_btn = self.create_modern_button(export_frame, text="Export As...", command=self.export_image,
                                            width=15, icon="📤", is_important=False,
                                            bg=self.secondary_color)
        export_btn.pack(pady=5)
        self.create_tooltip(export_btn, "Export the image with custom settings")

        # Social Media Export button with icon and animation
        social_btn = self.create_modern_button(export_frame, text="Social Media Export", command=self.social_media_export,
                                             width=15, icon="🔥", is_important=True,
                                             bg=self.accent_color)
        social_btn.pack(pady=5)
        self.create_tooltip(social_btn, "Export image optimized for social media platforms")

        # History controls
        history_frame = Frame(file_section, bg=self.bg_color)
        history_frame.pack(fill=tk.X, pady=10)

        # History section header
        history_header = Label(history_frame, text="History", font=self.subheader_font,
                             bg=self.bg_color, fg=self.text_color)
        history_header.pack(pady=5, anchor=tk.W)

        # History buttons
        history_btns = Frame(history_frame, bg=self.bg_color)
        history_btns.pack(fill=tk.X, pady=5)

        undo_btn = Button(history_btns, text="Undo", command=self.undo, width=9,
                         bg=self.bg_color, activebackground=self.highlight_color, font=self.normal_font)
        undo_btn.pack(side=tk.LEFT, padx=2)
        self.create_tooltip(undo_btn, "Undo last action (Ctrl+Z)")

        redo_btn = Button(history_btns, text="Redo", command=self.redo, width=9,
                         bg=self.bg_color, activebackground=self.highlight_color, font=self.normal_font)
        redo_btn.pack(side=tk.RIGHT, padx=2)
        self.create_tooltip(redo_btn, "Redo last undone action (Ctrl+Y)")

        # Real-time preview toggle
        preview_frame = Frame(file_section, bg=self.bg_color)
        preview_frame.pack(fill=tk.X, pady=10)

        preview_header = Label(preview_frame, text="Preview Options", font=self.subheader_font,
                              bg=self.bg_color, fg=self.text_color)
        preview_header.pack(pady=5, anchor=tk.W)

        self.preview_var = tk.BooleanVar(value=True)
        preview_check = Checkbutton(preview_frame, text="Real-time Preview",
                                  variable=self.preview_var,
                                  command=self.toggle_preview,
                                  bg=self.bg_color, font=self.normal_font)
        preview_check.pack(pady=5, anchor=tk.W)
        self.preview_var.set(self.real_time_preview)
        self.create_tooltip(preview_check, "Toggle real-time updates as you adjust settings")

        # Reset button
        reset_btn = Button(file_section, text="Reset All", command=self.reset_adjustments,
                          width=20, bg="#e74c3c", fg="white",
                          activebackground="#c0392b", font=self.normal_font)
        reset_btn.pack(pady=15)
        self.create_tooltip(reset_btn, "Reset all adjustments to default (Ctrl+R)")

        # Basic adjustments have been moved to the adjust tab

        # Color adjustments have been moved to the adjust tab

        # Transformations have been moved to the transform tab

        # Filters have been moved to the filter tab

        # Zoom and Pan have been moved to the advanced tab

        # Layer support has been removed

        # Resize has been moved to the transform tab



        # Reset button has been moved to the file tab

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp")]
        )

        if file_path:
            self.load_image_from_path(file_path)

    def load_image_from_path(self, file_path):
        """Load an image from the given file path and apply all necessary operations"""
        try:
            # Load the image
            self.original_image = Image.open(file_path)

            # Convert to RGB mode if needed (for proper display)
            if self.original_image.mode != 'RGB':
                self.original_image = self.original_image.convert('RGB')

            # Reset zoom and pan
            self.zoom_factor = 1.0
            self.pan_x = 0
            self.pan_y = 0

            # Reset adjustments to default values
            self.reset_adjustments(update_image=False)

            # Store the file path for reference
            self.current_file_path = file_path

            # Display the original image
            self.display_image(self.original_image, self.original_canvas)

            # Create initial processed image
            self.processed_image = self.original_image.copy()

            # Apply any default operations
            self.apply_default_operations()

            # Apply current adjustments and filters with force flag
            self.update_image("force")

            # Make sure both images are displayed
            self.update_display_image()

            # Show image information
            self.show_image_info()

            # Update resize dimensions with current image size
            self.update_resize_dimensions()

            # Reset history and add initial state
            self.history = []
            self.history_position = -1
            self.add_to_history()

            # Update file info in status bar
            self.status_bar.config(text=f"Loaded: {os.path.basename(file_path)}")

            # Ensure the notebook shows the image tab
            self.notebook.select(0)  # Select the first tab (Image)

            # Update UI elements to reflect current state
            self.update_ui_state()

            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error loading image: {str(e)}")
            self.status_bar.config(text=f"Error loading image: {str(e)}")
            return False

    def show_image_info(self):
        """Display information about the loaded image"""
        if self.original_image:
            info = get_image_info(self.original_image)
            info_text = f"Size: {info['width']}x{info['height']} pixels | Mode: {info['mode']} | Format: {info['format']}"
            if info['size_kb']:
                info_text += f" | File size: {info['size_kb']:.1f} KB"

            # Update status bar with image info
            self.status_bar.config(text=info_text)

    def update_image(self, *args):
        if not self.original_image:
            return

        # Skip processing if real-time preview is off (unless forced)
        if not self.real_time_preview and args and args[0] != "force":
            return

        # Get current adjustment values
        brightness = self.brightness_slider.get()
        contrast = self.contrast_slider.get()
        saturation = self.saturation_slider.get()
        hue = self.hue_slider.get()

        # Check if any adjustments have changed to avoid unnecessary processing
        adjustments_changed = (
            brightness != self.current_brightness or
            contrast != self.current_contrast or
            saturation != self.current_saturation or
            hue != self.current_hue or
            args and args[0] == "force"
        )

        if not adjustments_changed and not args:
            return

        # Update current values
        self.current_brightness = brightness
        self.current_contrast = contrast
        self.current_saturation = saturation
        self.current_hue = hue

        # Start with the original image - avoid copy if possible
        img = self.original_image.copy()

        # Apply adjustments in sequence
        # 1. Brightness and contrast
        img = adjust_brightness_contrast(img, self.current_brightness, self.current_contrast)

        # 2. Saturation - only apply if needed
        if self.current_saturation != 1.0:
            img = adjust_saturation(img, self.current_saturation)

        # 3. Hue - only apply if needed
        if self.current_hue != 0:
            img = adjust_hue(img, self.current_hue)

        # Apply filter if selected
        current_filter = self.current_filter.get()
        intensity = self.filter_intensity.get()

        if current_filter != "none":
            # Apply the selected filter based on its name
            if current_filter == "grayscale":
                img = img.convert('L').convert('RGB')
            elif current_filter == "sepia":
                img = apply_sepia(img)
            elif current_filter == "invert":
                img = ImageOps.invert(img)
            elif current_filter == "brightness":
                img = adjust_brightness_contrast(img, 50 * intensity, self.current_contrast)
            elif current_filter == "contrast":
                img = adjust_brightness_contrast(img, self.current_brightness, 1.0 + intensity)
            elif current_filter == "saturation":
                img = adjust_saturation(img, 1.0 + intensity)
            elif current_filter == "gaussian_blur":
                img = img.filter(ImageFilter.GaussianBlur(radius=intensity * 5))
            elif current_filter == "median_blur":
                img = img.filter(ImageFilter.MedianFilter(size=int(intensity * 5)))
            elif current_filter == "sharpen":
                img = img.filter(ImageFilter.SHARPEN)
                if intensity > 1.0:
                    for _ in range(int(intensity)):
                        img = img.filter(ImageFilter.SHARPEN)
            elif current_filter == "edge_detection":
                img = img.filter(ImageFilter.FIND_EDGES)
            elif current_filter == "emboss":
                img = img.filter(ImageFilter.EMBOSS)
            elif current_filter == "threshold":
                # Convert to grayscale first
                gray = img.convert('L')
                # Apply threshold
                threshold = int(128 * intensity)
                img = gray.point(lambda x: 255 if x > threshold else 0).convert('RGB')
            elif current_filter == "histogram_eq":
                # Apply histogram equalization with intensity based on the slider
                img = apply_histogram_equalization(img, intensity)
            elif current_filter == "color_balance":
                # Simple color balance by adjusting RGB channels
                r, g, b = img.split()
                r = ImageOps.autocontrast(r, cutoff=intensity * 10)
                g = ImageOps.autocontrast(g, cutoff=intensity * 10)
                b = ImageOps.autocontrast(b, cutoff=intensity * 10)
                img = Image.merge('RGB', (r, g, b))
            elif current_filter == "vignette":
                # Create vignette effect
                width, height = img.size
                mask = Image.new('L', (width, height), 0)
                draw = ImageDraw.Draw(mask)
                # Draw a gradient ellipse from center (255) to edges (0)
                for i in range(min(width, height) // 2, 0, -1):
                    # Calculate opacity based on distance from center
                    opacity = int(255 * (i / (min(width, height) // 2)))
                    draw.ellipse(
                        [(width//2 - i, height//2 - i), (width//2 + i, height//2 + i)],
                        fill=opacity
                    )
                # Apply the mask
                img = Image.composite(img, Image.new('RGB', img.size, (30, 20, 10)), mask)
            elif current_filter == "cartoonify":
                # Cartoonify effect
                # 1. Apply edge detection
                edges = img.filter(ImageFilter.FIND_EDGES)
                # 2. Convert to grayscale and invert
                edges = ImageOps.invert(edges.convert('L'))
                # 3. Posterize the original image
                color = ImageOps.posterize(img, 4)
                # 4. Combine edges with color
                img = ImageChops.multiply(color, edges.convert('RGB'))
            elif current_filter == "oil_painting":
                # Oil painting effect (simplified)
                img = img.filter(ImageFilter.ModeFilter(size=int(intensity * 5)))
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.5)
            elif current_filter == "pencil_sketch":
                # Use the enhanced pencil sketch function from image_utils
                img = apply_pencil_sketch(img, intensity)
            elif current_filter == "erosion":
                # Erosion (simplified using min filter)
                img = img.filter(ImageFilter.MinFilter(size=int(intensity * 5)))
            elif current_filter == "dilation":
                # Dilation (simplified using max filter)
                img = img.filter(ImageFilter.MaxFilter(size=int(intensity * 5)))
            elif current_filter == "opening":
                # Opening (erosion followed by dilation)
                img = img.filter(ImageFilter.MinFilter(size=int(intensity * 5)))
                img = img.filter(ImageFilter.MaxFilter(size=int(intensity * 5)))
            elif current_filter == "closing":
                # Closing (dilation followed by erosion)
                img = img.filter(ImageFilter.MaxFilter(size=int(intensity * 5)))
                img = img.filter(ImageFilter.MinFilter(size=int(intensity * 5)))

            # Update processed image
            self.processed_image = img

            # Update both original and processed image displays
            self.update_display_image()

            # Update status bar
            self.status_bar.config(
                text=f"Brightness: {self.current_brightness}, Contrast: {self.current_contrast}, "
                     f"Saturation: {self.current_saturation}, Hue: {self.current_hue}, "
                     f"Filter: {self.current_filter}, Zoom: {self.zoom_factor:.1f}x"
            )

            # Add to history (but not during history navigation or initial load)
            if args and args[0] != "history":
                self.add_to_history()

    def display_image(self, image, canvas):
        # Resize image to fit canvas while maintaining aspect ratio
        display_image = image.copy()

        # Calculate new dimensions
        max_width = 450
        max_height = 500
        width, height = display_image.size

        # Apply zoom factor
        zoomed_width = int(width * self.zoom_factor)
        zoomed_height = int(height * self.zoom_factor)

        # Resize with zoom factor
        if zoomed_width > 0 and zoomed_height > 0:  # Prevent zero dimensions
            display_image = display_image.resize((zoomed_width, zoomed_height), Image.LANCZOS)

        # Apply pan (crop to visible area)
        if self.zoom_factor > 1.0:
            # Calculate visible area
            visible_width = min(zoomed_width, max_width)
            visible_height = min(zoomed_height, max_height)

            # Calculate crop coordinates with pan offsets
            left = max(0, min(self.pan_x, zoomed_width - visible_width))
            top = max(0, min(self.pan_y, zoomed_height - visible_height))
            right = min(left + visible_width, zoomed_width)
            bottom = min(top + visible_height, zoomed_height)

            # Crop to visible area
            if right > left and bottom > top:  # Ensure valid crop area
                display_image = display_image.crop((left, top, right, bottom))

        # Final resize to fit canvas if needed
        width, height = display_image.size
        if width > max_width or height > max_height:
            ratio = min(max_width/width, max_height/height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            display_image = display_image.resize((new_width, new_height), Image.LANCZOS)

        # Convert to PhotoImage and display
        photo = ImageTk.PhotoImage(display_image)
        canvas.config(image=photo)
        canvas.image = photo  # Keep a reference to prevent garbage collection

    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        # We'll use a simpler approach that doesn't require external libraries
        # Just inform the user that they can use the File menu instead
        self.status_bar.config(text="Tip: Use File > Open to load images or the Save button to export in different formats")

    # This method is no longer used but kept for reference
    def on_drop(self, _):
        """Handle file drop event"""
        pass

    def save_image(self):
        if self.processed_image:
            # Create a dialog with format options
            formats = [
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("BMP files", "*.bmp"),
                ("GIF files", "*.gif"),
                ("TIFF files", "*.tiff"),
                ("WebP files", "*.webp"),
                ("All files", "*.*")
            ]

            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=formats
            )

            if file_path:
                try:
                    # Get the file extension to determine format
                    _, ext = os.path.splitext(file_path)
                    ext = ext.lower()

                    # Handle JPEG quality
                    if ext in ('.jpg', '.jpeg'):
                        self.processed_image.save(file_path, quality=95)
                    else:
                        self.processed_image.save(file_path)

                    self.status_bar.config(text=f"Saved: {os.path.basename(file_path)}")
                except Exception as e:
                    self.status_bar.config(text=f"Error saving image: {str(e)}")

    def export_image(self):
        """Export the image with custom settings"""
        if not self.processed_image:
            messagebox.showinfo("No Image", "Please open an image first.")
            return

        # Create a dialog for export options
        export_dialog = tk.Toplevel(self.root)
        export_dialog.title("Export Image")
        export_dialog.geometry("400x500")
        export_dialog.configure(bg=self.bg_color)
        export_dialog.transient(self.root)  # Set as transient to main window
        export_dialog.grab_set()  # Make dialog modal

        # Add a header
        header_frame = Frame(export_dialog, bg=self.accent_color, padx=10, pady=10)
        header_frame.pack(fill=tk.X)

        Label(header_frame, text="Export Image", font=self.header_font, bg=self.accent_color, fg="white").pack()

        # Content frame
        content_frame = Frame(export_dialog, bg=self.bg_color, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # File format selection
        format_frame = Frame(content_frame, bg=self.bg_color)
        format_frame.pack(fill=tk.X, pady=10)

        Label(format_frame, text="File Format:", font=self.subheader_font, bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)

        format_var = StringVar(value="PNG")
        formats = ["PNG", "JPEG", "BMP", "TIFF", "WEBP"]

        format_frame_inner = Frame(format_frame, bg=self.bg_color)
        format_frame_inner.pack(fill=tk.X, pady=5)

        for i, fmt in enumerate(formats):
            rb = Radiobutton(format_frame_inner, text=fmt, variable=format_var, value=fmt,
                           bg=self.bg_color, font=self.normal_font,
                           activebackground=self.highlight_color)
            rb.grid(row=0, column=i, padx=10)

        # Quality setting (for JPEG and WEBP)
        quality_frame = Frame(content_frame, bg=self.bg_color)
        quality_frame.pack(fill=tk.X, pady=10)

        Label(quality_frame, text="Quality (for JPEG/WEBP):", font=self.subheader_font,
             bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)

        quality_var = IntVar(value=90)
        quality_scale = Scale(quality_frame, from_=1, to=100, orient=tk.HORIZONTAL,
                            variable=quality_var, length=350,
                            bg=self.bg_color, highlightthickness=0,
                            troughcolor=self.highlight_color, activebackground=self.accent_color)
        quality_scale.pack(fill=tk.X, pady=5)

        # Size options
        size_frame = Frame(content_frame, bg=self.bg_color)
        size_frame.pack(fill=tk.X, pady=10)

        Label(size_frame, text="Resize Options:", font=self.subheader_font,
             bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)

        size_var = StringVar(value="original")
        Radiobutton(size_frame, text="Original Size", variable=size_var, value="original",
                   bg=self.bg_color, font=self.normal_font).pack(anchor=tk.W)

        custom_size_frame = Frame(size_frame, bg=self.bg_color)
        custom_size_frame.pack(fill=tk.X, pady=5)

        Radiobutton(custom_size_frame, text="Custom Size:", variable=size_var, value="custom",
                   bg=self.bg_color, font=self.normal_font).pack(side=tk.LEFT)

        width_var = StringVar()
        height_var = StringVar()

        # Set initial values if we have an image
        if self.processed_image:
            width, height = self.processed_image.size
            width_var.set(str(width))
            height_var.set(str(height))

        width_entry = Entry(custom_size_frame, textvariable=width_var, width=5)
        width_entry.pack(side=tk.LEFT, padx=5)

        Label(custom_size_frame, text="×", bg=self.bg_color).pack(side=tk.LEFT)

        height_entry = Entry(custom_size_frame, textvariable=height_var, width=5)
        height_entry.pack(side=tk.LEFT, padx=5)

        Label(custom_size_frame, text="pixels", bg=self.bg_color).pack(side=tk.LEFT, padx=5)

        # Buttons
        button_frame = Frame(content_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=20)

        def do_export():
            # Get the file path to save
            file_format = format_var.get().lower()
            file_ext = f".{file_format}"
            if file_format == "jpeg":
                file_ext = ".jpg"

            file_path = filedialog.asksaveasfilename(
                defaultextension=file_ext,
                filetypes=[(f"{format_var.get()} files", f"*{file_ext}")]
            )

            if not file_path:
                return  # User cancelled

            try:
                # Get a copy of the processed image
                img_to_save = self.processed_image.copy()

                # Resize if needed
                if size_var.get() == "custom":
                    try:
                        new_width = int(width_var.get())
                        new_height = int(height_var.get())
                        if new_width > 0 and new_height > 0:
                            img_to_save = img_to_save.resize((new_width, new_height), Image.LANCZOS)
                    except ValueError:
                        messagebox.showerror("Invalid Size", "Please enter valid width and height values.")
                        return

                # Save with appropriate options
                if file_format in ["jpeg", "webp"]:
                    img_to_save.save(file_path, quality=quality_var.get())
                else:
                    img_to_save.save(file_path)

                messagebox.showinfo("Export Successful", f"Image exported successfully to:\n{file_path}")
                export_dialog.destroy()

            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting image: {str(e)}")

        # Cancel button
        cancel_btn = Button(button_frame, text="Cancel", command=export_dialog.destroy,
                          width=10, bg=self.bg_color, font=self.normal_font)
        cancel_btn.pack(side=tk.LEFT, padx=10)

        # Export button
        export_btn = Button(button_frame, text="Export", command=do_export,
                          width=10, bg=self.accent_color, fg="white", font=self.normal_font)
        export_btn.pack(side=tk.RIGHT, padx=10)

    def social_media_export(self):
        """Export image optimized for social media platforms"""
        if not self.processed_image:
            messagebox.showinfo("No Image", "No image to export. Please load an image first.")
            return

        # Create a new toplevel window for the social media export dialog
        export_dialog = tk.Toplevel(self.root)
        export_dialog.title("Export for Social Media")
        export_dialog.geometry("500x600")
        export_dialog.configure(bg=self.bg_color)
        export_dialog.resizable(True, True)  # Allow resizing
        export_dialog.transient(self.root)  # Set as transient to main window
        export_dialog.grab_set()  # Make dialog modal

        # Button frame - this should be outside the scrollable area
        # Create a separate frame at the bottom of the dialog for buttons
        button_frame = Frame(export_dialog, bg=self.bg_color, padx=20, pady=15)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Create a main frame that will contain everything else
        main_container = Frame(export_dialog, bg=self.bg_color)
        main_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create a canvas for scrolling
        canvas = Canvas(main_container, bg=self.bg_color, highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas
        scrollbar = Scrollbar(main_container, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to use the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas for all content
        content_frame = Frame(canvas, bg=self.bg_color)
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor=tk.NW, tags="content_frame")

        # Configure the canvas to update its scroll region when the content frame changes size
        def update_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        # Bind the update function to the content frame's size changes
        content_frame.bind("<Configure>", update_scrollregion)

        # Make the canvas expand to fill available space
        export_dialog.grid_rowconfigure(0, weight=1)
        export_dialog.grid_columnconfigure(0, weight=1)

        # Add a header
        header_frame = Frame(content_frame, bg=self.bg_color, pady=10)
        header_frame.pack(fill=tk.X)

        Label(header_frame, text="Export Image for Social Media",
              font=self.header_font, bg=self.bg_color, fg=self.accent_color).pack()

        # Create a frame for the platform selection
        platform_frame = Frame(content_frame, bg=self.bg_color, padx=20, pady=10)
        platform_frame.pack(fill=tk.X)

        Label(platform_frame, text="Select Platform:",
              font=self.subheader_font, bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)

        # Define social media platforms and their optimal image sizes
        platforms = {
            "Instagram Post": {"size": (1080, 1080), "format": "jpg", "quality": 90, "description": "Square post (1:1)"},
            "Instagram Story": {"size": (1080, 1920), "format": "jpg", "quality": 90, "description": "Vertical (9:16)"},
            "Facebook Post": {"size": (1200, 630), "format": "jpg", "quality": 85, "description": "Rectangular post (1.91:1)"},
            "Facebook Cover": {"size": (851, 315), "format": "jpg", "quality": 85, "description": "Cover photo"},
            "Twitter Post": {"size": (1200, 675), "format": "jpg", "quality": 85, "description": "In-stream photo (16:9)"},
            "Twitter Header": {"size": (1500, 500), "format": "jpg", "quality": 85, "description": "Header image"},
            "LinkedIn Post": {"size": (1200, 627), "format": "jpg", "quality": 85, "description": "Standard post"},
            "LinkedIn Cover": {"size": (1584, 396), "format": "jpg", "quality": 85, "description": "Company page cover"},
            "Pinterest Pin": {"size": (1000, 1500), "format": "jpg", "quality": 85, "description": "Vertical pin (2:3)"},
            "YouTube Thumbnail": {"size": (1280, 720), "format": "jpg", "quality": 90, "description": "Video thumbnail (16:9)"},
            "TikTok Video": {"size": (1080, 1920), "format": "jpg", "quality": 90, "description": "Full screen vertical (9:16)"}
        }

        # Create a variable to store the selected platform
        self.selected_platform = StringVar(export_dialog)
        self.selected_platform.set(list(platforms.keys())[0])  # Default to first platform

        # Create a listbox with scrollbar for platform selection
        platform_list_frame = Frame(platform_frame, bg=self.bg_color)
        platform_list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        scrollbar = Scrollbar(platform_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        platform_listbox = tk.Listbox(platform_list_frame, height=8,
                                     font=self.normal_font, bg="white", fg=self.text_color,
                                     selectbackground=self.accent_color, selectforeground="white",
                                     yscrollcommand=scrollbar.set)

        # Add platforms to the listbox
        for platform in platforms.keys():
            platform_listbox.insert(tk.END, platform)

        platform_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=platform_listbox.yview)

        # Select the first platform by default
        platform_listbox.selection_set(0)

        # Create a frame for displaying platform details
        details_frame = Frame(content_frame, bg=self.bg_color, padx=20, pady=10)
        details_frame.pack(fill=tk.X)

        # Labels for displaying platform details
        Label(details_frame, text="Platform Details:",
              font=self.subheader_font, bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)

        details_content = Frame(details_frame, bg=self.bg_color, pady=5)
        details_content.pack(fill=tk.X)

        # Create labels for each detail
        size_label = Label(details_content, text="Size: ",
                          font=self.normal_font, bg=self.bg_color, fg=self.text_color)
        size_label.grid(row=0, column=0, sticky=tk.W, pady=2)

        self.size_value = Label(details_content, text="",
                               font=self.normal_font, bg=self.bg_color, fg=self.text_color)
        self.size_value.grid(row=0, column=1, sticky=tk.W, pady=2)

        format_label = Label(details_content, text="Format: ",
                            font=self.normal_font, bg=self.bg_color, fg=self.text_color)
        format_label.grid(row=1, column=0, sticky=tk.W, pady=2)

        self.format_value = Label(details_content, text="",
                                 font=self.normal_font, bg=self.bg_color, fg=self.text_color)
        self.format_value.grid(row=1, column=1, sticky=tk.W, pady=2)

        quality_label = Label(details_content, text="Quality: ",
                             font=self.normal_font, bg=self.bg_color, fg=self.text_color)
        quality_label.grid(row=2, column=0, sticky=tk.W, pady=2)

        self.quality_value = Label(details_content, text="",
                                  font=self.normal_font, bg=self.bg_color, fg=self.text_color)
        self.quality_value.grid(row=2, column=1, sticky=tk.W, pady=2)

        desc_label = Label(details_content, text="Description: ",
                          font=self.normal_font, bg=self.bg_color, fg=self.text_color)
        desc_label.grid(row=3, column=0, sticky=tk.W, pady=2)

        self.desc_value = Label(details_content, text="",
                               font=self.normal_font, bg=self.bg_color, fg=self.text_color)
        self.desc_value.grid(row=3, column=1, sticky=tk.W, pady=2)

        # Create a frame for export options
        options_frame = Frame(content_frame, bg=self.bg_color, padx=20, pady=10)
        options_frame.pack(fill=tk.X)

        Label(options_frame, text="Export Options:",
              font=self.subheader_font, bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)

        # Crop method options
        crop_frame = Frame(options_frame, bg=self.bg_color, pady=5)
        crop_frame.pack(fill=tk.X)

        Label(crop_frame, text="Crop Method:",
              font=self.normal_font, bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)

        crop_method = StringVar(export_dialog, value="fit")

        crop_options = Frame(crop_frame, bg=self.bg_color)
        crop_options.pack(fill=tk.X, pady=5)

        Radiobutton(crop_options, text="Fit (preserve aspect ratio)", variable=crop_method, value="fit",
                   bg=self.bg_color, font=self.normal_font).pack(anchor=tk.W)
        Radiobutton(crop_options, text="Fill (crop to fit)", variable=crop_method, value="fill",
                   bg=self.bg_color, font=self.normal_font).pack(anchor=tk.W)
        Radiobutton(crop_options, text="Stretch (ignore aspect ratio)", variable=crop_method, value="stretch",
                   bg=self.bg_color, font=self.normal_font).pack(anchor=tk.W)

        # Custom quality option
        quality_frame = Frame(options_frame, bg=self.bg_color, pady=5)
        quality_frame.pack(fill=tk.X)

        Label(quality_frame, text="Custom Quality:",
              font=self.normal_font, bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)

        quality_slider_frame = Frame(quality_frame, bg=self.bg_color)
        quality_slider_frame.pack(fill=tk.X, pady=5)

        custom_quality = IntVar(export_dialog, value=85)
        quality_slider = Scale(quality_slider_frame, from_=1, to=100, orient=tk.HORIZONTAL,
                              variable=custom_quality, length=200, bg=self.bg_color,
                              highlightthickness=0, troughcolor=self.highlight_color,
                              activebackground=self.accent_color)
        quality_slider.pack(side=tk.LEFT)

        # Preview frame
        preview_frame = Frame(content_frame, bg=self.bg_color, padx=20, pady=10)
        preview_frame.pack(fill=tk.X)

        Label(preview_frame, text="Preview:",
              font=self.subheader_font, bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)

        # Preview canvas
        preview_canvas = Label(preview_frame, bg="#222222", width=30, height=10)
        preview_canvas.pack(pady=10)

        # Function to update platform details and preview
        def update_platform_details(event=None):
            selected_idx = platform_listbox.curselection()
            if not selected_idx:
                return

            selected = platform_listbox.get(selected_idx[0])
            platform_data = platforms[selected]

            # Update detail labels
            self.size_value.config(text=f"{platform_data['size'][0]} × {platform_data['size'][1]} pixels")
            self.format_value.config(text=f"{platform_data['format'].upper()}")
            self.quality_value.config(text=f"{platform_data['quality']}%")
            self.desc_value.config(text=f"{platform_data['description']}")

            # Set quality slider to platform default
            custom_quality.set(platform_data['quality'])

            # Update preview
            if self.processed_image:
                # Create a preview of how the image will look
                preview_img = self.processed_image.copy()
                target_size = platform_data['size']

                # Apply selected crop method
                method = crop_method.get()
                if method == "fit":
                    # Resize to fit within dimensions while preserving aspect ratio
                    preview_img.thumbnail(target_size, Image.LANCZOS)
                    # Create a blank canvas of the target size
                    new_img = Image.new("RGB", target_size, (0, 0, 0))
                    # Paste the resized image in the center
                    paste_x = (target_size[0] - preview_img.width) // 2
                    paste_y = (target_size[1] - preview_img.height) // 2
                    new_img.paste(preview_img, (paste_x, paste_y))
                    preview_img = new_img
                elif method == "fill":
                    # Calculate aspect ratios
                    img_ratio = preview_img.width / preview_img.height
                    target_ratio = target_size[0] / target_size[1]

                    if img_ratio > target_ratio:
                        # Image is wider than target, crop sides
                        new_width = int(preview_img.height * target_ratio)
                        left = (preview_img.width - new_width) // 2
                        preview_img = preview_img.crop((left, 0, left + new_width, preview_img.height))
                    else:
                        # Image is taller than target, crop top/bottom
                        new_height = int(preview_img.width / target_ratio)
                        top = (preview_img.height - new_height) // 2
                        preview_img = preview_img.crop((0, top, preview_img.width, top + new_height))

                    # Resize to exact dimensions
                    preview_img = preview_img.resize(target_size, Image.LANCZOS)
                else:  # stretch
                    # Just resize to the exact dimensions, ignoring aspect ratio
                    preview_img = preview_img.resize(target_size, Image.LANCZOS)

                # Convert to PhotoImage for display
                # Resize for preview (smaller)
                preview_display_size = (300, 200)
                ratio = min(preview_display_size[0] / preview_img.width,
                           preview_display_size[1] / preview_img.height)
                display_size = (int(preview_img.width * ratio), int(preview_img.height * ratio))
                preview_display = preview_img.resize(display_size, Image.LANCZOS)

                # Convert to PhotoImage
                preview_photo = ImageTk.PhotoImage(preview_display)
                preview_canvas.config(image=preview_photo, width=display_size[0], height=display_size[1])
                preview_canvas.image = preview_photo  # Keep a reference

        # Bind the listbox selection event
        platform_listbox.bind('<<ListboxSelect>>', update_platform_details)

        # Also update when crop method changes
        for rb in crop_options.winfo_children():
            rb.config(command=update_platform_details)



        # Function to handle export
        def do_export():
            selected_idx = platform_listbox.curselection()
            if not selected_idx:
                messagebox.showinfo("Selection Required", "Please select a platform.")
                return

            selected = platform_listbox.get(selected_idx[0])
            platform_data = platforms[selected]

            # Get file path from user
            file_path = filedialog.asksaveasfilename(
                defaultextension=f".{platform_data['format']}",
                filetypes=[(f"{platform_data['format'].upper()} files", f"*.{platform_data['format']}")],
                initialfile=f"{selected.replace(' ', '_').lower()}"
            )

            if not file_path:
                return

            # Process the image according to selected options
            export_img = self.processed_image.copy()
            target_size = platform_data['size']

            # Apply selected crop method
            method = crop_method.get()
            if method == "fit":
                # Resize to fit within dimensions while preserving aspect ratio
                export_img.thumbnail(target_size, Image.LANCZOS)
                # Create a blank canvas of the target size
                new_img = Image.new("RGB", target_size, (0, 0, 0))
                # Paste the resized image in the center
                paste_x = (target_size[0] - export_img.width) // 2
                paste_y = (target_size[1] - export_img.height) // 2
                new_img.paste(export_img, (paste_x, paste_y))
                export_img = new_img
            elif method == "fill":
                # Calculate aspect ratios
                img_ratio = export_img.width / export_img.height
                target_ratio = target_size[0] / target_size[1]

                if img_ratio > target_ratio:
                    # Image is wider than target, crop sides
                    new_width = int(export_img.height * target_ratio)
                    left = (export_img.width - new_width) // 2
                    export_img = export_img.crop((left, 0, left + new_width, export_img.height))
                else:
                    # Image is taller than target, crop top/bottom
                    new_height = int(export_img.width / target_ratio)
                    top = (export_img.height - new_height) // 2
                    export_img = export_img.crop((0, top, export_img.width, top + new_height))

                # Resize to exact dimensions
                export_img = export_img.resize(target_size, Image.LANCZOS)
            else:  # stretch
                # Just resize to the exact dimensions, ignoring aspect ratio
                export_img = export_img.resize(target_size, Image.LANCZOS)

            # Save with selected quality
            quality_val = custom_quality.get()
            try:
                if platform_data['format'].lower() == 'jpg':
                    export_img.save(file_path, format='JPEG', quality=quality_val)
                elif platform_data['format'].lower() == 'png':
                    export_img.save(file_path, format='PNG')
                else:
                    export_img.save(file_path, quality=quality_val)

                self.status_bar.config(text=f"Image exported for {selected} to {file_path}")
                export_dialog.destroy()
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting image: {str(e)}")

        # Export and Cancel buttons
        Button(button_frame, text="Export", command=do_export,
               width=10, bg=self.accent_color, fg="white",
               activebackground=self.highlight_color, font=self.normal_font).pack(side=tk.RIGHT, padx=5)

        Button(button_frame, text="Cancel", command=export_dialog.destroy,
               width=10, bg=self.bg_color,
               activebackground=self.highlight_color, font=self.normal_font).pack(side=tk.RIGHT, padx=5)

        # Initialize the platform details
        update_platform_details()

    def reset_adjustments(self, update_image=True):
        """Reset all adjustments to default values

        Args:
            update_image (bool): Whether to update the image after resetting adjustments
        """
        # Reset all sliders to default values
        self.brightness_slider.set(0)
        self.contrast_slider.set(1.0)
        self.saturation_slider.set(1.0)
        self.hue_slider.set(0)

        # Reset filter settings
        self.filter_intensity.set(1.0)
        self.current_filter.set("none")

        # Reset histogram equalization
        self.histogram_eq_var.set(False)

        # Turn off crop mode
        self.crop_mode = False

        # Update the image if requested
        if update_image:
            self.update_image("force")

            # Clear history
            self.history = []
            self.history_position = -1

            # Add current state to history
            self.add_to_history()

            # Update status bar
            self.status_bar.config(text="All adjustments reset to default")

    # New methods for additional features
    def rotate_image(self, degrees):
        """Rotate the processed image by the specified degrees"""
        if self.processed_image:
            self.processed_image = rotate_image(self.processed_image, degrees)
            self.display_image(self.processed_image, self.processed_canvas)
            self.add_to_history()
            self.status_bar.config(text=f"Image rotated by {degrees} degrees")

    def flip_horizontal(self):
        """Flip the processed image horizontally"""
        if self.processed_image:
            self.processed_image = flip_image_horizontal(self.processed_image)
            self.display_image(self.processed_image, self.processed_canvas)
            self.add_to_history()
            self.status_bar.config(text="Image flipped horizontally")

    def flip_vertical(self):
        """Flip the processed image vertically"""
        if self.processed_image:
            self.processed_image = flip_image_vertical(self.processed_image)
            self.display_image(self.processed_image, self.processed_canvas)
            self.add_to_history()
            self.status_bar.config(text="Image flipped vertically")

    # Filter change handler has been removed

    def toggle_preview(self):
        """Toggle real-time preview on/off"""
        self.real_time_preview = self.preview_var.get()
        if self.real_time_preview:
            # Force update when turning preview back on
            self.update_image("force")
            self.status_bar.config(text="Real-time preview enabled")
        else:
            self.status_bar.config(text="Real-time preview disabled - use sliders and click Apply to see changes")

    def zoom(self, factor):
        """Zoom in or out by the given factor"""
        if self.processed_image:
            old_zoom = self.zoom_factor
            self.zoom_factor *= factor

            # Limit zoom range
            self.zoom_factor = max(0.1, min(5.0, self.zoom_factor))

            # Update display
            self.display_image(self.processed_image, self.processed_canvas)
            self.status_bar.config(text=f"Zoom: {self.zoom_factor:.1f}x")

    def reset_view(self):
        """Reset zoom and pan to default"""
        if self.processed_image:
            self.zoom_factor = 1.0
            self.pan_x = 0
            self.pan_y = 0
            self.display_image(self.processed_image, self.processed_canvas)
            self.status_bar.config(text="View reset to default")

    # Layer functionality has been removed

    def update_resize_dimensions(self):
        """Update resize input fields with current image dimensions"""
        if self.original_image:
            width, height = self.original_image.size

            # Update current size label
            self.current_size_label.config(text=f"Current size: {width} × {height} pixels")

            # Update dimension entries
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(width))

            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(height))

            # Reset percentage to 100%
            self.percentage_entry.delete(0, tk.END)
            self.percentage_entry.insert(0, "100")

            # Update new size label
            self.new_size_label.config(text=f"New size: {width} × {height} pixels")

            # Update file size estimate
            self.update_file_size_estimate(width, height)

    def toggle_resize_method(self):
        """Switch between pixel and percentage resize methods"""
        method = self.resize_method.get()

        if method == "pixels":
            self.percentage_frame.pack_forget()
            self.pixel_frame.pack(fill=tk.X, pady=5)
        else:  # percentage
            self.pixel_frame.pack_forget()
            self.percentage_frame.pack(fill=tk.X, pady=5)

        # Update preview
        self.update_resize_preview()

    def update_linked_dimensions(self, *_):
        """Update height when width changes or vice versa, maintaining aspect ratio"""
        if not self.original_image or not self.keep_aspect_var.get():
            return

        # Get original dimensions
        orig_width, orig_height = self.original_image.size
        aspect_ratio = orig_width / orig_height

        method = self.resize_method.get()

        if method == "pixels":
            # Check which dimension was last modified
            try:
                # Try to update height based on width
                width = int(self.width_entry.get())
                if width > 0:
                    new_height = int(width / aspect_ratio)
                    self.height_entry.delete(0, tk.END)
                    self.height_entry.insert(0, str(new_height))
            except ValueError:
                # If width is invalid, try to update width based on height
                try:
                    height = int(self.height_entry.get())
                    if height > 0:
                        new_width = int(height * aspect_ratio)
                        self.width_entry.delete(0, tk.END)
                        self.width_entry.insert(0, str(new_width))
                except ValueError:
                    pass

        # Update preview
        self.update_resize_preview()

    def animate_file_icon(self):
        """Animate the file icon in the file tab header"""
        self.file_icon_index = (self.file_icon_index + 1) % len(self.file_icons)
        self.file_icon_label.config(text=self.file_icons[self.file_icon_index])
        self.root.after(1000, self.animate_file_icon)  # Change icon every second

    def update_file_size_estimate(self, width, height):
        """Estimate file size based on dimensions and color depth"""
        if not self.original_image:
            return

        # Simple estimation based on dimensions and color depth
        # Actual file size will vary based on format and compression
        color_depth = 3  # RGB (3 bytes per pixel)
        if self.original_image.mode == 'RGBA':
            color_depth = 4  # RGBA (4 bytes per pixel)

        # Calculate raw size in bytes
        raw_size = width * height * color_depth

        # Convert to appropriate unit
        if raw_size < 1024:
            size_str = f"{raw_size} bytes"
        elif raw_size < 1024 * 1024:
            size_str = f"{raw_size/1024:.1f} KB"
        else:
            size_str = f"{raw_size/(1024*1024):.1f} MB"

        self.file_size_label.config(text=f"Estimated file size: {size_str}")

    def update_resize_preview(self):
        """Update the preview information for resize"""
        if not self.original_image:
            return

        try:
            orig_width, orig_height = self.original_image.size
            new_width, new_height = orig_width, orig_height

            method = self.resize_method.get()

            if method == "pixels":
                # Get dimensions from pixel entries
                new_width = int(self.width_entry.get())
                new_height = int(self.height_entry.get())
            else:  # percentage
                # Get percentage and calculate new dimensions
                percentage = float(self.percentage_entry.get())
                scale_factor = percentage / 100.0
                new_width = int(orig_width * scale_factor)
                new_height = int(orig_height * scale_factor)

            # Update new size label
            self.new_size_label.config(text=f"New size: {new_width} × {new_height} pixels")

            # Update file size estimate
            self.update_file_size_estimate(new_width, new_height)

        except (ValueError, ZeroDivisionError):
            self.new_size_label.config(text="New size: Invalid dimensions")
            self.file_size_label.config(text="Estimated file size: -")

    def preview_resize(self):
        """Show a preview of the resized image"""
        if not self.processed_image:
            return

        try:
            # Get dimensions based on method
            method = self.resize_method.get()
            keep_aspect = self.keep_aspect_var.get()

            if method == "pixels":
                # Get dimensions from pixel entries
                width = int(self.width_entry.get())
                height = int(self.height_entry.get())

                # Validate dimensions
                if width <= 0 or height <= 0:
                    self.status_bar.config(text="Invalid dimensions: Width and height must be positive")
                    return

                # Create preview
                preview_image = resize_image(self.processed_image, width, height, keep_aspect)

            else:  # percentage
                # Get percentage
                percentage = float(self.percentage_entry.get())

                # Validate percentage
                if percentage <= 0:
                    self.status_bar.config(text="Invalid percentage: Must be positive")
                    return

                # Create preview
                preview_image = resize_by_percentage(self.processed_image, percentage)

            # Display preview
            self.display_image(preview_image, self.processed_canvas)

            # Update status
            new_width, new_height = preview_image.size
            self.status_bar.config(text=f"Preview: {new_width}×{new_height} pixels (click Apply to save changes)")

            # Update new size label
            self.new_size_label.config(text=f"New size: {new_width} × {new_height} pixels")

            # Update file size estimate
            self.update_file_size_estimate(new_width, new_height)

        except ValueError:
            self.status_bar.config(text="Invalid dimensions: Please enter numeric values")

    def apply_resize(self):
        """Apply resize to the image"""
        if not self.processed_image:
            return

        try:
            # Get dimensions based on method
            method = self.resize_method.get()
            keep_aspect = self.keep_aspect_var.get()

            if method == "pixels":
                # Get dimensions from pixel entries
                width = int(self.width_entry.get())
                height = int(self.height_entry.get())

                # Validate dimensions
                if width <= 0 or height <= 0:
                    self.status_bar.config(text="Invalid dimensions: Width and height must be positive")
                    return

                # Resize the image
                self.processed_image = resize_image(self.processed_image, width, height, keep_aspect)

            else:  # percentage
                # Get percentage
                percentage = float(self.percentage_entry.get())

                # Validate percentage
                if percentage <= 0:
                    self.status_bar.config(text="Invalid percentage: Must be positive")
                    return

                # Resize the image
                self.processed_image = resize_by_percentage(self.processed_image, percentage)

            # Update display
            self.display_image(self.processed_image, self.processed_canvas)
            self.add_to_history()

            # Update status
            new_width, new_height = self.processed_image.size
            self.status_bar.config(text=f"Image resized to {new_width}×{new_height} pixels")

            # Update new size label
            self.new_size_label.config(text=f"New size: {new_width} × {new_height} pixels")

            # Update file size estimate
            self.update_file_size_estimate(new_width, new_height)

        except ValueError:
            self.status_bar.config(text="Invalid dimensions: Please enter numeric values")



    # This duplicate method has been removed

    # Crop functionality
    def toggle_crop_mode(self):
        """Toggle crop mode on/off"""
        self.crop_mode = not self.crop_mode
        if self.crop_mode:
            self.status_bar.config(text="Crop mode active: Click and drag on the image to select crop area")
        else:
            self.status_bar.config(text="Crop mode deactivated")

    def on_mouse_down(self, event):
        """Handle mouse button press"""
        if self.crop_mode and self.processed_image:
            # Get the canvas coordinates
            self.crop_start_x = event.x
            self.crop_start_y = event.y

    def on_mouse_drag(self, event):
        """Handle mouse drag"""
        if self.crop_mode and self.processed_image:
            # Update end coordinates
            self.crop_end_x = event.x
            self.crop_end_y = event.y

            # Show crop rectangle (this would be better with a proper canvas)
            self.status_bar.config(
                text=f"Crop selection: ({self.crop_start_x}, {self.crop_start_y}) to ({self.crop_end_x}, {self.crop_end_y})"
            )

    def on_mouse_up(self, event):
        """Handle mouse button release"""
        if self.crop_mode and self.processed_image:
            # Finalize end coordinates
            self.crop_end_x = event.x
            self.crop_end_y = event.y

            # Convert canvas coordinates to image coordinates
            # This is a simplified approach - in a real app, you'd need to account for scaling
            img_width, img_height = self.processed_image.size
            canvas_width = self.processed_canvas.winfo_width()
            canvas_height = self.processed_canvas.winfo_height()

            # Scale factors
            scale_x = img_width / canvas_width
            scale_y = img_height / canvas_height

            # Convert to image coordinates
            img_start_x = int(self.crop_start_x * scale_x)
            img_start_y = int(self.crop_start_y * scale_y)
            img_end_x = int(self.crop_end_x * scale_x)
            img_end_y = int(self.crop_end_y * scale_y)

            # Ensure start < end
            if img_start_x > img_end_x:
                img_start_x, img_end_x = img_end_x, img_start_x
            if img_start_y > img_end_y:
                img_start_y, img_end_y = img_end_y, img_start_y
            # Apply crop
            self.processed_image = crop_image(
                self.processed_image, img_start_x, img_start_y, img_end_x, img_end_y
            )

            # Add to history
            self.add_to_history()
            self.status_bar.config(text="Image cropped")

            # Exit crop mode
            self.crop_mode = False
            self.update_image()

    def update_display_image(self):
        """Update the displayed images (both original and processed)"""
        if not self.processed_image or not self.original_image:
            return

        # Display the original image
        self.display_image(self.original_image, self.original_canvas)

        # Display the processed image
        display_img = self.processed_image.copy()
        self.display_image(display_img, self.processed_canvas)

    def apply_default_operations(self):
        """Apply any default operations to a newly loaded image"""
        if not self.processed_image:
            return

        # Apply any default operations here
        # For example, auto-enhance, auto-contrast, etc.
        # Currently just a placeholder for future enhancements
        pass

    def update_ui_state(self):
        """Update UI elements to reflect the current state of the application"""
        if not self.processed_image:
            return

        # Update filter display
        current_filter = self.current_filter.get()
        if current_filter and current_filter != "none":
            filter_display_name = current_filter.replace("_", " ").title()
            self.current_filter_label.config(text=f"Current Filter: {filter_display_name}")
        else:
            self.current_filter_label.config(text="No filter selected")

        # Update adjustment displays
        brightness_value = self.brightness_slider.get()
        contrast_value = self.contrast_slider.get()
        saturation_value = self.saturation_slider.get()
        hue_value = self.hue_slider.get()

        # Update status bar with current values
        self.status_bar.config(
            text=f"Brightness: {brightness_value}, Contrast: {contrast_value}, "
                 f"Saturation: {saturation_value}, Hue: {hue_value}, "
                 f"Filter: {current_filter}, Zoom: {self.zoom_factor:.1f}x"
        )

    # History management for undo/redo
    def add_to_history(self):
        """Add current state to history"""
        if self.processed_image:
            # If we're not at the end of history, truncate it
            if self.history_position < len(self.history) - 1:
                self.history = self.history[:self.history_position + 1]

            # Add current state to history
            self.history.append(self.processed_image.copy())
            self.history_position = len(self.history) - 1

            # Limit history size
            if len(self.history) > self.max_history:
                self.history = self.history[1:]
                self.history_position -= 1

    def undo(self):
        """Undo the last operation"""
        if self.history_position > 0:
            self.history_position -= 1
            self.processed_image = self.history[self.history_position].copy()
            self.display_image(self.processed_image, self.processed_canvas)
            self.status_bar.config(text="Undo: Reverted to previous state")
        else:
            self.status_bar.config(text="Nothing to undo")

    def redo(self):
        """Redo the last undone operation"""
        if self.history_position < len(self.history) - 1:
            self.history_position += 1
            self.processed_image = self.history[self.history_position].copy()
            self.display_image(self.processed_image, self.processed_canvas)
            self.status_bar.config(text="Redo: Applied next state")
        else:
            self.status_bar.config(text="Nothing to redo")

# SplashScreen class removed to simplify the application

def main():
    root = tk.Tk()
    # Create the application and store it in a global variable to prevent garbage collection
    global app
    app = ImageProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
