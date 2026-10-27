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
        # လက်ရှိအလုပ်လုပ်နေသော Cobalt Public Instance API သို့ ချိတ်ဆက်ခြင်း
        api_url = "https://co.wuk.sh/api/json"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "vQuality": "720"
        }

        response = requests.post(api_url, json=payload, headers=headers, timeout=25)
        
        if response.status_code != 200:
            return jsonify({'success': False, 'error': f'API Server Error (Status {response.status_code})'})

        try:
            res_data = response.json()
        except Exception:
            return jsonify({'success': False, 'error': 'API မှ Data မှန်ကန်စွာ မပြန်လာပါ။'})

        status = res_data.get('status')
        if status in ['stream', 'redirect', 'picker']:
            download_url = res_data.get('url', '')
            
            if not download_url and 'picker' in res_data:
                picker_items = res_data.get('picker', [])
                if picker_items:
                    download_url = picker_items[0].get('url', '')

            if not download_url:
                return jsonify({'success': False, 'error': 'Download Link ရှာမတွေ့ပါ။'})

            return jsonify({
                'success': True,
                'title': 'KMT YouTube Download',
                'thumbnail': '',
                'download_url': download_url,
            })
        else:
            err_msg = res_data.get('text', 'ဗီဒီယိုလင့်ခ် ရယူ၍မရပါ။')
            return jsonify({'success': False, 'error': f'API Error: {err_msg}'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
