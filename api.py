import os
import random
import yt_dlp
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Isse hamari website bina kisi error ke backend se baat kar payegi

# 1. Free Proxy Pool (Yahan hum kuch working free public proxies ki list rakhte hain)
# Future me tool down na ho, isiliye har request par inme se ek random IP choose hogi
PROXY_POOL = [
    "http://45.77.55.122:8080",
    "http://198.211.121.34:3128",
    "http://167.172.184.23:80",
    "http://206.189.231.11:8080"
]

@app.route('/extract', methods=['POST'])
def extract_video():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"success": False, "error": "URL missing hai!"}), 400

    # Ek random proxy select karna taaki Instagram block na kare
    selected_proxy = random.choice(PROXY_POOL)

    # 2. yt-dlp ki advanced settings (Bina video download kiye sirf link nikalne ke liye)
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Sabse achhi quality
        'quiet': True,                         # Faltu logs band karne ke liye
        'no_warnings': True,
        'proxy': selected_proxy,               # Proxy yahan apply ho gayi
        'http_headers': {                      # Instagram ko lage ki ek normal mobile user browser chala raha hai
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # extract_info() se bina video download kiye saari details mil jaati hain
            info = ydl.extract_info(url, download=False)
            
            # Direct MP4 stream URL nikalna
            video_url = info.get('url') or info.get('entries')[0].get('url')
            title = info.get('title', 'Social Media Video')
            
            return jsonify({
                "success": True,
                "title": title,
                "download_link": video_url
            })
            
    except Exception as e:
        # Agar koi proxy kharab ho ya block ho jaye, to error handle karne ke liye
        return jsonify({
            "success": False, 
            "error": "Server temporary busy hai, please ek baar phir try karein!"
        }), 500

if __name__ == '__main__':
    app.run(debug=True)