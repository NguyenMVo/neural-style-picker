import streamlit as st
from PIL import Image
import numpy as np
from io import BytesIO
from API import transfer_style
from streamlit_image_select import image_select
from backend import (
    get_image_list,
    download_images_from_keyword,
    get_keyword_from_command,
    record_audio,
    speech_to_text,
)
import time

# Set page configs. Get emoji names from WebFx
st.set_page_config(page_title="PixelMix - Style Transfer",
                   page_icon="./assets/favicon.png", layout="centered")

# -------------Header Section------------------------------------------------

title = '<p style="text-align: center;font-size: 50px;font-weight: 350;font-family:Cursive "> PixelMix </p>'
st.markdown(title, unsafe_allow_html=True)


st.markdown(
    "<b> <i> Create Digital Art using Machine Learning ! </i> </b>  &nbsp; We takes 2 images — Content Image & Style Image — and blends "
    "them together so that the resulting output image retains the core elements of the content image, but appears to "
    "be “painted” in the style of the style reference image.", unsafe_allow_html=True
)


# Example Image
st.image(image="./assets/nst.png")
st.markdown("</br>", unsafe_allow_html=True)

# st.set_page_config(page_title="Image transfer using voice command")
# st.title("Image transfer using voice command")

# -------------Body Section------------------------------------------------

# Upload Images
col1, col2 = st.columns(2)
content_image = None
style_image = None
with col1:
    content_image = st.file_uploader(
        "Upload Content Image (PNG & JPG images only)", type=['png', 'jpg'])
with col2:
    # style_image = st.file_uploader(
    #     "Upload Style Image (PNG & JPG images only)", type=['png', 'jpg'])
    st.sidebar.title("Controls")
    start = st.sidebar.button("Start")
    stop = st.sidebar.button("Stop")
    new = st.sidebar.button("New")


st.markdown("</br>", unsafe_allow_html=True)
st.warning('NOTE : You need atleast Intel i3 with 8GB memory for proper functioning of this application. ' +
   ' Images greater then (2000x2000) are resized to (1000x1000).')


if content_image is not None and style_image is not None:

    with st.spinner("Styling Images...will take about 20-30 secs"):

        content_image = Image.open(content_image)
        style_image = Image.open(style_image)

        # Convert PIL Image to numpy array
        content_image = np.array(content_image)
        style_image = np.array(style_image)

        # Path of the pre-trained TF model
        model_path = r"model"

        # output image
        styled_image = transfer_style(content_image, style_image, model_path)
        if style_image is not None:
            # some baloons
            st.balloons()

        col1, col2 = st.columns(2)
        with col1:
            # Display the output
            st.image(styled_image)
        with col2:

            st.markdown("</br>", unsafe_allow_html=True)
            st.markdown(
                "<b> Your Image is Ready ! Click below to download it. </b>", unsafe_allow_html=True)

            # de-normalize the image
            styled_image = (styled_image * 255).astype(np.uint8)
            # convert to pillow image
            img = Image.fromarray(styled_image)
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            st.download_button(
                label="Download image",
                data=buffered.getvalue(),
                file_name="output.png",
                mime="image/png")


def job():
    # for _ in range(100):
    while st.session_state.recording:
        st.write("In progress")
        time.sleep(1)


if start:
    st.session_state.recording = True
    # p = Process(target=job)
    # p.start()
    st.write("Started process")
    record_audio("test_file.wav", st.session_state)

if stop:
    st.session_state.recording = False
    time.sleep(2)
    st.write("Stopped process")
    command = speech_to_text("test_file.wav")
    st.write(command)
    keyword = get_keyword_from_command(command)
    st.write(keyword)
    st.write("Downloading images")
    download_images_from_keyword(keyword)
    img = image_select(
        label="Select an image with the style you like",
        images=get_image_list(),
        captions=None,
    )
    st.image(img, caption="Selected image")
    style_image = img