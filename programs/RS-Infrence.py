import os
import cv2
from ultralytics import YOLO  # YOLOv8 library

# Load the custom YOLOv8 model
model_path = "Input/RoadScout.pt"  # Update with the path to your YOLOv8 model
model = YOLO(model_path)

# Paths for input and output directories
input_folder = "/media/matthew/USB-Hub/MF-TerminaX/Input"
output_folder = "/media/matthew/USB-Hub/MF-TerminaX/Output"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

def process_images(input_folder, output_folder):
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
    process_images(input_folder, output_folder)
