# This script was written by Ibrahim Al-Shinnawi, shinnawi.com, on 2024-06-16. It is licensed under the MIT License, use at your own risk -- no warranties provided whatsoever.

import os
import sys
import speech_recognition as sr
import moviepy.editor as mp
import time
from datetime import timedelta
from tqdm import tqdm
from openai import OpenAI

# Initialize OpenAI client with API key from environment variable 'OPENAI_API_KEY'
def initialize_openai_client():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("OpenAI API key not found. Exiting...")
        sys.exit(1)
    try:
        openai = OpenAI(api_key=api_key)
        return openai
    except Exception as e:
        print(f"Failed to initialize OpenAI client: {e}")
        return None

client = initialize_openai_client()

def ask_chatgpt(question):
    """
    Function to send a question to ChatGPT and receive a response.
    :param question: String containing the user's question
    :return: String containing ChatGPT's response or None if an error occurs
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who corrects transcripts by adding punctuation and fixing spelling errors without changing the meaning."},
                {"role": "user", "content": question}
            ],
            max_tokens=1024,
            temperature=0
        )
        response_message = response.choices[0].message.content.strip()
        return response_message
    except Exception as e:
        print(f"An error occurred with ChatGPT: {e}")
        return None

def get_video_duration(video_file):
    try:
        video = mp.VideoFileClip(video_file)
        duration = video.duration
        video.close()
        return duration
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return None

def estimate_processing_time(video_file, sample_duration=30):
    try:
        video = mp.VideoFileClip(video_file)
        sample_duration = min(sample_duration, video.duration)
        short_clip = video.subclip(0, sample_duration)
        audio_file = 'temp_calibration_audio.wav'
        start_time = time.time()
        short_clip.audio.write_audiofile(audio_file, codec='pcm_s16le', nbytes=2, fps=16000, verbose=False, logger=None)
        short_clip.close()
        video.close()

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
        transcription_start_time = time.time()
        recognizer.recognize_google(audio_data)
        transcription_time = time.time() - transcription_start_time

        total_time = time.time() - start_time + transcription_time
        return (total_time / sample_duration) * video.duration / 60
    except Exception as e:
        print(f"Error during processing time estimation: {e}")
        return None

def format_with_timing(result):
    srt_content = ""
    index = 1
    if 'alternative' in result:
        for alternative in result['alternative']:
            if 'timestamps' in alternative:
                for j, word_info in enumerate(alternative['timestamps']):
                    if j == 0:
                        start = timedelta(seconds=float(word_info[1]))  # Convert to timedelta
                    end = timedelta(seconds=float(word_info[2]))
                    transcript = word_info[0]
                    srt_content += f"{index}\n{str(start)} --> {str(end)}\n{transcript}\n\n"
                index += 1
    return srt_content

def transcribe_audio(audio_path, include_timing=False):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        total_duration = source.DURATION
        chunk_duration = 30  # seconds
        audio_chunks = int(total_duration / chunk_duration) + 1
        results = []

        with tqdm(total=audio_chunks, desc="Transcribing audio") as progress_bar:
            for i in range(audio_chunks):
                start_time = i * chunk_duration
                end_time = min((i + 1) * chunk_duration, total_duration)
                source.audio_reader.rewind()
                audio = recognizer.record(source, offset=start_time, duration=end_time - start_time)
                try:
                    if include_timing:
                        result = recognizer.recognize_google(audio, show_all=True)
                        results.append(result)
                    else:
                        result = recognizer.recognize_google(audio)
                        results.append(result)
                except sr.UnknownValueError:
                    results.append("[Unrecognized Speech]")
                except sr.RequestError as e:
                    results.append(f"[API request error: {e}]")
                progress_bar.update(1)

        if include_timing:
            return format_with_timing(results)
        else:
            return " ".join(results)

def extract_audio_and_transcribe(video_file, include_timing=False):
    try:
        video = mp.VideoFileClip(video_file)
        audio_file = 'temp_full_audio.wav'
        print("Extracting audio...")

        total_frames = int(video.fps * video.duration)
        with tqdm(total=total_frames, desc="Extracting audio") as progress_bar:
            audio_clip = video.audio
            audio_clip.write_audiofile(audio_file, codec='pcm_s16le', nbytes=2, fps=16000, verbose=False, logger=None)
            for i in range(total_frames):
                progress_bar.update(1)

        video.close()

        print("Transcribing video...")
        transcription = transcribe_audio(audio_file, include_timing)
        return transcription
    except Exception as e:
        print(f"An error occurred during the audio extraction and transcription: {e}")
        return None

def prompt_user_to_continue(estimated_time):
    print(f"Estimated time to complete processing: {estimated_time:.2f} minutes.")
    return input("Do you want to proceed? (yes/no): ").lower() == 'yes'

def correct_transcript_with_ai(transcript, video_filename):
    print("Correcting transcript using AI...")
    corrected_transcript = ask_chatgpt(transcript)
    if corrected_transcript:
        output_filename = f"{video_filename}_transcripts.txt"
        with open(output_filename, "w") as f:
            f.write(corrected_transcript)
        print(f"Corrected transcript saved to {output_filename}")
    else:
        print("Failed to correct transcript using AI.")

def save_transcript(transcript, video_filename, include_timing):
    output_filename = f"{video_filename}_transcripts.txt" if not include_timing else f"{video_filename}.srt"
    with open(output_filename, "w") as f:
        f.write(transcript)
    print(f"Transcript saved to {output_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <video_file>")
        sys.exit(1)

    video_file = sys.argv[1]
    video_filename = os.path.splitext(os.path.basename(video_file))[0]
    existing_transcript_file = f"{video_filename}_transcripts.txt"

    # Debug: Print the environment variable value
    print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")

    if os.path.exists(existing_transcript_file):
        print(f"Found existing transcript file: {existing_transcript_file}")
        print("Would you like to correct the existing transcript using AI or proceed with video transcription?")
        print("Enter '1' to correct the existing transcript using AI.")
        print("Enter '2' to proceed with video transcription.")
        user_choice = input("Your choice (1/2): ").strip()

        if user_choice == '1':
            if client:
                with open(existing_transcript_file, 'r') as f:
                    existing_transcript = f.read()
                correct_transcript_with_ai(existing_transcript, video_filename)
            else:
                print("Failed to initialize OpenAI client. Exiting...")
        elif user_choice == '2':
            duration = get_video_duration(video_file)
            if duration is None:
                print("Failed to retrieve video duration. Exiting...")
                sys.exit(1)

            estimated_total_time = estimate_processing_time(video_file)
            if estimated_total_time is None:
                print("Failed to estimate processing time. Exiting...")
                sys.exit(1)

            if prompt_user_to_continue(estimated_total_time):
                print("Do you want the output to include timestamps? (yes for SRT with timestamps, no for plain text):")
                include_timing = input().strip().lower() == 'yes'
                transcript = extract_audio_and_transcribe(video_file, include_timing)
                if transcript:
                    print("Would you like to use AI to correct the transcript? (yes/no):")
                    use_ai = input().strip().lower() == 'yes'
                    if use_ai:
                        if client:
                            correct_transcript_with_ai(transcript, video_filename)
                        else:
                            print("Failed to initialize OpenAI client. Saving raw transcript.")
                            save_transcript(transcript, video_filename, include_timing)
                    else:
                        save_transcript(transcript, video_filename, include_timing)
                else:
                    print("Failed to generate transcript.")
            else:
                print("Process aborted by the user.")
        else:
            print("Invalid choice. Exiting...")
    else:
        duration = get_video_duration(video_file)
        if duration is None:
            print("Failed to retrieve video duration. Exiting...")
            sys.exit(1)

        estimated_total_time = estimate_processing_time(video_file)
        if estimated_total_time is None:
            print("Failed to estimate processing time. Exiting...")
            sys.exit(1)

        if prompt_user_to_continue(estimated_total_time):
            print("Do you want the output to include timestamps? (yes for SRT with timestamps, no for plain text):")
            include_timing = input().strip().lower() == 'yes'
            transcript = extract_audio_and_transcribe(video_file, include_timing)
            if transcript:
                print("Would you like to use AI to correct the transcript? (yes/no):")
                use_ai = input().strip().lower() == 'yes'
                if use_ai:
                    if client:
                        correct_transcript_with_ai(transcript, video_filename)
                    else:
                        print("Failed to initialize OpenAI client. Saving raw transcript.")
                        save_transcript(transcript, video_filename, include_timing)
                else:
                    save_transcript(transcript, video_filename, include_timing)
            else:
                print("Failed to generate transcript.")
        else:
            print("Process aborted by the user.")
