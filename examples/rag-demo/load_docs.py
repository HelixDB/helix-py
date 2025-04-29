from transformers.utils.dummy_pt_objects import RagSequenceForGeneration
import helix
from helix.client import ragloaddocs, ragsearchdoc, ragtestload
from typing import Tuple, List, Any

# idk why I needed this but works better
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from transformers import BertTokenizer, BertModel
import torch
from tqdm import tqdm
import json
import os

DATA_FILE = "data/rust_book_data.json"

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertModel.from_pretrained("bert-base-uncased")

def save_to_json(data: List[Tuple[str, str]], filename: str=DATA_FILE):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_from_json(filename: str=DATA_FILE) -> List[Tuple[str, str]]:
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def setup_driver():
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
            # Use urljoin to handle relative and absolute URLs correctly
            full_url = urljoin(base_url, href)
            chapter_info.append({"title": title, "url": full_url})

    return chapter_info

def extract_chapter_content(soup):
    main_content = soup.find("main") or soup.find("div", class_="content")
    if not main_content:
        return ""

    content_elements = main_content.find_all(["p", "pre", "li", "h2", "h3"])
    content_parts = []

    for element in content_elements:
        text = element.get_text().strip()
        if text and not element.find_parent("nav"):
            content_parts.append(text)

    content = " ".join(content_parts)
    content = re.sub(r'\s+', ' ', content).strip()
    return content

def process_chapters(driver, chapter_info):
    chapter_data = []

    for i, chapter in enumerate(chapter_info, 1):
        print(f"Fetching content for chapter {i}: {chapter['title']}...")
        soup = fetch_page(driver, chapter["url"], "main, div.content")
        if soup:
            content = extract_chapter_content(soup)
            if content:
                chapter_data.append((chapter['title'], content))
            else:
                print(f"No content extracted for {chapter['title']}.")
        else:
            print(f"Failed to load page for {chapter['title']}.")

    return chapter_data

def fetch_rust_book_chapters() -> List[Any]:
    url = "https://doc.rust-lang.org/book/"
    driver = setup_driver()

    if os.path.exists(DATA_FILE):
        print(f"fetching from already saved data in: {DATA_FILE}")
        return load_from_json(DATA_FILE)

    try:
        soup = fetch_page(driver, url, "nav.sidebar, ul.chapter")
        if not soup:
            print("Failed to load the main page.")
            return []

        chapter_info = get_chapter_links(soup)
        if not chapter_info:
            print("Could not find any chapter links.")
            print("Debugging info: Printing first 500 characters of parsed HTML...")
            print(str(soup)[:500])
            return []

        chapter_data = process_chapters(driver, chapter_info)
        save_to_json(chapter_data, DATA_FILE)
        return chapter_data
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        driver.quit()

def chunk_content(text: str, chunk_size: int=200) -> List[str]:
    # chunk size in words
    text = ' '.join(text.split()).strip()

    sentences = [s.strip() for s in text.split('.') if s.strip()]
    sentences = [s + '.' for s in sentences]

    chunks = []
    current_chunk = ""
    current_word_count = 0

    for sentence in sentences:
        sentence_word_count = len(sentence.split())

        if current_word_count + sentence_word_count > chunk_size:
            if current_chunk:  # Only append non-empty chunks
                chunks.append(current_chunk.strip())
            current_chunk = sentence
            current_word_count = sentence_word_count
        else:
            current_chunk += sentence
            current_word_count += sentence_word_count

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def vectorize_chunked(chunked: List[str]) -> List[List[float]]:
    # embedding model and shit
    # embedding dims: 768
    vectorized = []
    for chunk in chunked:
        inputs = tokenizer(chunk, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
            embedding = outputs.last_hidden_state[:, 0, :].squeeze().tolist()
            vectorized.append(embedding)
    return vectorized

def process_to_vectorized(chapters: List[Tuple[str, str]]) -> List[Tuple[str, List[List[float]]]]:
    ret = []
    for title, content in tqdm(chapters, desc="processing chapters"):
        chunked = chunk_content(content)
        vectorized = vectorize_chunked(chunked)
        ret.append((content, vectorized)) # add chunked as well for properties
    return ret

if __name__ == "__main__":
    db = helix.Client(local=True)

    chapters = fetch_rust_book_chapters()
    processed = process_to_vectorized(chapters[:40])
    for doc, vecs in tqdm(processed):
        db.query(ragloaddocs([(doc, vecs)]))

    #import numpy as np
    #db.query(ragtestload("POO", np.arange(768, dtype=float).tolist()))

    #db.query(ragtestload("PEEEEE", [2, 2, 2, 2, 2]))
    #res = db.query(ragsearchdoc([3, 3, 3, 3, 3]))
    #print(res)

    #db.query(ragloaddocs([("POOOOOOOP 2.0", [[1, 1, 1, 1, 1]])]))
    #res = db.query(ragsearchdoc([0, 0, 0, 0, 0]))
    #print("res:", res)