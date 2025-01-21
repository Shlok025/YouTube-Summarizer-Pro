# YouTube Summarizer Pro

## Overview

**YouTube Summarizer Pro** is an interactive Streamlit app that transforms YouTube video transcripts into comprehensive summaries. It leverages Google Gemini Pro's AI-powered summarization to convert video content into detailed notes, offering multiple summary formats and options for saving and downloading.

## Features

### Key Features
- **Summarization Options**: Choose from three summary types—`detailed`, `quick`, or `chapter`.
- **Timestamp Support**: Includes the option to display timestamps in the summary.
- **Downloadable Content**: Allows downloading both the full transcript and the generated summary.
- **Save to File**: Option to save summaries for later reference.
- **Multilingual Support**: Ability to handle English transcripts or auto-detect the language.
- **Video Metadata Display**: Displays key video information such as title, channel, views, and duration.

### Visualizations and UI Components
1. **Video Information**: Displays video thumbnail, title, channel, views, and duration.
2. **Transcript Viewer**: Allows users to view and interact with the extracted transcript.
3. **Summary Display**: Provides a detailed or quick summary based on the selected option.

### Interactive Filters
- **Summary Type**: Choose between `detailed`, `quick`, or `chapter` summaries.
- **Language Preference**: Select the language for the transcript (English or Auto-detect).
- **Show Timestamps**: Display timestamps alongside the summary.
- **Save to File**: Save the summary to a file for future reference.

## Requirements

To run this app, ensure the following:

1. **Streamlit**: Install the latest version of Streamlit with `pip install streamlit`.
2. **Google Generative AI**: Set up Google Generative AI and obtain an API key.
3. **YouTube Transcript API**: Ensure that the `youtube-transcript-api` library is installed.
4. **yt-dlp**: Install `yt-dlp` to fetch YouTube video metadata.

## Setup Instructions

1. Clone the repository to your local machine.
2. Install the necessary Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Set up your environment variables in a `.env` file with the following content:
    ```
    GOOGLE_API_KEY=<your-google-api-key>
    ```
4. Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```

## Usage

1. Enter a YouTube video URL in the provided input field.
2. Select the desired summary type, language, and options such as displaying timestamps or saving the summary.
3. Click the "Generate Summary" button to process the video.
4. View the generated summary and download options for both the summary and transcript.
5. Optionally, save the summary to a file for future use.

## Images:
Result 1:
![Result 1](https://github.com/user-attachments/assets/b7d5bfd6-3beb-42d1-9b6b-72afd5febe02)

Result 2:
![Result 2](https://github.com/user-attachments/assets/10aa2836-0de2-49ba-8b52-a03312bd984a)

## Contribution

Contributions are welcome! If you have suggestions for improvement or encounter any issues, feel free to open an issue or submit a pull request.



## Footer

Developed with ❤ by [Shlok Gaikwad](https://github.com/shlok025)

⚡ Features: Transcription, Summarization, Chapter Detection, and Download Options
