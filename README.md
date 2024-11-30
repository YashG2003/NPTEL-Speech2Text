# Speech-to-Text Dataset Pipeline

This repository provides a pipeline for curating a Speech-to-Text dataset from NPTEL Deep Learning lectures.
The link to NPTEL Deep Learning course is https://nptel.ac.in/courses/106106184

## Setup Instructions

1. Clone the repository.
2. Install the required packages: pip install -r requirements.txt

## Scripts and other folders

1. **downloader.py**: Downloads audio files and transcripts from the specified NPTEL course.
2. **audio_preprocessor.py**: Converts audio to WAV format and preprocesses it.
3. **text_preprocessor.py**: Extracts and cleans text from transcripts.
4. **manifest_creator.py**: Creates a manifest file of jsonl format for training Speech-to-Text models.
5. **dashboard.py**: Displays dataset statistics and visualization plots.
6. **train_manifest.jsonl**: Contains data in jsonl format.
7. **preprocessed_audio**: This folder contains the audios in .wav format for first 5 lectures.

## How to Run

1. **Download data**: 
   a) type "python scripts/downloader.py" in command prompt.

2. **Preprocess audio**: 
   a) Type "wsl --install" in command prompt of VSCode. 
   b) I was working in windows, so I installed Windows Subsystem for Linux (WSL) to run bash script. 
   c) Connect to WSL in VSCode, choose WSL in the options available in terminal.
   d) "sudo apt update" and "sudo apt install parallel" to install parallel.
   e) "sudo apt install ffmpeg"
   f) "ffmpeg -version" "ffprobe -version"
   g) chmod +x ./scripts/audio_preprocessor.sh
   h) ./scripts/audio_preprocessor.sh ./videos ./preprocessed_audio 4 
   i) above line to run code represents (file_path <input_audio_directory> <output_audio_directory> <num_cpus>)

3. **Preprocess text**: 
   a) python scripts/text_preprocessor.py

4. **Create the manifest file**: 
   a) python scripts/manifest_creator.py

5. **Generate dataset statistics**: 
   a) python scripts/dashboard.py

## Observations

1. **Downloading transcripts**:
   a) Used Selenium to naviagte through the website and simulate the process of donwloading lectures.
   b) Interacted with the elements present in the website by using their relative XPATHs.
   b) All the pdfs were not getting downloaded due to errors like "Element not clickable, element click intercepted"
   c) Handled these errors by adding time.sleep(3), stopped the code execution for 3 seconds. 
   d) It took about 1 hour to download all transcripts.

2. **Downloading videos**:
   a) Downloaded all videos using Selenium, ffmpeg. Also, tried downloading videos using Selenium, requests library.
   b) It took about 2.5 hours to download videos using ffmpeg.
   c) Downloading using request library was faster than using ffmpeg. 
   d) For downloading a 13:40 minutes video, requests method took 1:30 minutes whereas ffmpeg took 1:50 minutes

3. **Videos to .wav format audio**
   a) Removed the first 12 seconds from all videos as nothing is spoken during that period.
   b) Removed the last 30 seconds from all videos as a song is played and video credits are shown during that period
   c) Audios are converted to .wav 16kHz sampling rate, monochannel format.
   d) The processing is done in parallel using a certain number of CPUs which is a user input.
   e) It took about 30 minutes using 4 CPUs, the number of CPUs can be increased for faster execution.

4. **Transcript PDFs to raw text .txt format**
   a) Extracted non-bold lines present in first page of each pdf using pdfplumber.
   b) Extracted the raw text excluding the bold lines using PyMuPDF.
   c) Clean the raw text by:
      - Replacing "" or "x" in dimensions (e.g., "64  64") with "cross"
      - Remove unspoken patterns like "(Refer Slide Time: xx:xx)" or "(Refer Time: xx:xx)" 
      - Removing lines starting with "Student:"
      - Converting to lowercase
      - Remove punctuation before digit conversion
      - Converting digits to their spoken form
      - Removing punctuation, including apostrophes
   d) Converting all pdfs to .txt files took about 6 minutes

5. **Dashboard**
   a) Most of the audio files have a duration of around 5-15 minutes.
   b) Several raw text files have around 100-2000 words.
   c) Most of the raw text files have around 5000-10000 characters.
   d) The total number of hours is 25 hours, 27 unique characters and vocabulary size (unique words) is 5434. 

6. This speech to text pipeline is robust and will work for any other NPTEL course having a similar website. 

## Future Work

1. There are few mistakes in the transcripts such as "MNIST" has been written as "immunized".
2. Good speech to text models can be used to generate transcripts.
3. All the generated transcripts can be used to make a final transcript by using majority voting for each word.
4. The created dataset can be used to train a speech to text model and achieve good performance.
      
