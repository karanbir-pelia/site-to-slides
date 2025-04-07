import json
import os
from firecrawl import FirecrawlApp
from pydantic import BaseModel

def scrape_webpage(url):
    """
    Scrape a webpage using Firecrawl API and extract structured data
    """
    # Initialize the FirecrawlApp with your API key
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

    class ExtractSchema(BaseModel):
        title: str
        images: dict
        paragraphs: dict

    data = None

    while not (data != None and
        'title' in data['data'] and
        'images' in data['data'] and
        'paragraphs' in data['data'] and
        data['data']['title']!='' and
        len(data['data']['paragraphs']) > 2):

        print(f"Extracting data...")

        data = app.extract([
            url
        ], {
            'prompt': '''

You'll be given the raw HTML of a webpage. Parse it and return a single JSON object with three keys: `title`, `paragraphs`, and `images`.

1. **Extract the page title**
    - Grab the text inside `<title>` and set `"title"` to that string.

2. **Build the `paragraphs` dictionary**
    - Keys: section headings.
    - Values: the concatenated plain text relevant paragraphs under that heading.
    - Always include an `"Introduction"` key first.
    - Include at least 4–6 sections total.
    - Order the entries exactly as they appear in the HTML.

3. **Build the `images` dictionary**
    - Keys: must exactly match the keys in `paragraphs`.
    - Values: a list of absolute, publicly accessible URLs from all `<img src="…">` tags within that section.
    - Try to include at least one image URL per section but if a section has no images, use an empty list. DO NOT INCLUDE EMPTY STRINGS IN THE LISTS.
    - Try to include mostly png images.
    - Include as many png images as possible.

4. **Output format**
    ```json
    {
        "title": "…",
        "paragraphs": {
        "Introduction": "…",
        "Section 1 Heading": "…",
        …
        },
        "images": {
        "Introduction": ["https://…", …],
        "Section 1 Heading": [ … ],
        …
        }
    }

            ''',
            'schema': ExtractSchema.model_json_schema(),
        })

        with open('data.json', 'w') as f:
            json.dump(data['data'], f, indent=4)

    return data['data']