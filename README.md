### WARNING: THIS DOCUMENTATION IS GENERATED BY AI, IT MAY CONTAIN ERRORS. PLEASE VERIFY THE CONTENTS.

# WebCrawler
### Step 1: Install Required Dependencies

```bash
# Install all required packages
pip install beautifulsoup4 requests pandas
```

### Step 2: Set Up Project Structure

Create the following directory structure for the project:

```bash
mkdir -p Data/Temp LinkData/Error LinkData/VisitedLink Error
```

Or the library will automatically create these directories when needed.

## File Structure and Key Components

The library is organized into four main classes, each with specific responsibilities:

```
WebScraper.py
├── Extractor - Extracts content from HTML
├── HTMLParser - Fetches and parses web pages
├── DataSaver - Saves data to files
└── Collector - High-level methods combining other components
```

### Directory Structure Created by the Library

```
.
├── Data/
│   ├── Temp/ - Temporary files during batch processing
│   └── (extracted content files)
├── LinkData/
│   ├── Error/ - Failed link processing logs
│   ├── VisitedLink/ - Successfully processed links
│   └── (link collection files)
└── WebScraper.py - Main library file
```

## Classes and Methods

### Extractor

The `Extractor` class is responsible for extracting specific content (text, tags, paragraphs, links) from HTML content using BeautifulSoup.

#### Private Methods:

- `__contains_bangla(text: str) -> bool`: Uses regex pattern `[\u0980-\u09FF]` to detect Bangla Unicode characters.
- `__clean_text(text: str) -> str`: Removes excess whitespace, newlines, and tabs.

#### Public Methods:

- `get_tags(soup, tags, min_length=20, bangla_only=True)`: Extracts content from specific HTML tags.
  - **Parameters**:
    - `soup`: BeautifulSoup object
    - `tags`: List of HTML tag names (e.g., ['h1', 'p'])
    - `min_length`: Minimum character length to include (default: 20)
    - `bangla_only`: Whether to only include text with Bangla characters (default: True)
  - **Returns**: List of extracted text strings

- `get_selectors(soup, selectors, min_length=20, bangla_only=True)`: Extract content using CSS selectors.
  - **Parameters**:
    - `soup`: BeautifulSoup object
    - `selectors`: List of CSS selectors (e.g., ['div.content', 'article.main'])
    - `min_length`: Minimum character length to include (default: 20)
    - `bangla_only`: Whether to only include text with Bangla characters (default: True)
  - **Returns**: List of extracted text strings

- `get_para(soup, container_selector=None, min_words=20, bangla_only=True)`: Extract paragraphs.
  - **Parameters**:
    - `soup`: BeautifulSoup object
    - `container_selector`: Optional CSS selector to narrow search area
    - `min_words`: Minimum word count to include (default: 20)
    - `bangla_only`: Whether to only include text with Bangla characters (default: True)
  - **Returns**: List of paragraph texts

- `get_all_links(soup, container_selector=None, should_contain=None)`: Extract hyperlinks.
  - **Parameters**:
    - `soup`: BeautifulSoup object
    - `container_selector`: Optional CSS selector to narrow search area
    - `should_contain`: Optional string that links must contain
  - **Returns**: List of unique URLs

### HTMLParser

The `HTMLParser` class manages fetching and parsing of web pages with robust error handling.

#### Private Methods:

- `__get_html_from_url(url, headers=None, proxies=None)`: Fetches HTML content from URLs.
- `__get_soup_from_html(html_content)`: Converts HTML string to BeautifulSoup object.

#### Public Methods:

- `get_soup(url, headers=None, proxies=None)`: Fetch a URL and return a BeautifulSoup object.
  - **Parameters**:
    - `url`: Target website URL
    - `headers`: Optional custom HTTP headers dictionary
    - `proxies`: Optional proxy configuration dictionary
  - **Returns**: BeautifulSoup object

### DataSaver

The `DataSaver` class handles saving extracted data to various file formats with proper directory structure creation.

#### Private Methods:

- `__create_directory(filepath)`: Creates necessary directories for a file path.

#### Public Methods:

- `save_csv(paragraphs, filepath, source_url, append=False)`: Save paragraphs to CSV.
  - **Parameters**:
    - `paragraphs`: List of text strings to save
    - `filepath`: Target CSV file path
    - `source_url`: URL source of the data
    - `append`: Whether to append to existing file (default: False)
  - **Returns**: File path of saved CSV

- `save_excel(paragraphs, filepath, source_url, sheet_name='Paragraphs', append=False)`: Save to Excel.
  - **Parameters**:
    - `paragraphs`: List of text strings to save
    - `filepath`: Target Excel file path
    - `source_url`: URL source of the data
    - `sheet_name`: Excel sheet name (default: 'Paragraphs')
    - `append`: Whether to append to existing file (default: False)
  - **Returns**: File path of saved Excel file

- `save_csv_links(links, filepath, append=False)`: Save links to CSV.
  - **Parameters**:
    - `links`: List of URLs to save
    - `filepath`: Target CSV file path
    - `append`: Whether to append to existing file (default: False)
  - **Returns**: File path of saved CSV

### Collector

The `Collector` class provides high-level methods that combine extraction and saving with advanced functionality for web crawling and batch processing.

#### Private Methods:

- `__read_links_from_csv(file_path)`: Reads and validates links from a CSV file.

#### Public Methods:

- `LinkParseAndAdd(url, filename, should_contain=None, container_selector=None, source=None)`: Extract and save links.
  - **Parameters**:
    - `url`: Target website URL
    - `filename`: Output CSV file path
    - `should_contain`: Optional filter string for links
    - `container_selector`: Optional CSS selector to narrow search area
    - `source`: Optional source identifier

- `ParseAndAdd(url, filename, container_selector=None)`: Extract and save paragraphs.
  - **Parameters**:
    - `url`: Target website URL
    - `filename`: Output CSV file path
    - `container_selector`: Optional CSS selector to narrow search area

- `CrawlAnd_AddLinks(baseUrl, unvisitedFile, shouldContain=None, container_selector=None)`: Crawl a website recursively.
  - **Parameters**:
    - `baseUrl`: Starting URL for crawling
    - `unvisitedFile`: CSV file to store found links
    - `shouldContain`: Optional filter string for links (default: baseUrl)
    - `container_selector`: Optional CSS selector to narrow search area

- `ParseAndAdd_FromCSV(file, storeLocation, container_selector=None, batch_size=20)`: Process URLs from a CSV file.
  - **Parameters**:
    - `file`: CSV file containing URLs to process
    - `storeLocation`: Output CSV file path
    - `container_selector`: Optional CSS selector for content extraction
    - `batch_size`: Number of URLs to process in each batch (default: 20)

## Usage Instructions

### Scraping a Single Webpage

Extract paragraphs from a specific webpage and save them to a CSV file:

```python
from WebScraper import Collector, HTMLParser, Extractor, DataSaver

# Method 1: Using high-level Collector class
url = "https://example.com/blog-post"
output_file = "extracted_data.csv"
container_selector = "div.content-area"  # Narrow down to main content area

# Extract and save paragraphs with special tags marking start/end
Collector.ParseAndAdd(url, output_file, container_selector)

# Method 2: Using component classes directly for more control
url = "https://example.com/blog-post"
soup = HTMLParser.get_soup(url)

# Extract paragraphs with at least 50 words containing Bangla text
paragraphs = Extractor.get_para(
    soup, 
    container_selector="div.content-area", 
    min_words=50, 
    bangla_only=True
)

# Save to CSV with source URL information
DataSaver.save_csv(
    paragraphs, 
    "./Data/custom_extracted_data.csv", 
    source_url=url,
    append=True  # Add to existing file if present
)
```

### Collecting Links

Extract all links from a webpage and save them to a CSV file:

```python
from WebScraper import Collector

# Method 1: Basic link extraction
url = "https://example.com"
links_file = "./LinkData/site_links.csv"

# Only collect links containing specific text (e.g., to filter by domain or section)
should_contain = "example.com/blog"

# Extract and save links
Collector.LinkParseAndAdd(url, links_file, should_contain)

# Method 2: With container selector to focus on specific area
url = "https://example.com/category"
links_file = "./LinkData/category_links.csv"
should_contain = "example.com/product"
container_selector = "div.product-listing"  # Only get links from product listing

# Extract and save links with source identification
Collector.LinkParseAndAdd(url, links_file, should_contain, container_selector, source="Category Page")
```

### Crawling Entire Websites

Recursively crawl a website and collect all links that match criteria:

```python
from WebScraper import Collector

# Start crawling from the base URL
base_url = "https://example.com"

# Where to store the discovered links
links_file = "./LinkData/all_site_links.csv"

# Filter to keep only links within the specific domain or pattern
should_contain = "example.com"

# Optional container to focus crawling
container_selector = "main.content"

# Begin crawling process
Collector.CrawlAnd_AddLinks(base_url, links_file, should_contain, container_selector)
```

### Batch Processing from CSV

Process a list of URLs from a CSV file in batches to extract content:

```python
from WebScraper import Collector

# CSV file containing URLs in the first column
input_file = "./LinkData/blog_links.csv"

# File to store the extracted content
output_file = "./Data/blog_content.csv"

# Optional container selector to focus on content area
container_selector = "article.post-content"

# Process URLs in batches of 10
batch_size = 10

# Begin batch processing
Collector.ParseAndAdd_FromCSV(input_file, output_file, container_selector, batch_size)
```
