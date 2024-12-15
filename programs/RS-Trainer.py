import configparser
from ultralytics import YOLO

# Load settings from settings.ini
config = configparser.ConfigParser()
config.read("settings.ini")

# Extract paths from the config file
input_path = config.get("Paths", "input_path")
output_path = config.get("Paths", "output_path")
current_model_path = config.get("Paths", "current_model_path")
training_model_path = config.get("Paths", "training_model_path")

if __name__ == "__main__":
    data_yaml_path = f"{training_model_path}/data.yaml"
    project_path = f"{current_model_path}/RSV"
    model = YOLO("yolo11n.yaml")   # Use the current model path from settings.ini

    # Train the model
    model.train(
        data=data_yaml_path,        # Path to your dataset YAML file
        epochs=100,                 # Number of training epochs
        imgsz=640,                  # Image size for training (default: 640)
        batch=32,                   # Batch size (adjust based on your system capabilities)
        device=0,                   # Use '0' for GPU, 'cpu' for CPU training
        workers=4,                  # Number of data loader workers (reduce to 0 if issues persist)
        project=project_path,       # Project directory to save results
        name="RSV"            # Run name (for tracking in saved results)
    )

    # Evaluate the trained model
    metrics = model.val()
    print("Validation Metrics:", metrics)

    # Export the model for inference
    export_path = model.export(
        format="onnx",
        path=current_model_path
    )
    print(f"Model exported to {export_path}")
