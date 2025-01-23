from pdf2image import convert_from_path
import base64
import io
from PIL import Image, ImageEnhance
from split_image import split_image
from tempfile import TemporaryDirectory
import os

def pdf_pages_to_images(pdf_path):
    images = convert_from_path(pdf_path)
    images_base64 = []
    for image in images:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        images_base64.append(image_base64)
    return images_base64


def drawing_pdf_to_images(pdf_path, rows=2, cols=2):
    # Convert each page of the PDF into an image
    images = convert_from_path(pdf_path)
    images_base64 = []

    # Create a temporary directory to store intermediate images
    with TemporaryDirectory() as output_dir:
        for page_index, image in enumerate(images, start=1):
            # Save the full page image as a JPEG
            original_page_name = f"page_{page_index}_image"
            temp_image_path = os.path.join(output_dir, f"{original_page_name}.jpg")
            image.save(temp_image_path, format="JPEG")

            # Split the image into rows x cols (2x2) = 4 images
            split_image(temp_image_path, rows, cols, should_square=True, should_cleanup=True, output_dir=output_dir)
            

            for split_filename in os.listdir(output_dir):
                if split_filename.startswith(original_page_name) and split_filename.endswith(".jpg"):
                    image_path = os.path.join(output_dir, split_filename)
                    img = Image.open(image_path)

                    # Define the brightness and contrast factors
                    brightness_factor = 1
                    contrast_factor = 4

                    # If it's the top-right quarter image, crop and zoom before adjustments
                    if split_filename.endswith("_1.jpg"):
                        width, height = img.size
                        # Crop coordinates for the top-right section
                        crop_area = (width // 3.5, 0, width, height // 2)
                        cropped_img = img.crop(crop_area)
                        img = cropped_img.resize((width, height), Image.LANCZOS)

                    # Apply brightness and contrast adjustments to all images
                    enhancer_brightness = ImageEnhance.Brightness(img)
                    img = enhancer_brightness.enhance(brightness_factor)

                    enhancer_contrast = ImageEnhance.Contrast(img)
                    img = enhancer_contrast.enhance(contrast_factor)

                    # Save the modified image
                    img.save(image_path, format="JPEG")

            for split_filename in sorted(os.listdir(output_dir)):
                if split_filename.startswith(original_page_name) and split_filename.endswith(".jpg"):
                    split_image_path = os.path.join(output_dir, split_filename)
                    with open(split_image_path, "rb") as f:
                        img_bytes = f.read()
                    image_base64 = base64.b64encode(img_bytes).decode("utf-8")
                    images_base64.append(image_base64)

    return images_base64
