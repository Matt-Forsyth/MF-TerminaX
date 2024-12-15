import os
import cv2
from ultralytics import YOLO
import configparser

def read_settings(settings_file):
    config = configparser.ConfigParser()
    config.read(settings_file)

    try:
        input_path = config["Paths"]["input_path"]
        output_path = config["Paths"]["output_path"]
        current_model_path = config["Paths"]["current_model_path"]
        return input_path, output_path, current_model_path
    except KeyError as e:
        print(f"Error: Missing key in settings file: {e}")
        return None, None, None

# Function to process images
def process_images(input_folder, output_folder, model):
    # List all JPG files in the input folder
    images = [f for f in os.listdir(input_folder) if f.lower().endswith('.jpg')]

    for image_name in images:
        # Read the image
        image_path = os.path.join(input_folder, image_name)
        image = cv2.imread(image_path)
        # Run inference
        results = model(image)
        # Save labels in YOLO format
        save_yolo_labels(image, results, image_name, output_folder)
        print(f"Processed and saved labels for: {image_name}")

# Function to save YOLO labels
def save_yolo_labels(image, results, image_name, output_folder):
    """
    Saves YOLOv8 detection results in YOLO label format.
    """
    height, width, _ = image.shape
    label_file_name = os.path.splitext(image_name)[0] + ".txt"
    label_file_path = os.path.join(output_folder, label_file_name)

    with open(label_file_path, "w") as f:
        for result in results:
            for bbox in result.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = bbox[:6]

                # Normalize YOLO bounding box format
                x_center = ((x1 + x2) / 2) / width
                y_center = ((y1 + y2) / 2) / height
                bbox_width = (x2 - x1) / width
                bbox_height = (y2 - y1) / height

                # Write label to file
                f.write(f"{int(class_id)} {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}\n")

if __name__ == "__main__":
    # Path to the settings file
    settings_file = "settings.ini"

    # Read paths from settings file
    input_folder, output_folder, current_model_path = read_settings(settings_file)

    if not input_folder or not output_folder or not current_model_path:
        print("Error: Invalid paths in settings file. Please check settings.ini.")
        exit(1)

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Load the custom YOLOv8 model
    model = YOLO(current_model_path)

    # Process images
    process_images(input_folder, output_folder, model)
