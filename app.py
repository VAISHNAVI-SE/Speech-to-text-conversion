import os
import datetime
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='public')

# Ensure the data directory exists for storing transcriptions
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'transcriptions')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/save-transcription', methods=['POST'])
def save_transcription():
    """API endpoint to save transcription data"""
    try:
        data = request.get_json()
        transcription = data.get('transcription', '').strip()
        language = data.get('language', 'en-US')
        
        if not transcription:
            return jsonify({
                'success': False,
                'message': 'No transcription provided'
            }), 400
        
        # Generate a unique filename with timestamp and language
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcription_{timestamp}_{language}.txt"
        filepath = os.path.join(data_dir, filename)
        
        # Save the transcription to a file with language metadata
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(f"Language: {language}\n\n{transcription}")
        
        return jsonify({
            'success': True,
            'message': 'Transcription saved successfully',
            'filename': filename
        })
    
    except Exception as e:
        print(f"Error saving transcription: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to save transcription: {str(e)}'
        }), 500

@app.route('/api/transcriptions', methods=['GET'])
def get_transcriptions():
    """API endpoint to get all saved transcriptions"""
    try:
        transcriptions = []
        
        # Sort files by modification time, newest first
        files = sorted(
            [f for f in os.listdir(data_dir) if f.startswith('transcription_')],
            key=lambda x: os.path.getmtime(os.path.join(data_dir, x)),
            reverse=True
        )
        
        for file in files:
            filepath = os.path.join(data_dir, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract date and language from filename
            parts = file.replace('transcription_', '').replace('.txt', '').split('_')
            date_str = f"{parts[0][:4]}-{parts[0][4:6]}-{parts[0][6:]} {parts[1][:2]}:{parts[1][2:4]}:{parts[1][4:]}"
            language = parts[2] if len(parts) > 2 else 'en-US'
            
            transcriptions.append({
                'filename': file,
                'date': date_str,
                'language': language,
                'content': content.split('\n\n', 1)[1] if '\n\n' in content else content
            })
        
        return jsonify({
            'success': True,
            'transcriptions': transcriptions
        })
    
    except Exception as e:
        print(f"Error retrieving transcriptions: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve transcriptions: {str(e)}'
        }), 500

@app.route('/api/delete-transcription/<filename>', methods=['DELETE'])
def delete_transcription(filename):
    """API endpoint to delete a specific transcription"""
    try:
        filepath = os.path.join(data_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'message': 'Transcription not found'
            }), 404
        
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Transcription deleted successfully'
        })
    
    except Exception as e:
        print(f"Error deleting transcription: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to delete transcription: {str(e)}'
        }), 500

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return "Page not found", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)