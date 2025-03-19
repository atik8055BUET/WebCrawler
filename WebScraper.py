from bs4 import BeautifulSoup
from typing import List, Optional
import re
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import csv
import os
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
import time

class Extractor:
    __bangla_pattern = re.compile(r'[\u0980-\u09FF]')
    
    @staticmethod
    def __contains_bangla(text: str) -> bool:
        return bool(Extractor.__bangla_pattern.search(text))
    
    @staticmethod
    def __clean_text(text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\r\n\t]', ' ', text)
        return text.strip()
    
    @staticmethod
    def get_tags(soup: BeautifulSoup, tags: List[str], min_length: int = 0, bangla_only: bool = True) -> List[str]:
        if not soup:
            raise ValueError("No soup object provided")
        
        results = []
        for tag_name in tags:
            elements = soup.find_all(tag_name)
            for element in elements:
                text = Extractor.__clean_text(element.get_text())
                if len(text) >= min_length and (not bangla_only or Extractor.__contains_bangla(text)):
                    results.append(text)
        return results
    
    @staticmethod
    def get_selectors(soup: BeautifulSoup, selectors: List[str], min_length: int = 0, bangla_only: bool = True) -> List[str]:
        if not soup:
            raise ValueError("No soup object provided")
        
        results = []
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = Extractor.__clean_text(element.get_text())
                if len(text) >= min_length and (not bangla_only or Extractor.__contains_bangla(text)):
                    results.append(text)
        return results
    
    @staticmethod
    def get_para(soup: BeautifulSoup, container_selector: Optional[str] = None, min_words: int = 0, bangla_only: bool = True) -> List[str]:
        if not soup:
            raise ValueError("No soup object provided")
        
        container = soup.select_one(container_selector) if container_selector else soup
        
        paragraphs = []
        for p in container.find_all('p'):
            text = Extractor.__clean_text(p.get_text())
            word_count = len(text.split())
            
            if word_count >= min_words and (not bangla_only or Extractor.__contains_bangla(text)):
                paragraphs.append(text)
        return paragraphs
    
    @staticmethod
    def get_all_links(soup: BeautifulSoup, container_selector: Optional[str] = None,should_contain=None) -> List[str]:
        if not soup:
            raise ValueError("No soup object provided")
        
        container = soup.select_one(container_selector) if container_selector else soup
        links = []
        for a in container.find_all('a', href=True):
            link = a['href']
            if(should_contain is not None):
                if link.startswith("http://") or link.startswith("https://"):
                    if(link.find(should_contain) != -1):
                        if link not in links:
                            links.append(link)
            elif(should_contain is None):
                if(link.startswith("http://") or link.startswith("https://")):
                    if link not in links:
                        links.append(link)
            
        return links

class HTMLParser:
    __DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    @staticmethod
    def __get_html_from_url(url: str, headers: Optional[Dict[str, str]] = None, proxies: Optional[Dict[str, str]] = None) -> str:
        if not url:
            raise ValueError("No URL provided")

        request_headers = HTMLParser.__DEFAULT_HEADERS.copy()
        if headers:
            request_headers.update(headers)
            
        try:
            response = requests.get(
                url, 
                headers=request_headers,
                proxies=proxies,
                timeout=30
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise e
    
    @staticmethod
    def __get_soup_from_html(html_content: str) -> BeautifulSoup:
        if not html_content:
            raise ValueError("No HTML content to parse")
        
        return BeautifulSoup(html_content, 'html.parser')
    
    @staticmethod
    def get_soup(url: str, headers: Optional[Dict[str, str]] = None, proxies: Optional[Dict[str, str]] = None) -> BeautifulSoup:
        html_content = HTMLParser.__get_html_from_url(url, headers, proxies)
        return HTMLParser.__get_soup_from_html(html_content)

class DataSaver:
    @staticmethod
    def __create_directory(filepath: str) -> None:
        """Create directory if it doesn't exist."""
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
    @staticmethod
    def save_csv(paragraphs: List[str], filepath: str, source_url: str, append: bool = False) -> str:
        DataSaver.__create_directory(filepath)

        rows = []
        date = datetime.now().date().isoformat()
        
        for paragraph in paragraphs:
            rows.append([paragraph, source_url, date])
        
        mode = 'a' if append and os.path.exists(filepath) else 'w'
        write_headers = not (append and os.path.exists(filepath) and os.path.getsize(filepath) > 0)
        
        with open(filepath, mode, newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if write_headers:
                writer.writerow(["text", "source_url", "date"])
            writer.writerows(rows)
        
        return filepath
    
    @staticmethod
    def save_excel(paragraphs: List[str], filepath: str, 
                source_url: str,
                sheet_name: str = 'Paragraphs',
                append: bool = False) -> str:
        DataSaver.__create_directory(filepath)
        
        data = {
            "text": paragraphs,
            "source_url": [source_url] * len(paragraphs),
            "date": [datetime.now().date().isoformat()] * len(paragraphs)
        }
        
        df_new = pd.DataFrame(data)
        
        if append and os.path.exists(filepath):
            try:
                with pd.ExcelWriter(filepath, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                    try:
                        df_existing = pd.read_excel(filepath, sheet_name=sheet_name)
                        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                        df_combined.to_excel(writer, sheet_name=sheet_name, index=False)
                    except:
                        df_new.to_excel(writer, sheet_name=sheet_name, index=False)
            except Exception as e:
                df_new.to_excel(filepath, sheet_name=sheet_name, index=False)
        else:
            df_new.to_excel(filepath, sheet_name=sheet_name, index=False)
        
        return filepath
    
    @staticmethod
    def save_csv_links(links: List[str], filepath: str, append: bool = False) -> str:
        DataSaver.__create_directory(filepath)

        rows = []
        
        for link in links:
            rows.append([link])
        
        mode = 'a' if append and os.path.exists(filepath) else 'w'
        write_headers = not (append and os.path.exists(filepath) and os.path.getsize(filepath) > 0)
        
        with open(filepath, mode, newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if write_headers:
                writer.writerow(["link"])
            writer.writerows(rows)
        
        return filepath
    
class Collector:
    @staticmethod
    def __read_links_from_csv(file_path: str) -> set[str]:
        """Read links from a CSV file and return them as a set."""
        try:
            df = pd.read_csv(file_path, on_bad_lines='skip')
            links = set(df.iloc[:, 0].tolist())
            links = {link for link in links if link.startswith("http://") or link.startswith("https://")}
            return links
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")
    
    @staticmethod
    def LinkParseAndAdd(BaseUrl,LinkFile,should_contain=None,container_selector: Optional[str] = None,source=None):
        """ Parse and add links from a given URL to a CSV file."""
        soup=HTMLParser.get_soup(BaseUrl)
        linklist = Extractor.get_all_links(soup, container_selector=container_selector, should_contain=should_contain)
    
        if source is not None:
            startingparser="<#START-LINK-ASTHA#> "+source
        else :
            startingparser="<#START-LINK-ASTHA#>"
        endingparser="<#END-LINK-ASTHA#>"
        linklist.insert(0,startingparser)
        linklist.append(endingparser)
        if LinkFile.find("./LinkData/") == -1:
            LinkFile="./LinkData/"+LinkFile
        DataSaver.save_csv_links(linklist, LinkFile, append=True)
        
    @staticmethod
    def ParseAndAdd(BaseUrl,DataFile,container_selector: Optional[str] = None):
        """ Parse and add paragraphs from a given URL to a CSV file."""
        soup=HTMLParser.get_soup(BaseUrl)
        dataList=Extractor.get_para(soup,bangla_only=True, container_selector=container_selector)
        if dataList==[]:
            raise Exception("No Bangla text found...")
        try:
            heading=Extractor.get_tags(soup, ["h1"], min_length=1, bangla_only=True)
            startingparser="<#START-ASTHA#> "+heading[0]
        except Exception as e:
            startingparser="<#START-ASTHA#> Heading not found"
        endingparser="<#END-ASTHA#>"
        dataList.insert(0,startingparser)
        dataList.append(endingparser)
        
        if DataFile.find("./Data/") == -1:
            DataFile="./Data/"+DataFile
        DataSaver.save_csv(dataList, DataFile, append=True, source_url=BaseUrl)
            
    @staticmethod        
    def CrawlAnd_AddLinks(BaseUrl,LinkFile:str,should_contain=None, container_selector: Optional[str] = None):
        """ Crawl a website and store all the sub-links of the given URL."""
        if(should_contain is None):
            should_contain=BaseUrl
            
        os.makedirs("./LinkData/Error", exist_ok=True)
        os.makedirs(os.path.dirname(LinkFile), exist_ok=True)
        try:
            seen_links = set(Collector.__read_links_from_csv(LinkFile))
        except Exception as e:
            seen_links = set()
            
        new_links = {BaseUrl}
        # new_links = set(new_links)
        all_links = seen_links.union(new_links)
        
        while new_links:
            try:
                current_link = new_links.pop()
                print(f"Crawling: {current_link}")
                current_link=str(current_link)
                soup= HTMLParser.get_soup(current_link)
                child_links = Extractor.get_all_links(soup, should_contain=should_contain,container_selector=container_selector)
                child_links= set(child_links)
                
                new_found_links = child_links.difference(all_links)
                
                if new_found_links:
                    DataSaver.save_csv_links(links=new_found_links, filepath=LinkFile, append=True)
                    new_links.update(new_found_links)
                
                all_links.update(new_found_links)
            except Exception as e:
                print(f"Error crawling {current_link}: {e}")
                with open("./LinkData/Error/errorLink.txt", "a") as f:
                    f.write(current_link + "\n")
                continue        
            time.sleep(1)
            
                
    @staticmethod
    def ParseAndAdd_FromCSV(LinkFile, DataFile, container_selector: Optional[str] = None, batch_size: int = 20):
        """ Parse and add paragraphs from a CSV file containing URLs in batches."""
        if not os.path.exists(LinkFile):
            raise ValueError(f"File {LinkFile} does not exist")
        
        os.makedirs("./Data", exist_ok=True)
        os.makedirs("./LinkData", exist_ok=True)
        os.makedirs("./LinkData/Error", exist_ok=True)
        os.makedirs("./LinkData/VisitedLink", exist_ok=True)
        os.makedirs("./Data/Temp", exist_ok=True)
        visited_file = f"./LinkData/VisitedLink/visited.csv"
        temp_file = f"./Data/Temp/temp.csv"
        error_file = f"./LinkData/Error/errorLink.txt"
        
        try:
            df= pd.read_csv(LinkFile, on_bad_lines='skip')
            all_links = set(df.iloc[:, 0].tolist())
            total_links = len(all_links)
            print(f"Found {total_links} links to process")
                        
            for i in range(0, len(all_links), batch_size):
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                    with open(temp_file, "w", encoding='utf-8') as f:
                        f.write("text,source_url,date\n")
                    
                    visited_links = []
                    end_index = min(i + batch_size, total_links)
                    batch_links = list(all_links)[i:end_index]
                    print(f"Processing batch {i//batch_size + 1} ({len(batch_links)} links)")

                    for link in batch_links:
                        print(f"Processing link: {link}")
                        try:
                            Collector.ParseAndAdd(link, temp_file, container_selector=container_selector)
                            visited_links.append(link)
                        except Exception as e:
                            print(f"Error processing link {link}: {e}")
                            with open(error_file, "a", encoding='utf-8') as f:
                                f.write(f"{link}\n")
                            continue
                    
                    if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                        if not os.path.exists(DataFile):
                            with open(DataFile, "w", encoding='utf-8') as f:
                                f.write("text,source_url,date\n")
                                
                        with open(temp_file, "r", encoding='utf-8') as temp_f:
                            content = temp_f.readlines()
                            if len(content) > 1:
                                with open(DataFile, "a", encoding='utf-8') as main_f:
                                    for line in content[1:]:
                                        main_f.write(line)
                    
                    if visited_links:
                        visited_df = pd.DataFrame({"link": visited_links})
                        if os.path.exists(visited_file):
                            visited_df.to_csv(visited_file, mode='a', header=False, index=False, encoding='utf-8')
                        else:
                            visited_df.to_csv(visited_file, index=False, encoding='utf-8')
                        try:
                            current_df = pd.read_csv(LinkFile)
                            updated_df = current_df[~current_df.iloc[:, 0].isin(visited_links)]
                            updated_df.to_csv(LinkFile, index=False, encoding='utf-8')
                        except Exception as e:
                            print(f"Error updating original file: {e}")
                            
                except Exception as e:
                    print(f"Error processing batch {i//batch_size + 1}: {e}")
                    continue
                time.sleep(1)
                
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            raise ValueError(f"Error reading CSV file: {e}")