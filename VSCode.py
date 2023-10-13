import cv2
import numpy as np
import streamlit as st
from io import BytesIO

st.markdown(
    """
    <style>
    .stApp {
        background-color: #1B3358;
        # margin-top:0px;
    }
    .stFileUploader {
        color: yellow;
        background-color: yellow;
    }
    .stFileUploader label {
        color: yellow;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Set Streamlit page title and header
st.title("Mineral Processing Technology")
st.header("Please Upload an Image !")

# Upload an image file
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Read the uploaded image
    img = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)

    # Create a stream to store the output image
    output_stream = BytesIO()

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Set Canny edge detection thresholds
    threshold1 = 100  # Adjust this value based on your image
    threshold2 = 200  # Adjust this value based on your image

    # Apply edge detection (e.g., using Canny)
    edges = cv2.Canny(gray, threshold1, threshold2)

    # Threshold the image to create a binary image
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours in the binary image
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    font_color = (0, 0, 221)
    font_thickness = 2

    # Loop through all contours and calculate the required parameters
    for contour in contours:
        # Smallest circle that just encapsulates the particle
        (x, y), radius = cv2.minEnclosingCircle(contour)
        center = (int(x), int(y))
        radius = int(radius)
        img = cv2.circle(img, center, radius, (0, 255, 0), 2)

        # Calculate the total surface area
        total_surface_area = cv2.contourArea(contour)
        img = cv2.putText(img, f"Total Surface Area: {total_surface_area:.2f}", (10, 30), font, font_scale, font_color, font_thickness)
        # Fit an ellipse to the contour
        ellipse = cv2.fitEllipse(contour)
        major_axis_length = max(ellipse[1])

        # Calculate the centroid of the contour
        M = cv2.moments(contour)
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        img = cv2.circle(img, (cx, cy), 5, (0, 255, 0), -1)
        img = cv2.putText(img, "Centroid: ({}, {})".format(cx, cy), (cx + 10, cy + 10), font, 0.6, (0, 0, 255), 2)
        # Get convex hull of the contour
        hull = cv2.convexHull(contour)

        # Find two furthest points in the hull (major axis)
        max_distance = 0
        pt1, pt2 = None, None
        for i in range(len(hull)):
            for j in range(i + 1, len(hull)):
                dist = np.linalg.norm(hull[i] - hull[j])
                if dist > max_distance:
                    max_distance = dist
                    pt1, pt2 = hull[i][0], hull[j][0]

        # Draw a line between these two points (major axis)
        img = cv2.line(img, tuple(pt1), tuple(pt2), (0, 0, 255), 2)
        img = cv2.putText(img, f"Major Axis Length: {max_distance:.2f}", (10, 60), font, font_scale, font_color, font_thickness)

    # Total perimeter of the particle (in pixels)
        perimeter = cv2.arcLength(contour, True)
        img = cv2.putText(img, f"Perimeter: {perimeter:.2f}", (10, 90), font, font_scale, font_color, font_thickness)


    # Display the result image
    st.image(img, channels="BGR")

    # Optionally, you can save the output image
    cv2.imwrite("output_image.png", img)
    st.write("Smallest Encapsulating Circle is drawn with Green circle.")
    st.write("Total Surface Area = ",total_surface_area,"pixels")
    st.write("Major Axis is drawn and its length = ",max_distance,"pixels")
    st.write("Total Perimeter = ",perimeter,"pixels")
    st.write("Centroid is shown with green dot and its value = ".format(cx, cy), (cx, cy))
    
