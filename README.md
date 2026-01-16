# VideosSpeedUp

A Python CLI tool to batch speed up MP4 videos in a directory.

## Features

- Batch process all `.mp4` files in a directory
- Configurable speed multiplier (default: 5x)
- High-quality output using libx264 with CRF 18
- Skips already processed files to avoid redundant work
- Preserves audio (sped up accordingly)

## Requirements

- Python 3.x
- ffmpeg (must be installed and available in PATH)
- moviepy

## Installation

1. Install ffmpeg:
   ```bash
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt install ffmpeg

   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

2. Install Python dependencies:
   ```bash
   pip install moviepy
   ```

## Usage

```bash
# Speed up videos by 5x (default)
python videos_speed_up.py -d /path/to/videos

# Speed up videos by 10x
python videos_speed_up.py -d /path/to/videos -s 10

# Using long flags
python videos_speed_up.py --directory /path/to/videos --speed 3
```

### Arguments

| Argument | Short | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| `--directory` | `-d` | Yes | - | Path to folder containing .mp4 files |
| `--speed` | `-s` | No | 5 | Speed multiplier |

### Output

Processed videos are saved in the same directory with the speed factor appended to the filename:
- `video.mp4` → `video_5x.mp4`

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test class
pytest test_videos_speed_up.py::TestProcessVideos

# Run tests matching pattern
pytest -k "test_speed"
```

## License

MIT
