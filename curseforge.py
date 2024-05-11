import os
import json
import requests
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk

def download_file(url):
    # Send a GET request to the URL with allow_redirects set to True to follow all redirects
    response = requests.get(url, allow_redirects=True)
    
    # The final URL after all redirects is the URL of the response
    final_url = response.url
    
    # Extract the file name from the final URL and decode it
    file_name = unquote(os.path.basename(final_url))
    
    # Create a directory named "MODS" if it doesn't exist
    mods_directory = os.path.join(os.getcwd(), "MODS")
    if not os.path.exists(mods_directory):
        os.makedirs(mods_directory)
    
    # Construct the full path to save the file in the "MODS" directory
    file_path = os.path.join(mods_directory, file_name)
    
    # Download the file from the final URL
    file_response = requests.get(final_url, stream=True)
    
    # Save the file to the "MODS" directory
    with open(file_path, 'wb') as file:
        for chunk in file_response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
    
    print(f"File downloaded: {file_path}")

def display_json(data):
    # Convert the JSON data to a string for display
    json_str = json.dumps(data, indent=4)

    # Find the index where the "files" key starts
    files_index = json_str.find('"files":')

    # Extract the JSON content up to the "files" key
    json_content = json_str[:files_index]

    # Create a Tkinter window
    root = tk.Tk()
    root.title("JSON Data")

    # Create a Text widget for displaying the JSON content
    text_widget = tk.Text(root)
    text_widget.pack(fill=tk.BOTH, expand=True)

    # Insert the JSON content into the Text widget
    text_widget.insert(tk.END, json_content)

    # Allow the user to edit the JSON content
    text_widget.config(state=tk.NORMAL)

    # Start the Tkinter event loop
    root.mainloop()

# Ask for the directory
directory = input("What is the modpack folder? ")

# Convert the directory to an absolute path
absolute_directory = os.path.abspath(directory)

# Check if the directory exists
if not os.path.exists(absolute_directory):
    print("The specified directory does not exist.")
    exit()

# Check if the manifest.json file exists in the directory
manifest_file = os.path.join(absolute_directory, "manifest.json")
if not os.path.exists(manifest_file):
    print("The manifest.json file does not exist in the specified directory.")
    exit()

# Open the manifest.json file and load the data
with open(manifest_file, "r") as file:
    data = json.load(file)

# Collect all URLs to download
urls_to_download = [f"https://www.curseforge.com/api/v1/mods/{file_data['projectID']}/files/{file_data['fileID']}/download" for file_data in data["files"]]

print("close the tinker window to start downloading the files, the files will be downloaded in a folder called mods")
display_json(data)

# Use ThreadPoolExecutor to download files in parallel
with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(download_file, urls_to_download)
