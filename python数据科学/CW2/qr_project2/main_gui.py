import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser, Toplevel
import os
from PIL import Image, ImageTk, ImageDraw, ImageEnhance, ImageSequence
import tempfile
from typing import Optional
import json
import shutil
from amzqr import amzqr  # Import amzqr
from matrix import QRMatrix  # Import qr_generator
from step_display import QRStepDisplay

class QRGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Artistic QR Code Generator")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize variables
        self.background_path = None
        self.logo_path = None
        self.qr_image = None
        self.temp_dir = os.path.join(os.path.expanduser('~'), '.qrcode_temp')
        self.qr_color = "#000000"   # Default black
        self.frames = []            # For storing GIF frames
        self.current_frame = 0      # Current displayed GIF frame
        self.is_playing = False     # GIF playback status
        self.qr_code = None
        self.qr_modules = None
        
        # Set styles
        self.setup_styles()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Security warning area
        self.create_security_warning()
        
        # Input area
        self.create_input_area()
        
        # Options area
        self.create_options_area()
        
        # Display area
        self.create_display_area()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_styles(self):
        style = ttk.Style()
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))
        style.configure("TEntry", font=("Arial", 10))
        style.configure("Warning.TLabel", foreground="red", font=("Arial", 9, "italic"))
        style.configure("Title.TLabel", font=("Arial", 12, "bold"))

    def create_security_warning(self):
        warning_frame = ttk.Frame(self.main_frame)
        warning_frame.pack(fill=tk.X, pady=(0, 10))
        
        warning_text = "⚠️ Security Warning: Please note that scanning QR codes from unknown sources may involve risks, including but not limited to:\n" \
                      "• Phishing and fraud\n" \
                      "• Malicious websites and viruses\n" \
                      "• Personal information leakage\n" \
                      "Please verify the reliability of QR code sources before scanning."
        
        warning_label = ttk.Label(warning_frame, text=warning_text, style="Warning.TLabel",
                                wraplength=800, justify=tk.LEFT)
        warning_label.pack(fill=tk.X)

    def create_input_area(self):
        self.input_frame = ttk.LabelFrame(self.main_frame, text="Input", padding="10")
        self.input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Text input
        ttk.Label(self.input_frame, text="Text Content:").pack(anchor=tk.W)
        self.text_input = ttk.Entry(self.input_frame, width=50)
        self.text_input.pack(fill=tk.X, pady=(5, 10))

    def create_options_area(self):
        options_frame = ttk.LabelFrame(self.main_frame, text="Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create two-column layout
        left_frame = ttk.Frame(options_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        right_frame = ttk.Frame(options_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(20, 0))
        
        # Left options
        # Error correction level
        ecl_frame = ttk.Frame(left_frame)
        ecl_frame.pack(fill=tk.X, pady=5)
        ttk.Label(ecl_frame, text="Error Correction Level:").pack(side=tk.LEFT)
        self.error_level = ttk.Combobox(ecl_frame, 
                                      values=["L", "M", "Q", "H"],
                                      width=10,
                                      state="readonly")
        self.error_level.set("H")
        self.error_level.pack(side=tk.LEFT, padx=5)
        
        # Color selection
        color_frame = ttk.Frame(left_frame)
        color_frame.pack(fill=tk.X, pady=5)
        ttk.Label(color_frame, text="QR Code Color:").pack(side=tk.LEFT)
        self.color_button = ttk.Button(color_frame, text="Choose Color", command=self.choose_color,width=15)
        self.color_button.pack(side=tk.LEFT, padx=5)
        self.color_preview = tk.Label(color_frame, bg=self.qr_color, width=3)
        self.color_preview.pack(side=tk.LEFT)
        
        # Right options
        # Image settings
        image_frame = ttk.Frame(right_frame)
        image_frame.pack(fill=tk.X, pady=5)
        
        # Background image
        bg_frame = ttk.Frame(image_frame)
        bg_frame.pack(fill=tk.X, pady=2)
        ttk.Button(bg_frame, text="Choose Background", 
                  command=self.choose_background).pack(side=tk.LEFT, padx=5)
        self.bg_label = ttk.Label(bg_frame, text="No background selected")
        self.bg_label.pack(side=tk.LEFT, padx=5)
        
        # Logo
        logo_frame = ttk.Frame(image_frame)
        logo_frame.pack(fill=tk.X, pady=2)
        ttk.Button(logo_frame, text="Choose Logo", 
                  command=self.choose_logo).pack(side=tk.LEFT, padx=5)
        self.logo_label = ttk.Label(logo_frame, text="No logo selected")
        self.logo_label.pack(side=tk.LEFT, padx=5)
        
        # Image effect settings
        effect_frame = ttk.Frame(right_frame)
        effect_frame.pack(fill=tk.X, pady=5)
        
        # Contrast
        contrast_frame = ttk.Frame(effect_frame)
        contrast_frame.pack(fill=tk.X, pady=2)
        ttk.Label(contrast_frame, text="Contrast:").pack(side=tk.LEFT)
        self.contrast_scale = ttk.Scale(contrast_frame, from_=0.2, to=2.0, orient=tk.HORIZONTAL)
        self.contrast_scale.set(1.0)
        self.contrast_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Brightness
        brightness_frame = ttk.Frame(effect_frame)
        brightness_frame.pack(fill=tk.X, pady=2)
        ttk.Label(brightness_frame, text="Brightness:").pack(side=tk.LEFT)
        self.brightness_scale = ttk.Scale(brightness_frame, from_=0.2, to=2.0, orient=tk.HORIZONTAL)
        self.brightness_scale.set(1.0)
        self.brightness_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Generate and reset buttons
        button_frame = ttk.Frame(options_frame)
        button_frame.pack(pady=10)
        
        self.generate_btn = ttk.Button(button_frame, 
                                     text="Generate QR Code",
                                     command=self.generate_qr)
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = ttk.Button(button_frame,
                                  text="Reset Settings",
                                  command=self.reset_all)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Add demo button
        self.demo_btn = ttk.Button(button_frame,
                                text="Show Generation Process",
                                command=self.show_qr_steps)
        self.demo_btn.pack(side=tk.LEFT, padx=5)

    def create_display_area(self):
        self.display_frame = ttk.LabelFrame(self.main_frame, text="QR Code Preview", padding="10")
        self.display_frame.pack(fill=tk.BOTH, expand=True)
        
        self.qr_label = ttk.Label(self.display_frame)
        self.qr_label.pack(expand=True)
        
        # Save button
        self.save_btn = ttk.Button(self.display_frame, 
                                 text="Save QR Code",
                                 command=self.save_qr_code)
        self.save_btn.pack(pady=10)

    def choose_background(self):
        file_types = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("All files", "*.*")
        ]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if file_path:
            self.background_path = file_path
            self.bg_label.config(text=os.path.basename(file_path))

    def choose_logo(self):
        file_types = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("All files", "*.*")
        ]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if file_path:
            self.logo_path = file_path
            self.logo_label.config(text=os.path.basename(file_path))

    def choose_color(self):
        """Choose the color for the QR code"""
        color = colorchooser.askcolor(color=self.qr_color, title="Choose QR Code Color")
        if color[1]:  # color is a tuple (RGB values, hexadecimal color value)
            self.qr_color = color[1]
            self.color_preview.configure(bg=self.qr_color)

    # def save_qr_code(self):
    #     if not self.qr_image:
    #         messagebox.showwarning("Warning", "Please generate a QR code first!")
    #         return
            
    #     file_types = [("PNG Image", "*.png")]
    #     if self.background_path and self.background_path.lower().endswith('.gif'):
    #         file_types = [("GIF Animation", "*.gif")] + file_types
            
    #     file_path = filedialog.asksaveasfilename(
    #         defaultextension=".png",
    #         filetypes=file_types
    #     )
    #     if file_path:
    #         try:
    #             shutil.copy2(self.qr_image, file_path)
    #             self.status_var.set(f"QR code saved to: {file_path}")
    #         except Exception as e:
    #             messagebox.showerror("Error", f"Error saving file: {str(e)}")

    def show_qr_steps(self):
        """Display a demonstration window for the QR code generation process"""
        if not self.qr_image:
            messagebox.showwarning("Warning", "Please generate a QR code first!")
            return
            
        if not self.qr_code:
            messagebox.showwarning("Warning", "The current mode does not support process demonstration!")
            return
            
        QRStepDisplay(self.root, self.qr_code, self.qr_modules)

    # def generate_qr(self):
    #     text = self.text_input.get().strip()
    #     if not text:
    #         messagebox.showwarning("Warning", "Please enter text content!")
    #         return

    #     try:
    #         # Clean temporary directory
    #         if os.path.exists(self.temp_dir):
    #             shutil.rmtree(self.temp_dir)
    #         os.makedirs(self.temp_dir)
            
    #         # Get error correction level
    #         ecl = self.error_level.get()  # Use L, M, Q, H directly
            
    #         # Prepare save name
    #         save_name = "qrcode"
    #         if self.background_path and self.background_path.lower().endswith('.gif'):
    #             save_name += ".gif"
    #         else:
    #             save_name += ".png"
                
    #         # Convert error correction level
    #         ecl_map = {
    #             "L": QRMatrix.Ecc.LOW,
    #             "M": QRMatrix.Ecc.MEDIUM,
    #             "Q": QRMatrix.Ecc.QUARTILE,
    #             "H": QRMatrix.Ecc.HIGH
    #         }
            
    #         # Convert color from HEX to RGB
    #         color = tuple(int(self.qr_color[i:i+2], 16) for i in (1, 3, 5))
            
    #         if self.background_path and self.background_path.lower().endswith('.gif'):
    #             # Handle GIF animation
    #             version, level, qr_name = amzqr.run(
    #                 words=text,
    #                 level=ecl,
    #                 picture=self.background_path,
    #                 colorized=True,
    #                 save_name=save_name,
    #                 save_dir=self.temp_dir
    #             )
    #             qr_path = os.path.join(self.temp_dir, qr_name)
    #             self.qr_image = qr_path
    #             self.qr_code = None
    #         else:
    #             # Generate QR code
    #             qr = QRMatrix.encode_text(text, ecl_map[ecl], color)
    #             self.qr_code = qr
                
    #             # Save module data
    #             self.qr_modules = [row[:] for row in qr._modules]
                
    #             # Create image
    #             scale = 10  # Scale factor
    #             size = qr.get_size() * scale
    #             image = Image.new("RGBA", (size, size), (255, 255, 255, 0))  # Use RGBA mode
                
    #             # Draw QR code
    #             qr_color = qr.get_color() + (255,)  # Add alpha channel
    #             for y in range(qr.get_size()):
    #                 for x in range(qr.get_size()):
    #                     if qr.get_module(x, y):
    #                         for i in range(scale):
    #                             for j in range(scale):
    #                                 image.putpixel((x * scale + i, y * scale + j), qr_color)

    #             # If there's a background image
    #             if self.background_path:
    #                 bg = Image.open(self.background_path).convert('RGBA')
    #                 bg = self.adjust_image(bg)  # Apply brightness and contrast adjustments
    #                 bg = bg.resize(image.size, Image.Resampling.LANCZOS)
                    
    #                 # Create result image
    #                 result = Image.new('RGBA', image.size, (255, 255, 255, 0))
    #                 result.paste(bg, (0, 0))
    #                 result.paste(image, (0, 0), image)
    #                 image = result

    #             # If there's a Logo
    #             if self.logo_path:
    #                 logo = Image.open(self.logo_path).convert('RGBA')
    #                 # Adjust Logo size, not exceeding 25% of QR code size
    #                 logo_size = int(image.size[0] * 0.25)
    #                 logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                    
    #                 # Create rounded corner mask
    #                 mask = Image.new('L', (logo_size, logo_size), 0)
    #                 draw = ImageDraw.Draw(mask)
    #                 draw.rounded_rectangle([0, 0, logo_size, logo_size], radius=int(logo_size*0.1), fill=255)
                    
    #                 # Calculate paste position
    #                 pos = ((image.size[0] - logo_size) // 2, (image.size[1] - logo_size) // 2)
                    
    #                 # Paste Logo
    #                 image.paste(logo, pos, mask)

    #             # Save image
    #             qr_path = os.path.join(self.temp_dir, save_name)
    #             image.save(qr_path)
    #             self.qr_image = image
            
    #         # Show preview
    #         if isinstance(self.qr_image, str):
    #             self.display_qr_preview(self.qr_image)
    #         else:
    #             self.qr_code = qr  # Save QR code object for demonstration
    #             self.display_qr_preview(qr_path)
            
    #         self.status_var.set("QR code generated successfully!")

    #     except Exception as e:
    #         messagebox.showerror("Error", f"Error generating QR code: {str(e)}")
    #         self.status_var.set("Generation failed")
    
    def generate_qr(self):
        text = self.text_input.get().strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text content!")
            return

        try:
            # Clean temporary directory
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            os.makedirs(self.temp_dir)
            
            # Get error correction level
            ecl = self.error_level.get()  # Use L, M, Q, H directly
            
            # Prepare save name
            save_name = "qrcode"
            if self.background_path and self.background_path.lower().endswith('.gif'):
                save_name += ".gif"
            else:
                save_name += ".png"
                
            # Convert error correction level
            ecl_map = {
                "L": QRMatrix.Ecc.LOW,
                "M": QRMatrix.Ecc.MEDIUM,
                "Q": QRMatrix.Ecc.QUARTILE,
                "H": QRMatrix.Ecc.HIGH
            }
            
            # Convert color from HEX to RGB
            color = tuple(int(self.qr_color[i:i+2], 16) for i in (1, 3, 5))
            
            if self.background_path and self.background_path.lower().endswith('.gif'):
                # Handle GIF animation
                version, level, qr_name = amzqr.run(
                    words=text,
                    level=ecl,
                    picture=self.background_path,
                    colorized=True,
                    save_name=save_name,
                    save_dir=self.temp_dir
                )
                qr_path = os.path.join(self.temp_dir, qr_name)
                self.qr_image = qr_path
                self.qr_code = None
            else:
                # Generate QR code
                qr = QRMatrix.encode_text(text, ecl_map[ecl], color)
                self.qr_code = qr
                
                # Save module data
                self.qr_modules = [row[:] for row in qr._modules]
                
                # Create image
                scale = 10  # Scale factor
                size = qr.get_size() * scale
                image = Image.new("RGBA", (size, size), (255, 255, 255, 0))  # Use RGBA mode
                
                # Draw QR code
                qr_color = qr.get_color() + (255,)  # Add alpha channel
                for y in range(qr.get_size()):
                    for x in range(qr.get_size()):
                        if qr.get_module(x, y):
                            for i in range(scale):
                                for j in range(scale):
                                    image.putpixel((x * scale + i, y * scale + j), qr_color)

                # If there's a background image
                if self.background_path:
                    bg = Image.open(self.background_path).convert('RGBA')
                    bg = self.adjust_image(bg)  # Apply brightness and contrast adjustments
                    bg = bg.resize((size, size), Image.Resampling.LANCZOS)
                    
                    # Create result image
                    result = Image.new('RGBA', (size, size), (255, 255, 255, 0))
                    result.paste(bg, (0, 0))
                    result.paste(image, (0, 0), image)
                    image = result

                # If there's a Logo
                if self.logo_path:
                    logo = Image.open(self.logo_path).convert('RGBA')
                    logo_size = int(size * 0.25)
                    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                    
                    # Create rounded corner mask
                    mask = Image.new('L', (logo_size, logo_size), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.rounded_rectangle([0, 0, logo_size, logo_size], radius=int(logo_size*0.1), fill=255)
                    
                    # Calculate paste position
                    pos = ((size - logo_size) // 2, (size - logo_size) // 2)
                    image.paste(logo, pos, mask)

                # Save image
                qr_path = os.path.join(self.temp_dir, save_name)
                image.save(qr_path)
                self.qr_image = image  # Store as PIL.Image for saving
            
            # Show preview
            if isinstance(self.qr_image, str):
                self.display_qr_preview(self.qr_image)
            else:
                self.qr_code = qr  # Save QR code object for demonstration
                self.display_qr_preview(qr_path)
            
            self.status_var.set("QR code generated successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Error generating QR code: {str(e)}")
            self.status_var.set("Generation failed")

    def save_qr_code(self):
        if not self.qr_image:
            messagebox.showwarning("Warning", "Please generate a QR code first!")
            return
            
        file_types = [("PNG Image", "*.png")]
        if self.background_path and self.background_path.lower().endswith('.gif'):
            file_types = [("GIF Animation", "*.gif")] + file_types
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=file_types,
            initialfile="qrcode"
        )
        if file_path:
            try:
                if isinstance(self.qr_image, str):
                    # If qr_image is a path (e.g., GIF from amzqr)
                    shutil.copy2(self.qr_image, file_path)
                else:
                    # If qr_image is a PIL.Image
                    preview_size = 400
                    if file_path.lower().endswith('.gif'):
                        # Save all frames for GIF
                        frames = []
                        for frame in ImageSequence.Iterator(self.qr_image):
                            frame = frame.copy()
                            frame.thumbnail((preview_size, preview_size), Image.Resampling.LANCZOS)
                            frames.append(frame)
                        frames[0].save(file_path, save_all=True, append_images=frames[1:], loop=0)
                    else:
                        # Save as PNG
                        image = self.qr_image.copy()
                        image.thumbnail((preview_size, preview_size), Image.Resampling.LANCZOS)
                        image.save(file_path, "PNG")
                self.status_var.set(f"QR code saved to: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {str(e)}")
                self.status_var.set("Save failed")

    def display_qr_preview(self, qr_path):
        """Display QR code preview, supporting GIF animation"""
        if qr_path.lower().endswith('.gif'):
            # Load GIF animation
            self.frames = []
            image = Image.open(qr_path)
            
            # Get all frames and adjust size
            for frame in ImageSequence.Iterator(image):
                # Adjust size to fit display area
                frame = frame.copy()
                frame.thumbnail((400, 400), Image.Resampling.LANCZOS)
                self.frames.append(ImageTk.PhotoImage(frame))
            
            # Show first frame
            self.current_frame = 0
            self.qr_label.configure(image=self.frames[0])
            
            # Start animation
            if not self.is_playing:
                self.is_playing = True
                self.animate_gif()
        else:
            # Show static image
            image = Image.open(qr_path)
            # Adjust image size to fit display area
            image.thumbnail((400, 400), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.qr_label.configure(image=photo)
            self.qr_label.image = photo
            self.is_playing = False

    def animate_gif(self):
        """GIF animation playback"""
        if self.is_playing and self.frames:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.qr_label.configure(image=self.frames[self.current_frame])
            self.root.after(100, self.animate_gif)  # Show next frame after 100ms

    def adjust_image(self, image: Image.Image) -> Image.Image:
        """Adjust the contrast and brightness of the image"""
        try:
            contrast = float(self.contrast_scale.get())
            brightness = float(self.brightness_scale.get())
            
            # Adjust the RGB channels of the image based on the selected contrast and brightness values
            image = ImageEnhance.Contrast(image).enhance(contrast)
            image = ImageEnhance.Brightness(image).enhance(brightness)
            
            return image
            
        except Exception as e:
            messagebox.showwarning("Warning", f"Image adjustment failed: {str(e)}")
            return image

    def reset_all(self):
        """Reset all settings to their initial state"""
        
        # Reset the error correction level to the default value
        self.error_level.set("H")
        
        # Reset the QR code color to the default black color
        self.qr_color = "#000000"
        self.color_preview.configure(bg=self.qr_color)
        
        # Reset the background image and logo selection
        self.background_path = None
        self.logo_path = None
        self.bg_label.config(text="No background selected")
        self.logo_label.config(text="No logo selected")
        
        # Reset the contrast and brightness sliders to their default values
        self.contrast_scale.set(1.0)
        self.brightness_scale.set(1.0)
        
        # Clear the generated QR code image
        self.qr_image = None
        self.qr_label.configure(image="")
        
        # Reset the status bar message to indicate that all settings have been reset
        self.status_var.set("All settings have been reset")
        
        # Stop any ongoing GIF animation playback
        self.is_playing = False
        self.frames = []
        self.current_frame = 0

