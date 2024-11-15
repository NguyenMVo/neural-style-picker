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


def transfer_style_from_images(content_image, style_image):
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
                "<b> Your Image is Ready ! Click below to download it. </b>",
                unsafe_allow_html=True,
            )

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
                mime="image/png",
            )


def set_stage(stage=None):
    if stage is not None:
        st.session_state.stage = stage
    else:
        st.session_state.stage = st.session_state.stage + 1
    print("updated flow stage: ", st.session_state.stage)


def voice_command_button_clicked():
    if st.session_state.stage > 1:
        st.session_state.stage = 1
    else:
        st.session_state.stage = st.session_state.stage + 1
    print(
        "Voice command button clicked, updated flow stage: ",
        st.session_state.stage,
    )
    if st.session_state.stage == 1:
        st.session_state.recording = True
    else:
        st.session_state.recording = False


if "stage" not in st.session_state:
    print("Initializing stage")
    st.session_state.stage = 0
    st.session_state.recording = False
    st.session_state.style_image_1_staging = None

# Set page configs. Get emoji names from WebFx
st.set_page_config(
    page_title="Image Style Transfer",
    page_icon="./assets/favicon.png",
    layout="centered",
)

# -------------Header Section------------------------------------------------

title = '<p style="text-align: center;font-size: 50px;font-weight: 350;font-family:Cursive "> Multimedia </p>'
st.markdown(title, unsafe_allow_html=True)


st.markdown(
    # TODO: Change the description
    "<b> <i> Create Digital Art using Machine Learning ! </i> </b>  &nbsp; We takes 2 images — Content Image & Style Image — and blends "
    "them together so that the resulting output image retains the core elements of the content image, but appears to "
    "be “painted” in the style of the style reference image.",
    unsafe_allow_html=True,
)


# Example Image
st.image(image="./assets/nst.png")
st.markdown("</br>", unsafe_allow_html=True)

# -------------Body Section------------------------------------------------

# Upload Images
# col1, col2 = st.columns(2)
content_image = None
style_image = None


# Step1: Upload content image
st.title("Step1: Upload content image")
content_image = st.file_uploader(
    "Upload Content Image (PNG & JPG images only)", type=["png", "jpg"]
)
if content_image:
    st.image(content_image, caption="Content Image")

# Step2: Upload style image
st.title("Step2: Upload style image")

col1, col2 = st.columns([0.8, 0.2])
with col1:
    style_image_1 = st.file_uploader(
        "Upload Style Image (PNG & JPG images only)",
        type=["png", "jpg"],
        disabled=style_image is not None,
    )
    if style_image_1 and st.session_state.style_image_1_staging != style_image_1:
        st.session_state.style_image_1_staging = style_image_1
        set_stage(5)

with col2:
    st.container(height=20, border=False)
    voice_command = st.button(
        label="Use voice command",
        icon=":material/mic:",
        on_click=voice_command_button_clicked,
        type="primary",
    )
    PLACEHOLDER_COL2 = st.empty()
    if st.session_state.stage == 1:
        PLACEHOLDER_COL2.empty()
        with PLACEHOLDER_COL2.container():
            st.write("Recording...")
            record_audio("test_file.wav", st.session_state)

    if st.session_state.stage == 2:
        PLACEHOLDER_COL2.empty()
        with PLACEHOLDER_COL2.container():
            st.write("Processing...")
            time.sleep(2)
        set_stage()

PLACEHOLDER = st.empty()


if st.session_state.stage == 3:
    PLACEHOLDER_COL2.empty()
    PLACEHOLDER.empty()
    with PLACEHOLDER.container():
        st.session_state.command = speech_to_text("test_file.wav")
        st.write(f"Your command: {st.session_state.command}")
        st.session_state.keyword = get_keyword_from_command(st.session_state.command)
        st.write(f"Style keyword: {st.session_state.keyword}")
        with st.spinner("Downloading images"):
            download_images_from_keyword(st.session_state.keyword)
        set_stage()

if st.session_state.stage == 4:
    PLACEHOLDER.empty()
    with PLACEHOLDER.container():
        st.write(f"Your command: {st.session_state.command}")
        st.write(f"Style keyword: {st.session_state.keyword}")
        with st.expander("Selecting image", expanded=True):
            st.cache_data.clear()
            img = image_select(
                label="Select an image with the style you like",
                images=get_image_list(),
                captions=None,
            )
        style_image = img
        st.image(style_image, caption="Style Image")

if st.session_state.stage == 5:
    PLACEHOLDER.empty()
    with PLACEHOLDER.container():
        style_image = st.session_state.style_image_1_staging
        st.image(style_image, caption="Style Image")


# Step3: Generate Image
st.title("Step3: Generate Image")
generate_image_button = st.button("Generate Image")
if generate_image_button:
    if content_image is not None and style_image is not None:
        transfer_style_from_images(content_image, style_image)
    else:
        st.error("Please upload both content and style images")
