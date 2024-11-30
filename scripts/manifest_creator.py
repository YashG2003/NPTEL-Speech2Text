import os
import json
import wave


def get_audio_duration(audio_filepath):
    """
    Get the duration of an audio file in seconds.
    Args:
        audio_filepath (str): Path to the audio file.
    Returns:
        float: Duration of the audio file in seconds.
    """
    with wave.open(audio_filepath, 'r') as audio:
        frames = audio.getnframes()
        rate = audio.getframerate()
        duration = frames / float(rate)
    return duration


def create_training_manifest(audio_dir, text_dir, output_file):
    """
    Create a training manifest file for speech-to-text training.
    Args:
        audio_dir (str): Directory containing audio files.
        text_dir (str): Directory containing corresponding text files.
        output_file (str): Path to the output JSONL manifest file.
    """
    manifest = []

    # List and sort audio files numerically by extracting the number from filenames
    audio_files = [f for f in os.listdir(audio_dir) if f.endswith(".wav")]
    audio_files = sorted(audio_files, key=lambda x: int(x.split('_')[1].split('.')[0]))

    for audio_file in audio_files:
        audio_number = audio_file.split('_')[1].split('.')[0]
        text_file = f"lec{audio_number}.txt"

        audio_filepath = os.path.join(audio_dir, audio_file)
        text_filepath = os.path.join(text_dir, text_file)
        
        # Replace backslashes with forward slashes for JSON consistency
        audio_filepath = audio_filepath.replace("\\", "/")
        text_filepath = text_filepath.replace("\\", "/")

        if not os.path.exists(text_filepath):
            print(f"Warning: Text file for {audio_file} not found. Skipping.")
            continue

        with open(text_filepath, "r", encoding="utf-8") as f:
            text = f.read().strip()

        duration = get_audio_duration(audio_filepath)

        # Create manifest entry
        entry = {
            "audio_filepath": audio_filepath,
            "duration": duration,
            "text": text
        }
        manifest.append(entry)

    with open(output_file, "w", encoding="utf-8") as f:
        for item in manifest:
            f.write(json.dumps(item) + "\n")

    print(f"Training manifest file created at: {output_file}")


if __name__ == "__main__":
    audio_dir = "./preprocessed_audio"
    text_dir = "./preprocessed_text"
    output_file = "train_manifest.jsonl"

    create_training_manifest(audio_dir, text_dir, output_file)


