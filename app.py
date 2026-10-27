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
        # တည်ငြိမ်ပြီး အလုပ်လုပ်သော Cobalt API ကို အသုံးပြုခြင်း
        api_url = "https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "vQuality": "720"  # လိုချင်သော Quality (ဥပမာ- 720p)
        }

        response = requests.post(api_url, json=payload, headers=headers, timeout=20)
        
        try:
            res_data = response.json()
        except Exception:
            return jsonify({'success': False, 'error': f'API Server Error (Status {response.status_code})'})

        # Cobalt API ရဲ့ Response ပုံစံအရ စစ်ဆေးခြင်း
        status = res_data.get('status')
        if status in ['stream', 'redirect', 'picker']:
            download_url = res_data.get('url', '')
            
            # အကယ်၍ picker ပုံစံဖြစ်နေပါက options များထဲမှ ပထမဆုံး URL ကို ယူမည်
            if not download_url and 'picker' in res_data:
                picker_items = res_data.get('picker', [])
                if picker_items:
                    download_url = picker_items[0].get('url', '')

            if not download_url:
                return jsonify({'success': False, 'error': 'Download Link ရှာမတွေ့ပါ။'})

            return jsonify({
                'success': True,
                'title': 'YouTube Video',
                'thumbnail': '',
                'download_url': download_url,
            })
        else:
            err_msg = res_data.get('text', 'ဗီဒီယိုအချက်အလက် ရယူ၍မရပါ။')
            return jsonify({'success': False, 'error': f'API Error: {err_msg}'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
