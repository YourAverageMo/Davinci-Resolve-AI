import json
import os


def parse_json(input_file):
    with open(input_file, "r") as f:
        data = json.load(f)

    parsed_data = []
    for entry in data:
        event = {
            "type": entry["type"],
            "trigger_time":
            int(entry["triggerTime"]),  # Convert trigger_time to an integer
        }
        parsed_data.append(event)

    return parsed_data


def seconds_to_timecode(seconds, frame_rate=60):
    # Calculate the total number of frames
    total_frames = int(seconds * frame_rate)

    # Calculate hours, minutes, seconds, and frames
    hours = total_frames // (frame_rate * 60 * 60)
    minutes = (total_frames // (frame_rate * 60)) % 60
    seconds = (total_frames // frame_rate) % 60
    frames = total_frames % frame_rate  # this is always going to be 0

    # Format the timecode as HH:MM:SS:FF
    timecode = f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"

    return timecode


def map_event_type_to_color(event_type):
    return {
        "kill": "Blue",
        "assist": "Green",
        "death": "Red"
    }.get(event_type.lower())


def generate_timeline_markers(parsed_data):
    timeline_markers = []
    for index, event in enumerate(parsed_data, start=1):
        # Use the template structure from the "output" EDL file format
        marker_color = map_event_type_to_color(event['type'])
        marker_start_time_seconds = event['trigger_time']
        marker_start_time_tc = seconds_to_timecode(marker_start_time_seconds)

        marker_start_time_plus_1_seconds = marker_start_time_seconds + 1
        marker_start_time_plus_1_tc = seconds_to_timecode(
            marker_start_time_plus_1_seconds)

        timeline_marker = f"{index:03d} 001 V C {marker_start_time_tc} {marker_start_time_plus_1_tc} {marker_start_time_tc} {marker_start_time_plus_1_tc}\n |C:ResolveColor{marker_color} |M:Marker {index} |D:1"
        timeline_markers.append(timeline_marker)

    return timeline_markers


def save_to_file(timeline_markers, output_file):
    with open(output_file, "w") as f:
        for marker in timeline_markers:
            f.write(marker + "\n" + "\n")


# Example usage
if __name__ == "__main__":
    # Set the input and output file paths to be in the same directory as main.py
    script_directory = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(script_directory, "test_clips.json")
    output_file_path = os.path.join(script_directory, "output_markers.edl")

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
