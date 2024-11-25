import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image
import cv2

def update_progress(current, total):
    progress = int((current / total) * 100)
    root.title(f"File Converter - {progress}% Completed")

def convert_to_png(files, destination):
    total = len(files)
    for i, file in enumerate(files, start=1):
        try:
            image = Image.open(file)
            file_name = Path(file).stem
            output_path = Path(destination) / f"{file_name}.png"
            image.save(output_path, "PNG")
        except Exception as e:
            print(f"Error converting {file} to PNG: {e}")
        update_progress(i, total)

def convert_to_gif(files, destination):
    for file in files:
        try:
            file_name = Path(file).stem
            output_path = Path(destination) / f"{file_name}.gif"
            with Image.open(file) as img:
                if getattr(img, "is_animated", False):
                    frames = []
                    durations = []
                    for frame in range(img.n_frames):
                        img.seek(frame)
                        # Convert each frame to RGBA for proper transparency handling
                        frame_image = img.convert("RGBA")
                        frames.append(frame_image)
                        durations.append(img.info.get("duration", 100))  # Default duration
                    
                    # Save the frames as an animated GIF
                    frames[0].save(
                        output_path,
                        save_all=True,
                        append_images=frames[1:],
                        loop=0,
                        duration=durations,
                        disposal=2,  # Clear each frame before displaying the next
                    )
                else:
                    # Static .webp -> single-frame .gif
                    img.save(output_path, "GIF")
        except Exception as e:
            print(f"Error converting {file} to GIF: {e}")

def convert_to_mp4(files, destination):
    total = len(files)
    for i, file in enumerate(files, start=1):
        try:
            if file.endswith(".webm"):
                capture = cv2.VideoCapture(file)
                file_name = Path(file).stem
                output_path = str(Path(destination) / f"{file_name}.mp4")
                fps = capture.get(cv2.CAP_PROP_FPS)
                width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                
                success, frame = capture.read()
                while success:
                    writer.write(frame)
                    success, frame = capture.read()
                capture.release()
                writer.release()
            else:
                print(f"{file} is not a video. Skipping MP4 conversion.")
        except Exception as e:
            print(f"Error converting {file} to MP4: {e}")
        update_progress(i, total)

def auto_convert(files, destination):
    total = len(files)
    for i, file in enumerate(files, start=1):
        if file.endswith(".webm"):
            # Convert videos to MP4
            convert_to_mp4([file], destination)
        elif file.endswith(".webp"):
            # Determine if the .webp is animated
            try:
                with Image.open(file) as img:
                    if getattr(img, "is_animated", False):
                        # Convert animated .webp to GIF
                        convert_to_gif([file], destination)
                    else:
                        # Convert static .webp to PNG
                        convert_to_png([file], destination)
            except Exception as e:
                print(f"Error processing {file}: {e}")
        else:
            print(f"Unsupported file format for auto conversion: {file}")
        update_progress(i, total)

def select_files():
    files = filedialog.askopenfilenames(filetypes=[("Image/Video Files", "*.webp *.webm")])
    if files:
        input_files.extend(files)
        files_label.config(text=f"Selected {len(input_files)} file(s)")

def select_destination():
    folder = filedialog.askdirectory()
    if folder:
        destination_folder.set(folder)
        destination_label.config(text=f"Destination: {folder}")

def process_files(conversion_type):
    if not input_files:
        messagebox.showerror("Error", "No input files selected.")
        return
    if not destination_folder.get():
        messagebox.showerror("Error", "No destination folder selected.")
        return

    root.title("File Converter - 0% Completed")
    if conversion_type == "png":
        convert_to_png(input_files, destination_folder.get())
    elif conversion_type == "gif":
        convert_to_gif(input_files, destination_folder.get())
    elif conversion_type == "auto":
        auto_convert(input_files, destination_folder.get())

    root.title("File Converter - Completed")
    messagebox.showinfo("Success", "Conversion completed.")

# Initialize Tkinter
root = tk.Tk()
root.title("File Converter")

input_files = []
destination_folder = tk.StringVar()

# File Selection
files_frame = tk.Frame(root)
files_frame.pack(pady=10)

select_files_button = tk.Button(files_frame, text="Select Files", command=select_files)
select_files_button.pack(side=tk.LEFT, padx=5)

files_label = tk.Label(files_frame, text="No files selected.")
files_label.pack(side=tk.LEFT)

# Destination Folder Selection
destination_frame = tk.Frame(root)
destination_frame.pack(pady=10)

select_destination_button = tk.Button(destination_frame, text="Select Destination", command=select_destination)
select_destination_button.pack(side=tk.LEFT, padx=5)

destination_label = tk.Label(destination_frame, text="No destination folder selected.")
destination_label.pack(side=tk.LEFT)

# Conversion Buttons
buttons_frame = tk.Frame(root)
buttons_frame.pack(pady=10)

convert_png_button = tk.Button(buttons_frame, text="Convert to PNG", command=lambda: process_files("png"))
convert_png_button.pack(side=tk.LEFT, padx=5)

convert_gif_button = tk.Button(buttons_frame, text="Convert to GIF", command=lambda: process_files("gif"))
convert_gif_button.pack(side=tk.LEFT, padx=5)

auto_convert_button = tk.Button(buttons_frame, text="Auto Convert", command=lambda: process_files("auto"))
auto_convert_button.pack(side=tk.LEFT, padx=5)

root.mainloop()