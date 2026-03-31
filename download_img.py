import os
import requests
import re
import urllib.parse
from PIL import Image
from io import BytesIO
import time
from generate_fukuoka import parse_md

def download_all():
    if not os.path.exists('deploy-fukuoka/images'):
        os.makedirs('deploy-fukuoka/images')

    sections = parse_md()
    
    for sec in sections:
        for item in sec['items']:
            ja_name = item['ja_name']
            signature = ""
            if 'menu_items' in item and len(item['menu_items']) > 0:
                signature = item['menu_items'][0].split('—')[0].split('(')[0].strip()
            
            query = f"福岡 {ja_name} {signature}"
            print(f"Search: {query}")
            
            img_path = f"deploy-fukuoka/images/{ja_name}.jpeg"
            if os.path.exists(img_path):
                print(f" -> Already exists: {img_path}")
                continue
                
            try:
                q = urllib.parse.quote(query)
                url = f"https://search.yahoo.co.jp/image/search?p={q}"
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
                html = requests.get(url, headers=headers, timeout=10).text
                
                # Yahoo Image search JSON structure in HTML
                matches = re.findall(r'"original":\s*\{\s*"url":\s*"([^"]+)"', html)
                
                success = False
                for img_url in matches[:5]:
                    if not img_url: continue
                    if img_url.startswith('x-raw-image'): continue
                    print(f"  Trying {img_url}")
                    try:
                        response = requests.get(img_url, headers=headers, timeout=8)
                        if response.status_code == 200:
                            content_type = response.headers.get('Content-Type', '')
                            if 'html' in content_type:
                                continue
                            
                            val = response.content
                            img = Image.open(BytesIO(val))
                            img = img.convert('RGB')
                            img.thumbnail((1200, 1200))
                            img.save(img_path, 'JPEG', quality=85)
                            success = True
                            print(f" -> Saved {img_path}")
                            break
                    except Exception as e:
                        pass
                
                if not success:
                    print(f" -> Failed to download for {ja_name}")
            except Exception as e:
                print(f" -> Yahoo Search Error on {ja_name}: {e}")
            
            time.sleep(1)

if __name__ == "__main__":
    download_all()
