# Site to Slides
A fully automated URL to presentation creator.

# Webpage to Alai Presentation Converter

This tool takes any arbitrary webpage URL and creates an Alai presentation from its content, returning a shareable link. The codebase has been modularized for better maintainability and readability.

## Features

-   Web scraping using Firecrawl API
-   Automatic authentication with Alai (with token refresh)
-   Presentation creation with 2-5 slides
-   Image extraction and upload from webpages
-   Generation of shareable presentation links

## Project Structure

The project is organized into the following modules:

-   `main.py` - Entry point for the application
-   `scraper.py` - Handles webpage scraping using Firecrawl API
-   `auth.py` - Manages authentication with Alai API
-   `presentation.py` - Functions for creating and managing presentations
-   `slide_processor.py` - Processes slides and images for the presentation

## Prerequisites

1. Python 3.6 or higher
2. Required Python packages (install with `pip install -r requirements.txt`)
3. Firecrawl API key (get from https://www.firecrawl.dev/)
4. Alai account (create at https://www.getalai.com/)

## Setup

1. Clone or download this repository
2. Create a `.env` file in the same directory as the script with the following variables:

```
FIRECRAWL_API_KEY=your_firecrawl_api_key
ALAI_EMAIL=your_alai_account_email
ALAI_PASSWORD=your_alai_account_password
```

3. Install the required packages:

```bash
pip install requests python-dotenv
```

## Usage

Run the main module with a webpage URL as an argument:

```bash
python main.py https://example.com
```

When run without any additional flags, the application will:

1. Scrape the webpage using Firecrawl API
2. Extract structured data (title, paragraphs, images)
3. Save the extracted data to `data.json` file

To explicitly create a presentation, use the `--create-presentation` flag:

```bash
python main.py https://example.com --create-presentation
```

With the `--create-presentation` flag, the application will:

1. Scrape the webpage using Firecrawl API
2. Authenticate with Alai
3. Create a presentation with content from the webpage
4. Generate and return a shareable link

## How It Works

1. **Web Scraping**: Uses Firecrawl API to extract structured data (headings, paragraphs, images) from the webpage.

2. **Authentication**: Handles Alai authentication with token refresh to ensure API access remains valid.

3. **Content Processing**: Organizes webpage content into logical groups for slides.

4. **Image Handling**: Downloads images from the webpage and uploads them to Alai for use in the presentation.

5. **Presentation Creation**: Creates a title slide and content slides (2-5 total) with appropriate formatting.

6. **Link Generation**: Produces a shareable link to the final presentation.

## Example Output

```
python main.py https://en.wikipedia.org/wiki/Hello --create-presentation
Scraping URL: https://en.wikipedia.org/wiki/Hello
Extracting data...
Extracted: 5 paragraphs, 1 images
Page title: Hello - Wikipedia
Authenticated with Alai
Created presentation with ID: 4931fcc3-de0e-4e24-a12d-37eced11b3b0
Created new slide with ID: 53d356da-c1d1-4ca2-b52c-bfa2adc87e36
WebSocket closed: 1000
Successfully picked variant dee9d95a-b9cf-4d99-98bc-ab5d87851b1a for slide 53d356da-c1d1-4ca2-b52c-bfa2adc87e36
Created new slide with ID: fcaee815-553c-4851-8f3e-cf021eb53ac0
WebSocket closed: 1000
Successfully picked variant 55b7374d-3893-40a9-a5f5-1ccab93f7f14 for slide fcaee815-553c-4851-8f3e-cf021eb53ac0
Created new slide with ID: 54d0dcb0-9543-45fd-9459-2c10207963cf
WebSocket closed: 1000
Successfully picked variant e2270876-cadd-4d91-bbcd-35a76fd21259 for slide 54d0dcb0-9543-45fd-9459-2c10207963cf
Created new slide with ID: 75651250-8b7a-4c56-832c-fbca76553494
WebSocket closed: 1000
Successfully picked variant d6dd62d8-f507-40c7-8325-8f8f4ecca15d for slide 75651250-8b7a-4c56-832c-fbca76553494
Created new slide with ID: 8e001c60-a067-4fde-9944-169b61b15313
WebSocket closed: 1000
Error: Not enough messages received from WebSocket.
Deleted slide with ID: 8e001c60-a067-4fde-9944-169b61b15313
Created new slide with ID: 6288adf6-b0c6-4944-9b05-609a421ae54b
WebSocket closed: 1000
Successfully picked variant 2a9fa6f5-8dec-4e92-8878-5613db179bb0 for slide 6288adf6-b0c6-4944-9b05-609a421ae54b

Presentation created successfully!

Shareable link: https://app.getalai.com/view/WzYOJJAERtyNfWViQP66vQ
```

## Troubleshooting

-   **API Key Errors**: Ensure your Firecrawl API key is valid and correctly set in the .env file
-   **Authentication Errors**: Verify your Alai credentials are correct in the .env file
-   **Image Upload Issues**: Some websites may block image downloads; the script will continue with text-only slides
