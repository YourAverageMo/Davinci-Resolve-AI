import json
import os

def parse_json(input_file):
    with open(input_file, 'r') as f:
        data = json.load(f)

    parsed_data = []
    for entry in data:
        event = {
            'type': entry['type'],
            'trigger_time': entry['triggerTime'],
        }
        parsed_data.append(event)

    return parsed_data

# Example usage
if __name__ == "__main__":
    # Set the input file path to be in the same directory as main.py
    script_directory = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(script_directory, 'input.json')

    parsed_data = parse_json(input_file_path)

    # Print the parsed data for verification
    for event in parsed_data:
        print(event)
