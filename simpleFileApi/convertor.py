import sys

import numpy as np
import cv2
from PIL import Image
import shortuuid
import os.path
from pathlib import Path


from simpleFileApi.settings import MEDIA_ROOT, MEDIA_URL


def generate_uuid() -> str:
    """Generate a UUID."""
    return shortuuid.ShortUUID().random(20)


def convert_image(base_file_name, pre_file_path):
    new_file_name = base_file_name + "_out.png"

    img = Image.open(pre_file_path)
    img = img.convert("RGBA")

    data = img.getdata()

    new_data = []

    for items in data:
        if items[0] == 255 and items[1] == 255 and items[2] == 255:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(items)

    img.putdata(new_data)
    path = os.path.join(MEDIA_ROOT, new_file_name)
    img.save(path, "PNG")
    img.close()
    return new_file_name


def process_image(file_name):
    file_path = os.path.join(MEDIA_ROOT, file_name)
    base_file_name = Path(file_path).stem
    image = cv2.imread(file_path)

    result = image.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower = np.array([90, 38, 0])
    upper = np.array([145, 255, 255])
    mask = cv2.inRange(image, lower, upper)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    close = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)

    cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    boxes = []
    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        boxes.append([x, y, x + w, y + h])

    boxes = np.asarray(boxes)
    left = np.min(boxes[:, 0])
    top = np.min(boxes[:, 1])
    right = np.max(boxes[:, 2])
    bottom = np.max(boxes[:, 3])

    result[close == 0] = (255, 255, 255)
    ROI = result[top:bottom, left:right].copy()
    cv2.rectangle(result, (left, top), (right, bottom), (36, 255, 12), 2)

    # pre_file_name = generate_uuid() + ".png"
    pre_file_path = os.path.join(MEDIA_ROOT, base_file_name + "_convert.png")

    cv2.imwrite(pre_file_path, ROI)
    cv2.waitKey()

    new_file_path = convert_image(base_file_name, pre_file_path)
    # os.remove(pre_file_path)
    # os.remove(file_path)
    return new_file_path
