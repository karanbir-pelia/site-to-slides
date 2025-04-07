import sys
from dotenv import load_dotenv
from scraper import scrape_webpage
from auth import get_alai_auth_token
from presentation import create_presentation, get_share_link
from slide_processor import create_slides

# Load environment variables
load_dotenv()

def create_alai_presentation(scraped_data, token):
    """
    Create an Alai presentation using the scraped webpage data
    """
    # Extract relevant content from scraped data
    page_title = scraped_data['title']

    # Create presentation
    presentation_data = create_presentation(token, page_title)
    presentation_id = presentation_data.get("id")
    print(f"Created presentation with ID: {presentation_id}")

    create_slides(token, presentation_data, scraped_data)

    # Generate shareable link
    share_link = get_share_link(token, presentation_id)
    return share_link


def main():
    """
    Main function to test the webpage scraping functionality
    """

    # Check if a URL was provided as a command-line argument
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        # Use a default URL for testing
        url = "https://en.wikipedia.org/wiki/Hello"
        print(f"No URL provided, using default: {url}")

    try:
        # Step 1: Scrape the webpage
        print(f"Scraping URL: {url}")
        scraped_data = scrape_webpage(url)

        # Print a summary of what was extracted
        print(f"Extracted: {len(scraped_data['paragraphs'])} paragraphs, {sum([len(scraped_data['images'][img]) for img in scraped_data['images']])} images")
        print(f"Page title: {scraped_data['title']}")

        # Step 2: Get Alai auth token (only if requested)
        if len(sys.argv) > 2 and sys.argv[2] == "--create-presentation":
            token = get_alai_auth_token()
            print("Authenticated with Alai")

            # Step 3: Create presentation
            share_link = create_alai_presentation(scraped_data, token)
            print("\nPresentation created successfully!")
            print(f"\nShareable link: {share_link}\n")

    except Exception as e:
        print(f"Error: {str(e)}")

# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()