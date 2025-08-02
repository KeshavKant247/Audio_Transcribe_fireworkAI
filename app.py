# import os
# import uuid
# import requests
# from flask import Flask, request, jsonify
# from openai import OpenAI

# # Replace this with your actual Fireworks API key
# FIREWORKS_API_KEY = "fw_3ZZTkpH2coFSZspjJQChc5d1"

# client = OpenAI(
#     base_url="https://audio-prod.us-virginia-1.direct.fireworks.ai/v1",
#     api_key=FIREWORKS_API_KEY
# )

# app = Flask(__name__)
# OUTPUT_DIR = "output"
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# @app.route('/transcribe', methods=['POST'])
# def translate_audio():
#     if not request.json or 'audio_url' not in request.json:
#         return jsonify({'error': 'Missing audio_url'}), 400

#     audio_url = request.json['audio_url']
#     filename = f"{uuid.uuid4()}.mp3"
#     audio_path = os.path.join(OUTPUT_DIR, filename)

#     try:
#         # Step 1: Download audio
#         response = requests.get(audio_url)
#         if response.status_code != 200:
#             return jsonify({'error': 'Audio download failed'}), 400

#         with open(audio_path, 'wb') as f:
#             f.write(response.content)

#         # Step 2: Transcribe + Translate
#         with open(audio_path, 'rb') as f:
#             result = client.audio.translations.create(
#                 model="whisper-v3",
#                 file=f
#             )
#         transcript = result.text

#     except Exception as e:
#         return jsonify({'error': f'Error: {str(e)}'}), 500

#     finally:
#         # Step 3: Clean up
#         if os.path.exists(audio_path):
#             os.remove(audio_path)

#     return jsonify({'translated_transcript': transcript})

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5009,debug=True)



from flask import Flask, request, jsonify
import os
import requests
import tempfile
from groq import Groq

app = Flask(__name__)
client = Groq(api_key="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")

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    data = request.get_json()
    audio_url = data.get("audio_url")

    if not audio_url:
        return jsonify({"error": "Missing 'audio_url' in request body"}), 400

    tmp_file_path = None

    try:
        # Step 1: Download audio
        response = requests.get(audio_url, stream=True)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(response.content)
            tmp_file_path = tmp_file.name

        # Step 2: Transcribe
        with open(tmp_file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(tmp_file_path), file.read()),
                model="whisper-large-v3",
                response_format="verbose_json",
            )

        # Step 3: Return only the text
        return jsonify({"transcript": transcription.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

if __name__ == "__main__":
    app.run(debug=True)