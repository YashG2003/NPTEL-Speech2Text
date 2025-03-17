# Speech-to-Text Dataset Pipeline

This repository has a pipeline for curating a Speech-to-Text dataset from NPTEL Deep Learning lectures.

The link to NPTEL Deep Learning course is https://nptel.ac.in/courses/106106184

The videos and transcripts are downloaded from website using Selenium for web scraping. They are processed further to make a Speech to Text dataset in jsonl format.

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
7. **preprocessed_first_5_audios**: This folder contains the audios in .wav format for first 5 lectures.

## How to Run

1. **Download data**: 
   - type "python scripts/downloader.py" in command prompt.

2. **Preprocess audio**: 
   - Type "wsl --install" in command prompt of VSCode. 
   - I was working in windows, so I installed Windows Subsystem for Linux (WSL) to run bash script. 
   - Connect to WSL in VSCode, choose WSL in the options available in terminal.
   - "sudo apt update" and "sudo apt install parallel" to install parallel.
   - "sudo apt install ffmpeg"
   - "ffmpeg -version" "ffprobe -version"
   - chmod +x ./scripts/audio_preprocessor.sh
   - ./scripts/audio_preprocessor.sh ./videos ./preprocessed_audio 4 
   - above line to run code represents (file_path <input_audio_directory> <output_audio_directory> <num_cpus>)

3. **Preprocess text**: 
   - python scripts/text_preprocessor.py

4. **Create the manifest file**: 
   - python scripts/manifest_creator.py

5. **Generate dataset statistics**: 
   - python scripts/dashboard.py

## Observations

1. **Downloading transcripts**:
   - Used Selenium to naviagte through the website and simulate the process of donwloading lectures.
   - Interacted with the elements present in the website by using their relative XPATHs.
   - All the pdfs were not getting downloaded due to errors like "Element not clickable, element click intercepted"
   - Handled these errors by adding time.sleep(3), stopped the code execution for 3 seconds. 
   - It took about 1 hour to download all transcripts.

2. **Downloading videos**:
   - Downloaded all videos using Selenium, ffmpeg. Also, tried downloading videos using Selenium, requests library.
   - It took about 2.5 hours to download videos using ffmpeg.
   - Downloading using request library was faster than using ffmpeg. 
   - For downloading a 13:40 minutes video, requests method took 1:30 minutes whereas ffmpeg took 1:50 minutes

3. **Videos to .wav format audio**
   - Removed the first 12 seconds from all videos as nothing is spoken during that period.
   - Removed the last 30 seconds from all videos as a song is played and video credits are shown during that period
   - Audios are converted to .wav 16kHz sampling rate, monochannel format.
   - The processing is done in parallel using a certain number of CPUs which is a user input.
   - It took about 30 minutes using 4 CPUs, the number of CPUs can be increased for faster execution.

4. **Transcript PDFs to raw text .txt format**
   - Extracted non-bold lines present in first page of each pdf using pdfplumber.
   - Extracted the raw text excluding the bold lines using PyMuPDF.
   - Clean the raw text by:
     - Replacing "" or "x" in dimensions (e.g., "64  64") with "cross"
     - Remove unspoken patterns like "(Refer Slide Time: xx:xx)" or "(Refer Time: xx:xx)" 
     - Removing lines starting with "Student:"
     - Converting to lowercase
     - Remove punctuation before digit conversion
     - Converting digits to their spoken form
     - Removing punctuation, including apostrophes
   - Converting all pdfs to .txt files took about 6 minutes

5. **Dashboard**
   - Most of the audio files have a duration of around 5-15 minutes.
   - Several raw text files have around 100-2000 words.
   - Most of the raw text files have around 5000-10000 characters.
   - The total number of hours is 25 hours, 117 utterances (files), 27 unique characters and vocabulary size (unique words) is 5434. 

6. This speech to text pipeline is robust and will work for any other NPTEL course having a similar website. 

## Future Work

1. There are few mistakes in the transcripts such as "MNIST" has been written as "immunized".
2. Good speech to text models can be used to generate transcripts.
3. All the generated transcripts can be used to make a final transcript by using majority voting for each word.
4. The created dataset can be used to train a speech to text model and achieve good performance.
      

