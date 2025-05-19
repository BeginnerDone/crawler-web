import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image

class ImageCrawler:
    def __init__(self, config_path='config.json'):
        self.config = self.load_config(config_path)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.774tuba.cc/'
        })
        
    def load_config(self, config_path):
        if not os.path.exists(config_path):
            default_config = {
                "target_url": "https://www.774tuba.cc/html/11/61347.html",
                "save_dir": "./downloads"
            }
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config
        
        with open(config_path) as f:
            return json.load(f)
    
    def download_image(self, url, save_path):
        try:
            print(f"正在尝试下载: {url}")
            response = self.session.get(url, stream=True, timeout=10)
            
            if response.status_code != 200:
                print(f"下载失败: HTTP状态码 {response.status_code}")
                return False
                
            try:
                # 先保存临时文件
                temp_path = save_path + '.temp'
                with open(temp_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        if not chunk:  # 检查空块
                            print(f"下载中断: {url}")
                            return False
                        f.write(chunk)
                
                # 处理水印
                try:
                    img = Image.open(temp_path)
                    width, height = img.size
                    # 裁剪掉左下角15%的区域
                    crop_height = int(height * 0.15)
                    img = img.crop((0, 0, width, height - crop_height))
                    img.save(save_path)
                    os.remove(temp_path)
                except Exception as e:
                    print(f"水印处理失败: {e}")
                    os.rename(temp_path, save_path)
                
                print(f"成功保存到: {save_path}")
                return True
            except IOError as e:
                print(f"文件保存失败: {save_path}, 错误: {e}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"网络请求失败: {url}, 错误: {e}")
        except Exception as e:
            print(f"未知错误: {url}, 错误: {e}")
        return False
    
    def crawl(self):
        os.makedirs(self.config['save_dir'], exist_ok=True)
        
        try:
            response = self.session.get(self.config['target_url'])
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            content_div = soup.find('div', class_='content')
            if not content_div:
                print("未找到class为content的容器")
                return
                
            img_tags = content_div.find_all('img')
            if not img_tags:
                print("未找到图片")
                return
                
            print(f"找到 {len(img_tags)} 张图片")
            
            for i, img in enumerate(img_tags, 1):
                img_url = img.get('src')
                if not img_url:
                    continue
                    
                if not img_url.startswith('http'):
                    img_url = urljoin(self.config['target_url'], img_url)
                    
                ext = os.path.splitext(img_url)[1] or '.jpg'
                save_path = os.path.join(self.config['save_dir'], f"image_{i}{ext}")
                
                print(f"正在下载第 {i} 张: {img_url}")
                if self.download_image(img_url, save_path):
                    print(f"已保存到: {save_path}")
                
        except Exception as e:
            print(f"爬取失败: {e}")

if __name__ == '__main__':
    crawler = ImageCrawler()
    crawler.crawl()