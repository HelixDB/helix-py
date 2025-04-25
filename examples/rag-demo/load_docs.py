from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re

def setup_driver():
    """Set up Selenium WebDriver with Chrome in headless mode."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        from webdriver_manager.chrome import ChromeDriverManager
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except ImportError:
        return webdriver.Chrome(options=options) # Assumes chromedriver is in PATH

def fetch_page(driver, url, selector="body"):
    """Fetch a webpage and return its BeautifulSoup object."""
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        return BeautifulSoup(driver.page_source, "html.parser")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_chapter_links(soup, base_url="https://doc.rust-lang.org/book/"):
    """Extract chapter links and titles from the TOC."""
    chapters = soup.select("nav.sidebar a.chapter, ul.chapter a")
    if not chapters:
        sidebar = soup.find("nav", class_="sidebar") or soup.find("div", class_="sidebar")
        if sidebar:
            chapters = sidebar.find_all("a")

    chapter_info = []
    for chapter in chapters:
        title = chapter.get_text().strip()
        href = chapter.get("href", "")
        if title and not title.lower().startswith(("table of contents", "foreword", "introduction")):
            # Construct full URL if href is relative
            full_url = base_url + href if href.startswith("ch") else href
            chapter_info.append({"title": title, "url": full_url})

    return chapter_info

def extract_chapter_content(soup):
    """Extract the main content of a chapter, excluding headers, footers, and navigation."""
    # Target the main content area (mdBook typically uses <main> or <div class="content">)
    main_content = soup.find("main") or soup.find("div", class_="content")
    if not main_content:
        return ""

    # Extract text from paragraphs, code blocks, and other relevant elements
    content_elements = main_content.find_all(["p", "pre", "li", "h2", "h3"])
    content_parts = []

    for element in content_elements:
        text = element.get_text().strip()
        if text and not element.find_parent("nav"):  # Exclude navigation elements
            content_parts.append(text)

    # Join content and clean up excessive whitespace
    content = " ".join(content_parts)
    content = re.sub(r'\s+', ' ', content).strip()
    return content

def process_chapters(driver, chapter_info):
    """Process each chapter to extract its content."""
    all_contents = []
    chapter_contents_list = []

    for i, chapter in enumerate(chapter_info, 1):
        print(f"Fetching content for chapter {i}: {chapter['title']}...")
        soup = fetch_page(driver, chapter["url"], "main, div.content")
        if soup:
            content = extract_chapter_content(soup)
            if content:
                chapter_contents_list.append(content)
                all_contents.append(content)
            else:
                print(f"No content extracted for {chapter['title']}.")
        else:
            print(f"Failed to load page for {chapter['title']}.")

    return " ".join(all_contents), chapter_contents_list

def main():
    url = "https://doc.rust-lang.org/book/"
    driver = setup_driver()

    try:
        # Fetch the main page
        soup = fetch_page(driver, url, "nav.sidebar, ul.chapter")
        if not soup:
            print("Failed to load the main page.")
            return

        # Get chapter links
        chapter_info = get_chapter_links(soup)
        if not chapter_info:
            print("Could not find any chapter links.")
            print("Debugging info: Printing first 500 characters of parsed HTML...")
            print(str(soup)[:500])
            return

        # Process chapters to get contents
        all_contents_string, chapter_contents_list = process_chapters(driver, chapter_info)

        if chapter_contents_list:
            # Output results
            print("\nSingle string of all chapter contents (truncated to 500 characters):")
            print(all_contents_string[:500] + "..." if len(all_contents_string) > 500 else all_contents_string)
            print("\nList of individual chapter contents:")
            for i, content in enumerate(chapter_contents_list, 1):
                print(f"\nChapter {i} (truncated to 200 characters):")
                print(content[:200] + "..." if len(content) > 200 else content)
        else:
            print("No chapter contents extracted.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
