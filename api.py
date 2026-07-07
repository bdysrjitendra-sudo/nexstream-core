import os
import yt_dlp
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/extract', methods=['POST'])
def extract_video():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON data!"}), 400
        
    url = data.get('url')
    if not url:
        return jsonify({"success": False, "error": "URL missing hai!"}), 400

    # Advanced Cloud-Optimized Settings (No heavy extraction)
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False, # Sirf link aur title nikalne ke liye
        'skip_download': True, # Video download bilkul nahi karni
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return jsonify({"success": False, "error": "Video data nahi mil paya!"}), 400

            # Direct video stream URL structure check karna
            video_url = None
            if 'url' in info:
                video_url = info['url']
            elif 'formats' in info and len(info['formats']) > 0:
                # Sabse best quality format ka link nikalna
                video_url = info['formats'][-1].get('url')

            title = info.get('title', 'NexStream_Video')

            if not video_url:
                return jsonify({"success": False, "error": "Direct MP4 link extract nahi ho saka!"}), 400

            return jsonify({
                "success": True,
                "title": title,
                "download_link": video_url
            })
            
    except Exception as e:
        # Asli error check karne ke liye string me convert kiya
        error_msg = str(e)
        print("Ytdl Error:", error_msg) # Vercel Logs me dikhega
        
        return jsonify({
            "success": False, 
            "error": f"Cloud Engine Error: {error_msg[:50]}..." 
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
