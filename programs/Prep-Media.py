import os
import configparser
from PIL import Image
import cv2
import glob

def read_settings():
    """
    Reads the input and output paths from settings.ini.
    Returns a tuple (input_path, output_path).
    """
    config = configparser.ConfigParser()
    if not os.path.exists('settings.ini'):
        print("Error: 'settings.ini' not found.")
        return None, None

    config.read('settings.ini')
    try:
        input_path = config['Paths']['input_path']
        output_path = config['Paths']['output_path']
        return input_path, output_path
    except KeyError as e:
        print(f"Missing key in settings.ini: {e}")
        return None, None

def convert_images_to_jpg(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    files = os.listdir(input_folder)

    for file in files:
        input_path = os.path.join(input_folder, file)
        if not os.path.isfile(input_path):
            continue

        try:
            with Image.open(input_path) as img:
                img = img.convert("RGB")
                base_name = os.path.splitext(file)[0]
                output_path = os.path.join(output_folder, f"{base_name}.jpg")
                img.save(output_path, "JPEG")
                print(f"Converted: {file} -> {base_name}.jpg")
                img.close()
                os.remove(input_path)
                print(f"Deleted original file: {file}")
        except Exception as e:
            print(f"Failed to convert {file}: {e}")

def extract_frames(video_path, output_folder, fps_interval=1):
    os.makedirs(output_folder, exist_ok=True)
    video_capture = cv2.VideoCapture(video_path)

    if not video_capture.isOpened():
        print(f"Error: Unable to open video file {video_path}")
        return

    frame_count = 0
    extracted_count = 0
    fps = int(video_capture.get(cv2.CAP_PROP_FPS))
    interval = max(1, int(fps * fps_interval))

    success, frame = video_capture.read()
    while success:
        if frame_count % interval == 0:
            frame_filename = os.path.join(output_folder, f"frame_{frame_count:06d}.jpg")
            cv2.imwrite(frame_filename, frame)
            extracted_count += 1

        frame_count += 1
        success, frame = video_capture.read()

    video_capture.release()
    print(f"Extraction complete. {extracted_count} frames saved to {output_folder}")

def find_mov_files(directory):
    return glob.glob(os.path.join(directory, "*.mov"))

def process_mov_files(input_directory, output_directory):
    mov_files = find_mov_files(input_directory)
    if mov_files:
        for mov_file in mov_files:
            base_name = os.path.splitext(os.path.basename(mov_file))[0]
            video_output_directory = os.path.join(output_directory, base_name)
            print(f"Processing {mov_file} into folder {video_output_directory}")
            extract_frames(mov_file, video_output_directory, fps_interval=1)
    else:
        print(f"No .mov files found in {input_directory}. Add .mov files and re-run.")

def main():
    input_folder, output_folder = read_settings()
    if not input_folder or not output_folder:
        print("Error: Missing or invalid settings. Please check 'settings.ini'.")
        return

    print("Select operation:")
    print("1. Convert images to JPG")
    print("2. Extract frames from .mov files")
    choice = input("Enter your choice (1/2): ")

    if choice == "1":
        convert_images_to_jpg(input_folder, output_folder)
        print("Image conversion completed.")
    elif choice == "2":
        process_mov_files(input_folder, output_folder)
        print("Frame extraction completed.")
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
