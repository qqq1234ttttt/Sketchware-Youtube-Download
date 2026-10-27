import os
from flask import Flask, jsonify, render_template, request
from yt_dlp import YoutubeDL

# template_folder='.' ကြောင့် GitHub Root ထဲရှိ index.html ကို တိုက်ရိုက်ဖတ်ယူပါမည်
app = Flask(__name__, template_folder='.')


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/get_info')
def get_info():
  url = request.args.get('url', '')
  if not url:
    return jsonify({'success': False, 'error': 'Link မပါဝင်ပါ။'})

  ydl_opts = {'extract_flat': False, 'skip_download': True}
  try:
    with YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=False)
      video_title = info.get('title', 'YouTube Video')
      thumbnail_url = info.get('thumbnail', '')

      # Direct Download stream url ရယူရန်
      formats = info.get('formats', [])
      best_url = ''
      for f in formats:
        if (
            f.get('ext') == 'mp4'
            and f.get('vcodec') != 'none'
            and f.get('acodec') != 'none'
        ):
          best_url = f.get('url')
          break
      if not best_url and formats:
        best_url = formats[0].get('url')

      return jsonify({
          'success': True,
          'title': video_title,
          'thumbnail': thumbnail_url,
          'download_url': best_url,
      })
  except Exception as e:
    return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
