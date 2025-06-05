from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re
import json

options = Options()
options.add_argument("--headless") 

list_of_links = []
for term in ['Winter-2024', 'Summer-2024']:
    driver = webdriver.Chrome(options=options)
    page = 1
    while True:
        url = f"https://karakterstatistik.stads.ku.dk/#searchText=&term={term}&block=&institute=&faculty=1868&searchingCourses=true&page={page}"
        driver.get(url)
        driver.refresh()
        time.sleep(1)

        match = re.finditer(r'(?<=<a href=")[^"]*(?=[^>]*>(v24\/B1|v24/B2|s24\/B3|s24\/B4|s24\/B5))', driver.page_source)
        
        my_list = list(match)
        length = len(my_list)
        if length == 0:
            print(f'Page {page} loaded for {term}, no links found.')
            break
        print(f'Page {page} loaded for {term}, found {length} links.')
        for m in my_list:
            list_of_links.append(m.group(0))
        page += 1
        
        
        
driver = webdriver.Chrome(options=options)
print(f"Found {len(list_of_links)} links.")
data = []
for index, link in enumerate(list_of_links):
    driver.get(link)
    title = driver.find_element(By.TAG_NAME, "h2").text
    GPA = ""

    match = re.search(r'-?([0-9]*,)?[0-9]+(?= \(Efter 7-trinsskalaen\))', driver.page_source)
    
    if match:
        GPA = match.group(0)

    print(f'Title, GPA: {title}, {GPA} {index + 1}/{len(list_of_links)}')
    data.append({
        "link": link,
        "GPA": GPA,
        "title": title,
    })

with open('data.json', 'w') as f:
    json.dump(data, f, indent=4)
driver.quit()

