#!/bin/bash

# Ensure the script exits on errors
set -e

# Check if all inputs are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <input_directory> <output_directory> <num_cpus>"
    exit 1
fi

# Read user inputs
INPUT_DIR=$1
OUTPUT_DIR=$2
NUM_CPUS=$3

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Function to process a single audio file
process_audio() {
    INPUT_FILE=$1
    OUTPUT_DIR=$2

    # Extract base name (e.g., video_1.mp4 -> video_1)
    BASE_NAME=$(basename "$INPUT_FILE" | sed 's/\.[^.]*$//')

    # Replace 'video' prefix with 'audio' (e.g., video_1 -> audio_1)
    OUTPUT_NAME=$(echo "$BASE_NAME" | sed 's/^video/audio/').wav
    OUTPUT_FILE="$OUTPUT_DIR/$OUTPUT_NAME"

    # Remove the first 12 seconds and last 30 seconds, convert to 16kHz mono WAV
    DURATION=$(ffprobe -i "$INPUT_FILE" -show_entries format=duration -v quiet -of csv="p=0")
    NEW_ENDING_TIME=$(echo "$DURATION - 30" | bc)  
    ffmpeg -i "$INPUT_FILE" -af "atrim=start=12:end=$NEW_ENDING_TIME" -ar 16000 -ac 1 "$OUTPUT_FILE" -y
}

export -f process_audio
export OUTPUT_DIR

# Start time when the script starts executing
START_TIME=$(date +%s)

# Find all audio files in the input directory and process them
find "$INPUT_DIR" -type f -name "*.mp4" -o -name "*.wav" -o -name "*.flac" | \
parallel -j "$NUM_CPUS" process_audio {} "$OUTPUT_DIR"

# End time when the script finishes execution
END_TIME=$(date +%s)
ELAPSED_TIME=$((END_TIME - START_TIME))

echo "Audio preprocessing complete. Total time: $ELAPSED_TIME seconds."

