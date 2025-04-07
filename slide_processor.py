import json
import requests
import websocket
from io import BytesIO
from functools import partial
from auth import ensure_valid_token
from presentation import pick_slide_variant, create_new_slide, delete_slide

def on_message(ws, message, messages):
    messages.append(message)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed:", close_status_code, close_msg)

def on_open(ws, token, presentation_id, slide_id, context, images_on_slide):
    payload = {
        "auth_token": token,
        "presentation_id": presentation_id,
        "slide_id": slide_id,
        "slide_specific_context": context,
        "images_on_slide": images_on_slide,
        "additional_instructions": '''

Make slides that are engaging and informative with minimal text. Follow these rules for every slide:

Title
– One short relevant title.

Content
– 4–5 bullet points, each ≤ 12 words.
– One idea per bullet.

Layout depends on image availability in images_on_slide:
– If With image: two‑column with text on left and image on right or vice-versa.
– If Without image: centered title + bullets.

If images_on_slide is empty, only then fallback to using text-only layout.

        ''',
        "layout_type": "AI_GENERATED_LAYOUT",
        "update_tone_verbosity_calibration_status": False
    }
    ws.send(json.dumps(payload))

def process_slide(token, presentation_id, slide_id, context, images_on_slide):
    websocket.enableTrace(False)

    ws_url = "wss://alai-standalone-backend.getalai.com/ws/create-and-stream-slide-variants"

    # Additional headers as required by the endpoint.
    headers = [
        "Origin: https://app.getalai.com",
        "Cache-Control: no-cache",
        "Accept-Language: en",
        "Pragma: no-cache",
        "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Sec-WebSocket-Version: 13",
        "Sec-WebSocket-Extensions: permessage-deflate; client_max_window_bits"
    ]

    messages = []

    ws_app = websocket.WebSocketApp(
        ws_url,
        header=headers,
        on_open=partial(on_open,
                        token = token,
                        presentation_id = presentation_id,
                        slide_id = slide_id,
                        context = context,
                        images_on_slide = images_on_slide),
        on_message=partial(on_message,
                        messages = messages),
        on_error=on_error,
        on_close=on_close
    )

    # Run the WebSocket connection. This call will block and run forever until the connection is closed.
    ws_app.run_forever()

    if len(messages) < 2:
        print("Error: Not enough messages received from WebSocket.")
        ws_app.close()

        if "Input should be 'image/jpeg', 'image/png', 'image/gif' or 'image/webp'" in messages[-1]:
            return "Image Error"

        return False

    default_variant = json.loads(messages[1])

    pick_slide_variant(token, slide_id, default_variant['id'])

    ws_app.close()

    return True

def process_images(token, presentation_id, images):
    """
    Process images and return a list of image data URIs
    """
    if images == []:
        return []

    token = ensure_valid_token(token)

    url = "https://alai-standalone-backend.getalai.com/upload-images-for-slide-generation"

    headers = {
        "Accept": "*/*",
        "Accept-Language": "en",
        "Authorization": f"Bearer {token}",
        "Origin": "https://app.getalai.com"
    }

    files = []

    for i in range(len(images)):

        if not images[i].startswith("http"):
            continue

        # Download the image
        response = requests.get(
            images[i],
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
            }
        )

        if response.status_code != 200:
            print(f"Warning: Error downloading image: {response.status_code}\n{response.text}")
            continue

        image_data = BytesIO(response.content)

        if not image_data:
            continue

        content_type = response.headers.get("Content-Type", "image/jpeg").lower()

        extension = content_type.split('/')[1]

        if extension in ["jpeg", "png", "gif", "webp"]:
            files.append(('files', (f"image{i}.{extension}", image_data, content_type)))

    if files == []:
        return []

    files.append(('upload_input', (None, json.dumps({"presentation_id": presentation_id}), "application/json")))
    response = requests.post(url, headers=headers, files=files)

    data = response.json()

    return data['images']

def create_slides(token, presentation_data, scraped_data):
    """
    Create and process slides for the presentation using the scraped data
    """

    presentation_id = presentation_data.get("id")

    # Extract relevant content from scraped data
    paragraphs = scraped_data['paragraphs']
    para_keys = list(paragraphs.keys())
    images = scraped_data['images']

    slide_id = presentation_data['slides'][0]['id']

    num_of_slides = len(para_keys)

    i = 0

    for _ in range(num_of_slides):

        key = 'Introduction' if 'Introduction' in paragraphs else para_keys[0]

        context = key + ": " + paragraphs[key]

        if key in images:
            images_on_slide = process_images(token, presentation_id, images[key])
        else:
            images_on_slide = []

        para_keys.remove(key)
        del paragraphs[key]

        trials = 0

        while trials != 4:
            if slide_id == None:
                i += 1
                slide_id = create_new_slide(token, presentation_id, slide_order=i)

            print(f"Created new slide with ID: {slide_id}")

            slide_processed = process_slide(token, presentation_id, slide_id, context, images_on_slide)

            if slide_processed and slide_processed != "Image Error":
                slide_id = None
                break

            if slide_processed == "Image Error" and trials == 2:
                print("The images on this slide have been omitted due to an error.")
                images_on_slide = []

            delete_slide(token, slide_id)
            i -= 1
            trials += 1
            slide_id = None