import os
import requests
import speech_recognition as sr
import cv2
import pyaudio
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip
from datetime import datetime

# Your Gooey.AI API key - hardcoded here
API_KEY = "sk-BJ6gi3JxtmJUi9Lwis1Z08AXeechUXf5RuWapozsSOAsMmCB"

# Generate a unique filename using a timestamp
def generate_unique_filename(base_name, extension):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"

# Perform the face swap (Placeholder, replace with actual face swap logic)
def perform_face_swap(source_image, target_image):
    # Assume successful face swap, replace this with actual code using FaceDancer or similar
    target_image_result = cv2.imread(target_image)  # Loading target image
    face_swap_output = generate_unique_filename("faceswap_result", "jpg")
    cv2.imwrite(face_swap_output, target_image_result)  # Saving the result image
    print(f"Face-swap result saved as {face_swap_output}")
    return face_swap_output

# Perform lip sync using Gooey.AI LipSyncTTS API
def perform_lipsync_tts(text_prompt):
    payload = {
        "text_prompt": text_prompt,
        "tts_provider": "OPEN_AI",
        "elevenlabs_voice_name": None,
        "elevenlabs_voice_id": None,
        "elevenlabs_api_key": None,
    }
    
    # Make the API call
    response = requests.post(
        "https://api.gooey.ai/v2/LipsyncTTS",
        headers={
            "Authorization": "Bearer " + API_KEY,
        },
        json=payload,
    )
    
    # Ensure the request was successful
    if response.ok:
        result = response.json()
        audio_url = result['output']['audio_url']
        print(f"Lip-sync audio URL: {audio_url}")
        
        # Download the lip-synced audio
        audio_output = generate_unique_filename("output_audio", "mp3")
        audio_data = requests.get(audio_url).content
        with open(audio_output, "wb") as f:
            f.write(audio_data)
        print(f"Lip-sync audio saved as {audio_output}")
        
        return audio_output
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# Function to create video using the face-swapped image and lip-synced audio
def create_lipsync_video(image_path, audio_path):
    image_clip = ImageClip(image_path)
    audio_clip = AudioFileClip(audio_path)
    
    # Set the duration of the video to match the audio
    image_clip = image_clip.set_duration(audio_clip.duration)
    
    # Set the audio to the video
    video_output = generate_unique_filename("output_video", "mp4")
    video = image_clip.set_audio(audio_clip)
    
    # Save the final video
    video.write_videofile(video_output, fps=24)
    print(f"Lip-sync video saved as {video_output}")

# Function to select microphone
def select_microphone():
    r = sr.Recognizer()
    mics = sr.Microphone.list_microphone_names()
    print("Available Microphones:")
    for i, mic in enumerate(mics):
        print(f"{i}: {mic}")
    
    mic_index = int(input("Select the microphone by entering its index: "))
    return sr.Microphone(device_index=mic_index)

# Function to select language
def select_language():
    languages = {
        1: 'en',  # English
        2: 'hi',  # Hindi
        3: 'te',  # Telugu
        4: 'ta',  # Tamil
        5: 'bn',  # Bengali
        6: 'mr'   # Marathi
    }
    
    print("Select a language:")
    for key, lang in languages.items():
        print(f"{key}: {lang.capitalize()}")

    language_choice = int(input("Enter the language number: "))
    return languages.get(language_choice, 'en')  # Default to English if invalid choice

# Convert speech to text using selected microphone and language
def record_and_convert_audio(language):
    r = sr.Recognizer()
    with select_microphone() as source:
        print("Recording for 10 seconds...")
        audio = r.record(source, duration=10)  # Recording for 10 seconds
    
    try:
        print("Recognizing speech...")
        return r.recognize_google(audio, language=language)
    except sr.UnknownValueError:
        print("Could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

# Convert text to speech
def text_to_speech(text, output_audio_path, language):
    tts = gTTS(text=text, lang=language)
    tts.save(output_audio_path)
    print(f"Text-to-Speech saved at {output_audio_path}")

def main():
    # Input source and target image paths for face swapping
    source_image = input("Enter the path to the source image (face to swap in): ")
    target_image = input("Enter the path to the target image (face to swap onto): ")
    
    # Perform face swap
    swapped_image = perform_face_swap(source_image, target_image)

    # Prompt the user to select a language
    language = select_language()

    # Record audio using the selected microphone
    input_text = record_and_convert_audio(language)
    if input_text is None:
        print("No valid input text, exiting.")
        return

    print(f"Recognized text: {input_text}")

    # Convert the recognized text to speech and save as an mp3 file
    text_to_speech(input_text, "output_audio.mp3", language)
    
    # Perform lip sync using Gooey.AI
    audio_path = perform_lipsync_tts(input_text)
    
    if audio_path:
        # Create the final lip-sync video with the face-swapped image
        create_lipsync_video(swapped_image, audio_path)

if __name__ == "__main__":
    main()