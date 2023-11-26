import json
import os
import tkinter as tk
from tkinter import filedialog, scrolledtext


def parse_json(input_file):
    """
    Parse a JSON file and extract relevant event information. Only event type and trigger time for now.

    Parameters:
    - input_file (str): Path to the input JSON file.

    Returns:
    - list: A list of dictionaries containing event information.
    """
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
    """
    Convert seconds to a timecode format (HH:MM:SS:FF) used by Davinci Resolve .EDL file format.

    Parameters:
    - seconds (int): The input time in seconds.
    - frame_rate (int): The frame rate of the video (default is 60). For now this wont make a difference since input (seconds) is less granular than frames.

    Returns:
    - str: The timecode formatted string.
    """
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
    """
    Map event type to a corresponding color for Davinci Resolve. By Default kills are blue, assists are green, deaths are red.

    Parameters:
    - event_type (str): The type of event (kill, assist, death). Not case sensitive.

    Returns:
    - str: The color string.
    """
    return {
        "kill": "Blue",
        "assist": "Green",
        "death": "Red"
    }.get(event_type.lower())


def gen_markers(parsed_data):
    """
    Generate timeline markers for Davinci Resolve based on parsed event data.

    Parameters:
    - parsed_data (list): List of dictionaries containing event information.

    Returns:
    - list: A list of strings representing timeline markers.
    """
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


def save_file(timeline_markers, output_file, log_callback=None):
    """
    Save generated timeline markers to a .EDL file. To import in Davinci Resolve right-click timeline > timelines > import > timeline markers from edl...

    Parameters:
    - timeline_markers (list): List of strings representing timeline markers.
    - output_file (str): Path to the output file.
    - log_callback (function): Callback function to update the log.
    """
    with open(output_file, "w") as f:
        for marker in timeline_markers:
            f.write(marker + "\n" + "\n")
            if log_callback:
                log_callback(marker + "\n")


def process_files(input_file_path, output_file_path, log_callback=None):
    parsed_data = parse_json(input_file_path)
    markers = gen_markers(parsed_data)
    save_file(markers, output_file_path, log_callback)


class App:

    def __init__(self, master):
        self.master = master
        master.title("Timeline Marker Generator")
        master.minsize(width=360, height=300)
        master.geometry("360x300")

        # Configure rows and columns for resizing
        master.columnconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)
        master.columnconfigure(2, weight=1)
        master.rowconfigure(0, weight=0)
        master.rowconfigure(1, weight=0)
        master.rowconfigure(2, weight=0)
        master.rowconfigure(3, weight=0)
        master.rowconfigure(4, weight=1)

        # First Row
        self.input_label = tk.Label(master, text="Input File:")
        self.input_label.grid(row=0, column=0, sticky="e")

        self.input_entry = tk.Entry(master)
        self.input_entry.grid(row=0, column=1, sticky="ew")

        self.browse_button = tk.Button(master,
                                       text="Browse",
                                       command=self.browse_input)
        self.browse_button.grid(row=0, column=2, sticky="w")

        # Second Row
        self.output_label = tk.Label(master, text="Output File:")
        self.output_label.grid(row=1, column=0, sticky="e")

        self.output_entry = tk.Entry(master)
        self.output_entry.grid(row=1, column=1, sticky="ew")

        self.browse_button = tk.Button(master,
                                       text="Browse",
                                       command=self.browse_output)
        self.browse_button.grid(row=1, column=2, sticky="w")

        self.process_button = tk.Button(master,
                                        text="Process Files",
                                        command=self.process_files)
        self.process_button.grid(row=2, column=1)

        self.log_label = tk.Label(master, text="Log:")
        self.log_label.grid(row=3, column=1)

        self.log_text = scrolledtext.ScrolledText(master, height=10)
        self.log_text.grid(row=4, column=0, columnspan=3, sticky="nsew")

    def browse_input(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files",
                                                           "*.json")])
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, file_path)

    def browse_output(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".edl",
                                                 filetypes=[("EDL files",
                                                             "*.edl")])
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, file_path)

    def process_files(self):
        input_file_path = self.input_entry.get()
        output_file_path = self.output_entry.get()

        if input_file_path.lower() == "seattle weather":
            self.log(
                "You dont need a weather report for this... you can just assume the weather in seattle is probably cloudy with slight chance of rain at all times. as a general rule of thumb if location == seattle then weather = bad. fun fact there is a guy named murad in seattle who is a mal.\n"
            )

        if not input_file_path or not output_file_path:
            self.log("Please select both input and output files.")
            return

        try:
            process_files(input_file_path, output_file_path, self.log)
            self.log("Files processed successfully.")
        except Exception as e:
            self.log(f"Error: {str(e)}")

    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
