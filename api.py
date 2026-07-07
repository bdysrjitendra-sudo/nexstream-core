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

    # Advanced Bypass Settings for YouTube & Instagram
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        # YouTube bot detection bypass karne ke liye android client native check
        'extractor_args': {
            'youtube': {
                'player_client': ['android'],
                'skip': ['dash', 'hls']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }

    # Agar YouTube short ya video hai toh best single format uthane ke liye
    if "youtube.com" in url or "youtu.be" in url:
        ydl_opts['format'] = 'best[ext=mp4]/best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return jsonify({"success": False, "error": "Video data nahi mil paya!"}), 400

            # Video URL extract karne ka logic
            video_url = None
            if 'url' in info:
                video_url = info['url']
            elif 'formats' in info and len(info['formats']) > 0:
                # Filter out formats without video+audio combinations if possible, or grab the best available
                valid_formats = [f for f in info['formats'] if f.get('url')]
                if valid_formats:
                    video_url = valid_formats[-1].get('url')

            title = info.get('title', 'NexStream_Video')

            if not video_url:
                return jsonify({"success": False, "error": "Direct streaming link nahi mila!"}), 400

            return jsonify({
                "success": True,
                "title": title,
                "download_link": video_url
            })
            
    except Exception as e:
        error_msg = str(e)
        return jsonify({
            "success": False, 
            "error": f"Cloud Engine Error: {error_msg[:60]}..." 
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
