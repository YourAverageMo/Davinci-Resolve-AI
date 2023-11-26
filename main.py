import json
import os


def parse_json(input_file):
    with open(input_file, 'r') as f:
        data = json.load(f)

    parsed_data = []
    for entry in data:
        event = {
            'type': entry['type'],
            'trigger_time': int(entry['triggerTime']),  # Convert trigger_time to an integer
        }
        parsed_data.append(event)

    return parsed_data


def generate_timeline_markers(parsed_data):
    timeline_markers = []
    for index, event in enumerate(parsed_data, start=1):
        # Use the template structure from the "output" EDL file format
        marker_color = f"Color{event['type']}"
        marker_start_time = event['trigger_time']
        marker_start_time_plus_1_frame = marker_start_time + 1  # Adjust as needed

        timeline_marker = f"{index:03d} 001 V C {marker_start_time} {marker_start_time_plus_1_frame} {marker_start_time} {marker_start_time_plus_1_frame}\n |C:Resolve{marker_color} |M:Marker {index} |D:1"
        timeline_markers.append(timeline_marker)

    return timeline_markers

def save_to_file(timeline_markers, output_file):
    with open(output_file, 'w') as f:
        for marker in timeline_markers:
            f.write(marker + '\n')

# Example usage
if __name__ == "__main__":
    # Set the input and output file paths to be in the same directory as main.py
    script_directory = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(script_directory, 'input.json')
    output_file_path = os.path.join(script_directory, 'output_markers.txt')

    # Parse the JSON file
    parsed_data = parse_json(input_file_path)

    # Generate timeline markers
    timeline_markers = generate_timeline_markers(parsed_data)

    # Save the generated timeline markers to a text file
    save_to_file(timeline_markers, output_file_path)

    # Print the generated timeline markers for verification
    for marker in timeline_markers:
        print(marker)

    print(f"\nTimeline markers saved to {output_file_path}")
