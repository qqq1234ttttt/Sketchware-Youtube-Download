import os
import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__, template_folder='.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_info')
def get_info():
    url = request.args.get('url', '')
    if not url:
        return jsonify({'success': False, 'error': 'Link မပါဝင်ပါ။'})

    try:
        # လက်ရှိအလုပ်လုပ်နေသော Public YouTube Downloader API ကို ချိတ်ဆက်ခြင်း
        api_url = f"https://apis.davidcyriltech.my.id/youtube/dl?url={url}"
        
        response = requests.get(api_url, timeout=25)
        res_data = response.json()

        # API ရဲ့ Response အခြေအနေကို စစ်ဆေးခြင်း
        if res_data and 'status' in res_data and res_data['status'] == 200:
            result_info = res_data.get('result', {})
            download_url = result_info.get('download_url', '') or result_info.get('url', '')
            video_title = result_info.get('title', 'KMT YouTube Download')

            if not download_url:
                return jsonify({'success': False, 'error': 'Download Link ရှာမတွေ့ပါ။'})

            return jsonify({
                'success': True,
                'title': video_title,
                'thumbnail': result_info.get('thumbnail', ''),
                'download_url': download_url,
            })
        else:
            err_msg = res_data.get('message', 'ဗီဒီယိုအချက်အလက် ရယူ၍မရပါ။')
            return jsonify({'success': False, 'error': f'API Error: {err_msg}'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
