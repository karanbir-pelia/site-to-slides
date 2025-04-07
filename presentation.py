import uuid
import requests
from auth import ensure_valid_token

def create_presentation(token, title):
    """
    Create a new presentation in Alai using the standalone backend endpoint
    """
    # Ensure we have a valid token
    token = ensure_valid_token(token)

    # Generate a UUID for the presentation
    presentation_id = str(uuid.uuid4())

    url = "https://alai-standalone-backend.getalai.com/create-new-presentation"

    headers = {
        "Accept": "*/*",
        "Accept-Language": "en",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "https://app.getalai.com"
    }

    payload = {
        "presentation_id": presentation_id,
        "presentation_title": title,
        "create_first_slide": True,
        "theme_id": "a6bff6e5-3afc-4336-830b-fbc710081012",
        "default_color_set_id": 0
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"Error creating presentation: {response.status_code}, {response.text}")

    return response.json()

def pick_slide_variant(token, slide_id, variant_id):
    """
    Pick a specific variant for a slide
    This is called after setting the slide status to confirm the variant selection
    """
    # Ensure we have a valid token
    token = ensure_valid_token(token)

    url = "https://alai-standalone-backend.getalai.com/pick-slide-variant"

    headers = {
        "Accept": "*/*",
        "Accept-Language": "en",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "https://app.getalai.com"
    }

    payload = {
        "slide_id": slide_id,
        "variant_id": variant_id
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"Warning: Error picking slide variant: {response.status_code}, {response.text}")
        return None

    print(f"Successfully picked variant {variant_id} for slide {slide_id}")
    return response.json()

def create_new_slide(token, presentation_id, slide_order=1, color_set_id=0):
    """
    Create a new slide in the presentation using the create-new-slide API
    """
    # Ensure we have a valid token
    token = ensure_valid_token(token)

    # Generate a UUID for the slide
    slide_id = str(uuid.uuid4())

    url = "https://alai-standalone-backend.getalai.com/create-new-slide"

    headers = {
        "Accept": "*/*",
        "Accept-Language": "en",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "https://app.getalai.com"
    }

    payload = {
        "slide_id": slide_id,
        "presentation_id": presentation_id,
        "product_type": "PRESENTATION_CREATOR",
        "slide_order": slide_order,
        "color_set_id": color_set_id
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"Error creating new slide: {response.status_code}, {response.text}")

    return slide_id

def delete_slide(token, slide_id):
    """
    Delete a slide from the presentation using the delete-slide API
    """
    url = "https://alai-standalone-backend.getalai.com/delete-slides"
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en",
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Origin": "https://app.getalai.com"
    }

    # The JSON payload is a list of slide IDs to delete.
    payload = [slide_id]

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print(f"Deleted slide with ID: {slide_id}")

def get_share_link(token, presentation_id):
    """
    Generate a shareable link for the presentation
    """
    # Ensure we have a valid token
    token = ensure_valid_token(token)

    url = "https://alai-standalone-backend.getalai.com/upsert-presentation-share"

    headers = {
        "Accept": "*/*",
        "Accept-Language": "en",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "https://app.getalai.com"
    }

    response = requests.post(url, headers=headers, json={"presentation_id": presentation_id})
    share_id = response.text.strip('"')
    share_link = f"https://app.getalai.com/view/{share_id}"

    return share_link