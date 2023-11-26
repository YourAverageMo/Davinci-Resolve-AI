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


def to_timecode(seconds, frame_rate=60):
    # Calculate the total number of frames
    total_frames = int(seconds * frame_rate)

    # Calculate hours, minutes, seconds, and frames
    hours = total_frames // (frame_rate * 60 * 60)
    minutes = (total_frames // (frame_rate * 60)) % 60
    seconds = (total_frames // frame_rate) % 60
    frames = total_frames % frame_rate  # this is always going to be 0 since input is seconds

    # Format the timecode as HH:MM:SS:FF
    timecode = f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"

    return timecode


def color_mapping(event_type):
    return {
        "kill": "Blue",
        "assist": "Green",
        "death": "Red"
    }.get(event_type.lower())


def gen_markers(parsed_data):
    timeline_markers = []
    for index, event in enumerate(parsed_data, start=1):
        # Use the template structure from the "output" EDL file format
        marker_color = color_mapping(event['type'])
        trigger_time = event['trigger_time']
        trigger_timecode = to_timecode(trigger_time)

        # source in and out in edl file have to be different so trigger2 is + 1 second to trigger_time
        trigger2_time = trigger_time + 1
        trigger2_timecode = to_timecode(trigger2_time)

        timeline_marker = f"{index:03d} 001 V C {trigger_timecode} {trigger2_timecode} {trigger_timecode} {trigger2_timecode}\n |C:ResolveColor{marker_color} |M:Marker {index} |D:1"
        timeline_markers.append(timeline_marker)

    return timeline_markers


def save_file(timeline_markers, output_file):
    with open(output_file, "w") as f:
        for marker in timeline_markers:
            f.write(marker + "\n" + "\n")


if __name__ == "__main__":
    # Set the input and output file paths to be in the same directory as main.py
    script_directory = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(script_directory, "test_clips.json")
    output_file_path = os.path.join(script_directory, "output_markers.edl")

    # Parse the JSON file
    parsed_data = parse_json(input_file_path)

    # Generate timeline markers
    markers = gen_markers(parsed_data)

    # Save the generated timeline markers to a text file
    save_file(markers, output_file_path)

    # Print the generated timeline markers for verification
    for marker in markers:
        print(marker)

    print(f"\nTimeline markers saved to {output_file_path}")
