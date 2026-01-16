import argparse
import os
from moviepy import VideoFileClip
from moviepy.video.fx import MultiplySpeed

def process_videos(directory, speed_factor=5):
    """
    Speeds up all .mp4 files in the given directory by the speed_factor
    and saves them as new files.
    """
    
    # Check if directory exists
    if not os.path.exists(directory):
        print(f"Error: The directory '{directory}' does not exist.")
        return

    # List all files in the directory
    files = [f for f in os.listdir(directory) if f.lower().endswith(".mp4")]

    if not files:
        print("No .mp4 files found in the directory.")
        return

    print(f"Found {len(files)} videos to process...")

    for filename in files:
        # Construct full file paths
        input_path = os.path.join(directory, filename)
        
        # Create output filename (e.g., video.mp4 -> video_10x.mp4)
        name_part, ext_part = os.path.splitext(filename)
        output_filename = f"{name_part}_{speed_factor}x{ext_part}"
        output_path = os.path.join(directory, output_filename)

        # Skip if the output file already exists to prevent redundant processing
        if os.path.exists(output_path):
            print(f"Skipping {filename}: Output file already exists.")
            continue

        try:
            print(f"Processing: {filename}...")
            
            # Load the video
            clip = VideoFileClip(input_path)

            # Apply the speed effect
            fast_clip = clip.with_effects([MultiplySpeed(speed_factor)])

            # Write the result to a file with high quality
            # CRF 18 is visually lossless, lower = better quality
            fast_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                ffmpeg_params=['-crf', '18', '-preset', 'slow']
            )
            
            # Close the clips to release resources
            clip.close()
            fast_clip.close()
            
            print(f"Saved: {output_filename}")

        except Exception as e:
            print(f"Failed to process {filename}: {e}")

    print("\nProcessing complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Speed up all .mp4 files in a directory."
    )
    parser.add_argument(
        "-d", "--directory",
        required=True,
        help="Path to folder containing .mp4 files"
    )
    parser.add_argument(
        "-s", "--speed",
        type=int,
        default=5,
        help="Speed multiplier (default: 5)"
    )

    args = parser.parse_args()
    process_videos(directory=args.directory, speed_factor=args.speed)
