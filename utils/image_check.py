import cv2
import numpy as np
from werkzeug.datastructures import FileStorage

def is_blurry(image_file: FileStorage, threshold: float = 70.0) -> bool:
    # Read the image in grayscale
    file_bytes = np.frombuffer(image_file.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)

    if image is None:
        print("⚠️ Failed to decode image. Treating as blurry.")
        return True

    # Compute the Laplacian and its variance
    laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
    print(f"📷 Laplacian variance: {laplacian_var}")

    # Reset the stream so Flask can re-use the file
    image_file.stream.seek(0)

    return laplacian_var < threshold
