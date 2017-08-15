"""Detect skin and nudity in images."""
import os
import numpy as np
import cv2

from skinny.utils import PROCESSED_DIR


def resize_to_ratio(frame):
    """resize image to a certain size."""
    rows, cols, _ = frame.shape

    ratio = float(cols)/float(rows)
    new_rows = 400
    new_cols = int(ratio*new_rows)

    resized_image = cv2.resize(frame, (new_cols, new_rows))
    return resized_image


def skin_detect(image):
    """detect skin frame."""
    frame = cv2.imread(image)
    lower = np.array([0, 48, 80], np.uint8)
    # HSV: V-79%
    upper = np.array([20, 150, 179], np.uint8)

    frame = resize_to_ratio(frame)

    converted = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    skinMask = cv2.inRange(converted, lower, upper)
    skinMask = cv2.GaussianBlur(skinMask, (3, 3), 1)
    skinMask = cv2.erode(skinMask, kernel, iterations=2)
    skinMask = cv2.dilate(skinMask, kernel, iterations=2)

    skin = cv2.bitwise_and(frame, frame, mask=skinMask)

    return skin


def skin_detect_percentage(image_dir=None):
    """Skin detection from image."""
    result = skin_detect(image_dir)
    filename = os.path.join(PROCESSED_DIR, image_dir.split('/')[-1])

    if not os.path.exists(PROCESSED_DIR):
            os.makedirs(PROCESSED_DIR)
    cv2.imwrite(filename, result)

    # take pixel values from inside contours,
    # that way we get random samples as well.
    grey_img = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    greyscale_skin_nonzero_count = cv2.countNonZero(grey_img)

    return float(greyscale_skin_nonzero_count)/float(grey_img.size)


def nudity_detect_certainty(image_dir=None):
    """Nudity detection from image."""
    result = skin_detect(image_dir)
    filename = os.path.join(PROCESSED_DIR, image_dir.split('/')[-1])

    if not os.path.exists(PROCESSED_DIR):
            os.makedirs(PROCESSED_DIR)
    cv2.imwrite(filename, result)

    # take pixel values from inside contours.
    # that way we get random samples as well.
    grey_img = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    greyscale_skin_nonzero_count = cv2.countNonZero(grey_img)

    return float(greyscale_skin_nonzero_count)/float(grey_img.size)
