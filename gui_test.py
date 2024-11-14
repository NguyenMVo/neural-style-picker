from streamlit_image_select import image_select
import streamlit as st

img = image_select(
    label="Select an image with the style you like",
    images=[
        "image_folder\\000001.png",
        "image_folder\\000002.jpg",
        "image_folder\\000003.jpg",
        "image_folder\\000004.jpg",
        "image_folder\\000005.jpg",
        "image_folder\\000006.jpg",
        "image_folder\\000007.jpg",
        "image_folder\\000008.jpg",
        "image_folder\\000009.jpg",
        "image_folder\\000010.jpg",
    ],
    captions=None,
)
st.cache_data.clear()
