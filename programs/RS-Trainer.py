from ultralytics import YOLO

if __name__ == "__main__":
    # Load the YOLOv8 model
    model = YOLO("yolov8n.pt")  # Replace 'yolov8n.pt' with your desired YOLOv8 model variant

    # Train the model
    model.train(
        data="/media/matthew/USB-Hub/MF-TerminaX/Input/data.yaml",  # Path to your dataset YAML file
        epochs=100,                 # Number of training epochs
        imgsz=640,                 # Image size for training (default: 640)
        batch=16,                  # Batch size (adjust based on your system capabilities)
        device=0,                  # Use '0' for GPU, 'cpu' for CPU training
        workers=4,                 # Number of data loader workers (reduce to 0 if issues persist)
        project="Output/RS-Model",  # Project directory to save results
        name="RoadScout"   # Run name (for tracking in saved results)
    )

    # Evaluate the trained model
    metrics = model.val()
    print("Validation Metrics:", metrics)

    # Export the model for inference
    export_path = model.export(format="onnx")  # Options: 'torchscript', 'onnx', 'coreml', etc.
    print(f"Model exported to {export_path}")
