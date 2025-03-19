from WebScraper import Collector

# Base URL of the website to be crawled
BaseUrl="https://www.shajgoj.com/"

# file paths for storing links
LinkFile="./LinkData/linkData1.csv"

# file paths for storing scraped data
DataFile="./Data/trainData.csv"

# the keyword to filter the links
should_contain="https://www.shajgoj.com/"

# the CSS selector to filter the links
container_selector=None


# Crawl The full Website and store all the links in a CSV file
# Collector.CrawlAnd_AddLinks(BaseUrl=BaseUrl,LinkFile=LinkFile,should_contain=should_contain,container_selector=container_selector)

# Scrape the data from the links in the CSV file and store it in a CSV file
# Collector.ParseAndAdd_FromCSV(LinkFile=LinkFile,DataFile=DataFile,container_selector=container_selector,batch_size=10)

# Crawl a single webpage and store the links in a CSV file
# Collector.LinkParseAndAdd(BaseUrl=BaseUrl,LinkFile=LinkFile,should_contain=should_contain,container_selector=container_selector)

# Scrape the data from a single webpage and store it in a CSV file
# Collector.ParseAndAdd(BaseUrl=BaseUrl,DataFile=DataFile,container_selector=container_selector)