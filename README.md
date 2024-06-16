Here's the updated README with a detailed step-by-step guide specific to using your script:

# VideoToTextTranscriber

This repository contains a Python script that uses `moviepy.editor` to extract audio from video files, `SpeechRecognition` to transcribe the audio into text, and OpenAI's GPT model to correct the transcript by adding punctuation and fixing spelling errors. The script estimates processing time based on a sample from the video and allows you to choose the format for the transcription output (SRT with timestamps or plain text). Use at your own risk and give me props/throw me a bone if you end up rolling this into your new, AI startup that makes a zillion dollars.

## Prerequisites

Before you begin, ensure you have met the following requirements:
- You have a `Windows/Linux/Mac` machine.
- You have Python 3.x installed.
- You have an OpenAI API key.

## Installation

To set up your local environment to run this tool, follow these steps:

1. **Clone the repository:**

```bash
git clone https://github.com/1B05H1N/VideoToTextTranscriber.git
cd VideoToTextTranscriber
```

2. **Set up a virtual environment (recommended):**

```bash
python3 -m venv myenv
source myenv/bin/activate  # On Windows use `myenv\Scripts\activate`
```

3. **Install required Python libraries:**

```bash
pip install moviepy SpeechRecognition tqdm openai
```

## Usage

Here's how to run the script to extract audio from a video file, transcribe it, and optionally correct the transcript using GPT:

1. **Set the OpenAI API Key:**

```bash
export OPENAI_API_KEY="your_openai_api_key"
```

Replace `your_openai_api_key` with your actual OpenAI API key.

2. **Run the script:**

```bash
python script.py path_to_your_video.mp4
```

Replace `path_to_your_video.mp4` with the path to the video file you wish to transcribe.

3. **Follow the prompts:**

- If an existing transcript is found, you'll be asked if you want to correct it using GPT or proceed with video transcription.
- The script will estimate the processing time based on a sample from the video.
- You will be asked if you want to proceed after seeing the estimated time.
- You can choose whether you want the output to include timestamps (SRT format) or just plain text.

### Example

Assuming your video file is located at `/path/to/video.mp4`, you would run:

```bash
python script.py /path/to/video.mp4
```

You will be prompted to confirm the estimated processing time and to choose the output format.

### Output

- If you choose to include timestamps, the output will be saved in `video_filename.srt` in SRT format.
- If you choose plain text, the output will be saved in `video_filename_transcripts.txt`.

### Step-by-Step Guide

1. **Prepare Your Environment**:
    - Ensure you have Python 3.x installed.
    - Set up a virtual environment and install the required libraries as shown in the Installation section.

2. **Set Your OpenAI API Key**:
    - Obtain your API key from OpenAI.
    - Set the API key in your terminal session:
      ```bash
      export OPENAI_API_KEY="your_openai_api_key"
      ```

3. **Run the Script**:
    - Execute the script with your video file:
      ```bash
      python script.py /path/to/your/video.mp4
      ```

4. **Follow Prompts**:
    - If an existing transcript file is found, choose whether to correct it using GPT or transcribe the video again.
    - Review the estimated processing time and decide whether to proceed.
    - Select the desired output format (SRT with timestamps or plain text).

5. **Use the Output**:
    - The transcript will be saved in the specified format.
    - Import the transcript into your YouTube video or any other platform as needed.

## Script Details

### Script Functionality

- **initialize_openai_client()**: Initializes the OpenAI client using the API key from the environment variable.
- **ask_chatgpt(question)**: Sends a question to ChatGPT and receives a corrected transcript response.
- **get_video_duration(video_file)**: Retrieves the duration of the video file.
- **estimate_processing_time(video_file, sample_duration=30)**: Estimates the processing time based on a sample from the video.
- **format_with_timing(result)**: Formats the transcription with timing for SRT output.
- **transcribe_audio(audio_path, include_timing=False)**: Transcribes the audio from the video file.
- **extract_audio_and_transcribe(video_file, include_timing=False)**: Extracts audio from the video file and transcribes it.
- **prompt_user_to_continue(estimated_time)**: Prompts the user to continue based on the estimated processing time.
- **correct_transcript_with_ai(transcript, video_filename)**: Corrects the transcript using AI.
- **save_transcript(transcript, video_filename, include_timing)**: Saves the transcript to a file.

### Usage Prompts

- **Correct Existing Transcript**: If an existing transcript file is found, the user is prompted to correct it using AI or proceed with video transcription.
- **Estimate Processing Time**: The script estimates processing time and asks the user if they want to proceed.
- **Output Format**: The user can choose to include timestamps (SRT format) or plain text for the output.

## Contributing

Contributions to this project are welcome. To contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature_branch_name`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add some feature'`).
5. Push to the branch (`git push origin feature_branch_name`).
6. Create a new Pull Request.

Feel free to check the issues page.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details.

## Contact

If you have any questions, please open an issue.