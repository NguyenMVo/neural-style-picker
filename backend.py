from faster_whisper import WhisperModel
from icrawler.builtin import GoogleImageCrawler
from transformers import pipeline
import streamlit as st
import tempfile
import shutil
import pyaudio
import wave
from glob import glob

IMAGE_FOLDER = "image_folder"
MODEL_WHISPER = WhisperModel("base.en", device="cpu", compute_type="int8")
MODEL_QA = pipeline(
    "question-answering", model="phong1123/question_answering_finetune_on_squad2"
)


def speech_to_text(audio_filename):
    segments, info = MODEL_WHISPER.transcribe(audio_filename, beam_size=5)

    print(
        "Detected language '%s' with probability %f"
        % (info.language, info.language_probability)
    )

    text = "".join([segment.text for segment in segments])
    return text


def record_audio(filename, session_state, sample_rate=44100, chunk=1024):
    # filename = "test_file.wav"
    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Open stream
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=chunk,
    )

    frames = []
    i = 0
    try:
        while session_state.recording:
            i += 1
            print(f"Recording {i}")
            for _ in range(0, int(sample_rate / chunk)):
                data = stream.read(chunk)
                frames.append(data)
    except Exception as e:
        # st.write(f"Error: {e}")
        print(f"Error: {e}")
    finally:

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # Save the recorded data as a WAV file
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(sample_rate)
            wf.writeframes(b"".join(frames))

        print(f"Audio saved as {filename}")


def get_keyword_from_command(command):
    if not command:
        st.error("Cannot process your voice command. Please try again.")
        return None

    question = "What is the style of art that user want?"

    response = MODEL_QA(question=question, context=command)
    print("QA answer: ", response)
    return response["answer"]


def download_images_from_keyword(keyword, limit=10, image_folder=IMAGE_FOLDER):
    if not keyword:
        st.error("Cannot process your voice command. Please try again.")
        return

    shutil.rmtree(image_folder, ignore_errors=True)
    google_crawler = GoogleImageCrawler(storage={"root_dir": image_folder})
    google_crawler.crawl(keyword=keyword, max_num=limit)


def get_image_list(image_folder=IMAGE_FOLDER):
    return glob(f"{image_folder}/*")
