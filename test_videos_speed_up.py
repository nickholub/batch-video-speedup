import argparse
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from videos_speed_up import process_videos


class TestArgumentParsing:
    """Tests for command-line argument parsing."""

    def test_directory_required(self):
        """Test that --directory is required."""
        with pytest.raises(SystemExit):
            parser = argparse.ArgumentParser()
            parser.add_argument("-d", "--directory", required=True)
            parser.add_argument("-s", "--speed", type=int, default=10)
            parser.parse_args([])

    def test_directory_short_flag(self):
        """Test -d flag works."""
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--directory", required=True)
        parser.add_argument("-s", "--speed", type=int, default=10)
        args = parser.parse_args(["-d", "/some/path"])
        assert args.directory == "/some/path"

    def test_directory_long_flag(self):
        """Test --directory flag works."""
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--directory", required=True)
        parser.add_argument("-s", "--speed", type=int, default=10)
        args = parser.parse_args(["--directory", "/some/path"])
        assert args.directory == "/some/path"

    def test_speed_default(self):
        """Test speed defaults to 10."""
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--directory", required=True)
        parser.add_argument("-s", "--speed", type=int, default=10)
        args = parser.parse_args(["-d", "/some/path"])
        assert args.speed == 10

    def test_speed_custom(self):
        """Test custom speed value."""
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--directory", required=True)
        parser.add_argument("-s", "--speed", type=int, default=10)
        args = parser.parse_args(["-d", "/some/path", "-s", "5"])
        assert args.speed == 5


class TestProcessVideos:
    """Tests for the process_videos function."""

    def test_nonexistent_directory(self, capsys):
        """Test handling of non-existent directory."""
        process_videos("/nonexistent/directory/path")
        captured = capsys.readouterr()
        assert "does not exist" in captured.out

    def test_no_mp4_files(self, capsys):
        """Test handling of directory with no .mp4 files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a non-mp4 file
            with open(os.path.join(tmpdir, "test.txt"), "w") as f:
                f.write("test")

            process_videos(tmpdir)
            captured = capsys.readouterr()
            assert "No .mp4 files found" in captured.out

    def test_empty_directory(self, capsys):
        """Test handling of empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            process_videos(tmpdir)
            captured = capsys.readouterr()
            assert "No .mp4 files found" in captured.out

    def test_skips_existing_output(self, capsys):
        """Test that already processed files are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a fake input and output file
            input_file = os.path.join(tmpdir, "video.mp4")
            output_file = os.path.join(tmpdir, "video_5x.mp4")

            with open(input_file, "w") as f:
                f.write("fake video")
            with open(output_file, "w") as f:
                f.write("fake output")

            process_videos(tmpdir)
            captured = capsys.readouterr()
            assert "Skipping video.mp4: Output file already exists" in captured.out

    @patch("videos_speed_up.VideoFileClip")
    def test_processes_video_successfully(self, mock_video_clip, capsys):
        """Test successful video processing with mocked moviepy."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a fake input file
            input_file = os.path.join(tmpdir, "test_video.mp4")
            with open(input_file, "w") as f:
                f.write("fake video")

            # Setup mocks
            mock_clip = MagicMock()
            mock_fast_clip = MagicMock()
            mock_video_clip.return_value = mock_clip
            mock_clip.with_effects.return_value = mock_fast_clip

            process_videos(tmpdir, speed_factor=5)

            # Verify the video was loaded
            mock_video_clip.assert_called_once_with(input_file)

            # Verify speed effect was applied
            mock_clip.with_effects.assert_called_once()

            # Verify output was written
            expected_output = os.path.join(tmpdir, "test_video_5x.mp4")
            mock_fast_clip.write_videofile.assert_called_once()
            call_args = mock_fast_clip.write_videofile.call_args
            assert call_args[0][0] == expected_output

            # Verify clips were closed
            mock_clip.close.assert_called_once()
            mock_fast_clip.close.assert_called_once()

            captured = capsys.readouterr()
            assert "Processing: test_video.mp4" in captured.out
            assert "Processing complete" in captured.out

    @patch("videos_speed_up.VideoFileClip")
    def test_handles_processing_error(self, mock_video_clip, capsys):
        """Test error handling during video processing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a fake input file
            input_file = os.path.join(tmpdir, "bad_video.mp4")
            with open(input_file, "w") as f:
                f.write("fake video")

            # Make VideoFileClip raise an exception
            mock_video_clip.side_effect = Exception("Codec error")

            process_videos(tmpdir)

            captured = capsys.readouterr()
            assert "Failed to process bad_video.mp4" in captured.out
            assert "Codec error" in captured.out
