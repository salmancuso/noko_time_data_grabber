import requests
import pandas as pd
import time
from typing import List, Dict
from config import HEADERS, baseUrl

def fetch_api_data(page: int) -> List[Dict]:
    url = f"{baseUrl}?page={page}" if page > 0 else baseUrl
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        print(f"Successfully fetched data from page {page}.")
        return response.json()
    else:
        print(f"Failed to fetch data from page {page}. Status code: {response.status_code}")
        return []

def mainAPIpull():  
    all_data = []
    page = 1

    while True:
        entries = fetch_api_data(page)
        if not entries:
            break

        all_data.extend(entries)
        page += 1
        time.sleep(.125)  # Rate limiting

    #### FOR TEST ONLY  
    # entries = fetch_api_data(page)
    # all_data.extend(entries)
    
    df = pd.json_normalize(all_data)
    df.columns = df.columns.str.replace('entry.', '')

    columns_to_drop = [
        'project_id', 'time_from', 'time_to', 'user_id', 'url', 'billable',
        'invoiced_at', 'invoice_id', 'description_text', 'import_id',
        'description', 'money_status', 'billable_status', 'project.id', 'tags'
    ]
    
    df = df.drop(columns=columns_to_drop, errors='ignore')
    df.columns = [col.replace('project.name', 'project_name') for col in df.columns]
    timeToInclude = ["1-Maintenance/Operations", "2-Service Requests","3-Projects","4-Planning/Optimization/Continuous Improvement","5-Professional Development/Growth","6-Administrative Activities/Overhead"]
    df = df[df['project_name'].isin(timeToInclude)]
    return df