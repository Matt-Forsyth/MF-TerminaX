import os
import cv2
import glob
import configparser

def extract_frames(video_path, output_folder, fps_interval=1):
    fps_interval = 15
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
        # Save the frame if it matches the interval
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

def read_settings(settings_file):
    config = configparser.ConfigParser()
    config.read(settings_file)

    try:
        input_path = config["Paths"]["input_path"]
        output_path = config["Paths"]["output_path"]
        return input_path, output_path
    except KeyError as e:
        print(f"Error: Missing key in settings file: {e}")
        return None, None

if __name__ == "__main__":
    settings_file = "settings.ini"

    # Read input and output paths from settings.ini
    input_directory, output_directory = read_settings(settings_file)

    if not input_directory or not output_directory:
        print("Error: Invalid paths in settings file. Please check settings.ini.")
        exit(1)

    # Create directories if they don't exist
    os.makedirs(input_directory, exist_ok=True)
    os.makedirs(output_directory, exist_ok=True)

    # Process .mov files in the input directory
    mov_files = find_mov_files(input_directory)
    if mov_files:
        for mov_file in mov_files:
            base_name = os.path.splitext(os.path.basename(mov_file))[0]
            video_output_directory = os.path.join(output_directory, base_name)
            print(f"Processing {mov_file} into folder {video_output_directory}")
            extract_frames(mov_file, video_output_directory, fps_interval=1)
    else:
        print(f"No .mov files found in {input_directory}. Add .mov files and re-run.")
