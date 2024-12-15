import os
from PIL import Image

def convert_images_to_jpg(input_folder, output_folder):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # List all files in the input folder
    files = os.listdir(input_folder)

    for file in files:
        input_path = os.path.join(input_folder, file)
        # Skip if it's not a file
        if not os.path.isfile(input_path):
            continue

        try:
            # Open the image
            with Image.open(input_path) as img:
                # Ensure the image is converted to RGB mode (JPEG doesn't support RGBA/Palette modes)
                img = img.convert("RGB")
                
                # Create the output path with .jpg extension
                base_name = os.path.splitext(file)[0]
                output_path = os.path.join(output_folder, f"{base_name}.jpg")
                
                # Save the image as JPEG
                img.save(output_path, "JPEG")
                print(f"Converted: {file} -> {base_name}.jpg")

            # Explicitly close the file before deletion
            img.close()
            
            # Delete the original file after processing
            os.remove(input_path)
            print(f"Deleted original file: {file}")

        except Exception as e:
            print(f"Failed to convert {file}: {e}")

if __name__ == "__main__":
    input_folder = "/media/matthew/USB-Vault/MF-TerminaX/Input"
    output_folder = "/media/matthew/USB-Vault/MF-TerminaX/Output"

    convert_images_to_jpg(input_folder, output_folder)
    print("Conversion process completed.")
