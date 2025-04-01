from PIL import Image, UnidentifiedImageError

def apply_background_color(image_path, color):
    """
    Replace transparent background with a given RGB color.
    """
    try:
        # ✅ Open image safely
        image = Image.open(image_path)
        image.verify()  # Check if image is valid
        image = Image.open(image_path).convert("RGBA")  # Reload image after verification

        new_background = Image.new("RGBA", image.size, color + (255,))  # Ensure full opacity

        # ✅ Only apply color on transparent pixels
        final_image = Image.alpha_composite(new_background, image)

        return final_image.convert("RGB")  # Convert to RGB before saving

    except UnidentifiedImageError:
        print(f"❌ ERROR: Cannot identify image file at {image_path}")
        return None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def apply_custom_background(image_path, background_image):
    """
    Replace the background of the given image with a custom uploaded background image.
    """
    image = Image.open(image_path).convert("RGBA")
    bg = Image.open(background_image).convert("RGBA").resize(image.size)

    # Composite image with custom background
    final_image = Image.alpha_composite(bg, image)
    
    return final_image.convert("RGB")
