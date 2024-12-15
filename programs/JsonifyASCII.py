import json
import configparser
import os

def ascii_art_to_json(input_path, output_path):
    try:
        # Ensure the output directory exists
        os.makedirs(output_path, exist_ok=True)
        
        # Process all .txt files in the input directory
        for file_name in os.listdir(input_path):
            if file_name.endswith(".txt"):
                input_file = os.path.join(input_path, file_name)
                output_file = os.path.join(output_path, f"{os.path.splitext(file_name)[0]}.json")

                # Read ASCII art from the input file
                with open(input_file, 'r') as f:
                    lines = f.readlines()
                
                # Create a JSON-friendly single-line string
                formatted_art = " \n".join(line.rstrip() for line in lines)  # Preserve spaces at the start
                
                # Save it to a JSON file
                with open(output_file, 'w') as f:
                    json.dump({"ascii_art": formatted_art}, f, indent=4)
                
                print(f"Converted {file_name} to JSON: {output_file}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    # Load settings from settings.ini
    config = configparser.ConfigParser()
    config.read("settings.ini")
    
    try:
        input_path = config["Paths"]["input_path"]
        output_path = config["Paths"]["output_path"]

        # Validate paths
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input path does not exist: {input_path}")

        # Convert ASCII art to JSON
        ascii_art_to_json(input_path, output_path)
    except KeyError as e:
        print(f"Missing configuration in settings.ini: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
