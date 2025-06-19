import cv2
import math
import os.path as osp
import numpy as np

# Insert data in the low bit.
# Lower value for BITS means less distortion but less capacity.
BITS = 2

HIGH_BITS = 256 - (1 << BITS)
LOW_BITS = (1 << BITS) - 1
BYTES_PER_BYTE = math.ceil(8 / BITS)
FLAG = '%'


def insert(path, txt):
    img = cv2.imread(path, cv2.IMREAD_ANYCOLOR)
    if img is None:
        raise ValueError(f"Could not load image from path: {path}")

    ori_shape = img.shape
    max_bytes = ori_shape[0] * ori_shape[1] // BYTES_PER_BYTE

    # Prefix the text with length and FLAG
    txt = '{}{}{}'.format(len(txt), FLAG, txt)
    if max_bytes < len(txt):
        raise ValueError(f"Message too long. Max allowed: {max_bytes} characters")

    data = np.reshape(img, -1)

    for idx, val in enumerate(txt):
        encode(data[idx * BYTES_PER_BYTE: (idx + 1) * BYTES_PER_BYTE], val)

    # Reshape to original shape
    img = np.reshape(data, ori_shape)

    # Save new image in the same directory with a new name
    directory = osp.dirname(path)
    base_name = osp.splitext(osp.basename(path))[0]
    new_filename = osp.join(directory, base_name + "_lsb_embedded.png")

    success = cv2.imwrite(new_filename, img)
    if not success:
        raise IOError(f"Failed to save image to: {new_filename}")

    return new_filename


def extract(path):
    img = cv2.imread(path, cv2.IMREAD_ANYCOLOR)
    if img is None:
        raise ValueError(f"Could not load image from path: {path}")

    data = np.reshape(img, -1)
    total = data.shape[0]
    res = ''
    idx = 0

    # Decode the message length
    while idx < total // BYTES_PER_BYTE:
        ch = decode(data[idx * BYTES_PER_BYTE: (idx + 1) * BYTES_PER_BYTE])
        idx += 1
        if ch == FLAG:
            break
        res += ch

    try:
        msg_len = int(res)
    except ValueError:
        raise ValueError("Failed to parse message length. Invalid or corrupted image.")

    end = msg_len + idx
    if end > total // BYTES_PER_BYTE:
        raise ValueError("Message length exceeds image capacity.")

    res = ''
    while idx < end:
        res += decode(data[idx * BYTES_PER_BYTE: (idx + 1) * BYTES_PER_BYTE])
        idx += 1

    return res


def encode(block, data):
    data = ord(data)
    for idx in range(len(block)):
        block[idx] &= HIGH_BITS
        block[idx] |= (data >> (BITS * idx)) & LOW_BITS


def decode(block):
    val = 0
    for idx in range(len(block)):
        val |= (block[idx] & LOW_BITS) << (idx * BITS)
    return chr(val)


if __name__ == '__main__':
    # Message to hide
    data = 'A collection of simple python mini projects to enhance your Python skills.'

    # Path to input image
    input_path = r"D:\sweety ecet\images.png"  # Use your actual image path

    # Insert message
    res_path = insert(input_path, data)
    print(f"New image saved at: {res_path}")

    # Extract and print message
    extracted_text = extract(res_path)
    print("Extracted message:")
    print(extracted_text)
