import os
import cv2
import glob

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

if __name__ == "__main__":
    import argparse

    # Argument parser for additional flexibility
    parser = argparse.ArgumentParser(description="Extract frames from videos.")
    args = parser.parse_args()

    # Automatically handle input and output directories
    input_directory = "/media/matthew/USB-Hub/MF-Repo/TerminaX/Input"
    output_directory = "/media/matthew/USB-Hub/MF-Repo/TerminaX/Output"

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
            extract_frames(mov_file, video_output_directory, fps_interval=args.fps_interval)
    else:
        print(f"No .mov files found in {input_directory}. Add .mov files and re-run.")
 