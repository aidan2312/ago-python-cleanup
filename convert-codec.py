#Author: AAD
#Use: Convert MP4s into the correct codec for web hosting.  
#Input: A file path, Another file path
#Output: MP4s.
import os
from moviepy.editor import VideoFileClip

# Define the input directory where your videos are located
input_directory = ''

# Define the output directory where you want to save the converted videos
output_directory = ''

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Function to convert a video to H.264 codec
def convert_video(input_path, output_path):
    video = VideoFileClip(input_path)
    video.write_videofile(output_path, codec='libx264')

# Iterate through the directory structure
for root, _, files in os.walk(input_directory):
    for file in files:
        if file.endswith('.mp4'):
            input_path = os.path.join(root, file)
            
            # Create the corresponding directory structure in the output directory
            relative_path = os.path.relpath(input_path, input_directory)
            output_path = os.path.join(output_directory, relative_path)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert the video
            convert_video(input_path, output_path)

print("Conversion completed!")
