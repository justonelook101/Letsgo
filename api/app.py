from flask import Flask, request, redirect, url_for, render_template_string
import os
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '../static/videos'
app.config['IMAGE_FOLDER'] = '../static/images'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'jpg', 'png', 'webp', 'gif'}

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['IMAGE_FOLDER'], exist_ok=True)

def allowed_file(filename, extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

@app.route('/', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        video = request.files.get('video')
        image = request.files.get('image')
        
        if video and allowed_file(video.filename, {'mp4'}) and image and allowed_file(image.filename, {'jpg', 'png', 'webp', 'gif'}):
            vid_id = str(uuid.uuid4())
            video_ext = 'mp4'
            image_ext = image.filename.rsplit('.', 1)[1].lower()
            
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{vid_id}.{video_ext}')
            image_path = os.path.join(app.config['IMAGE_FOLDER'], f'{vid_id}.{image_ext}')
            
            video.save(video_path)
            image.save(image_path)
            
            return redirect(url_for('video_page', vid_id=vid_id))
    
    return '''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload Video</title>
    </head>
    <body>
        <h1>Upload a Video and Thumbnail Image</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="video" accept="video/mp4" required>
            <input type="file" name="image" accept="image/jpeg,image/png,image/webp,image/gif" required>
            <input type="submit" value="Upload">
        </form>
    </body>
    </html>
    '''

@app.route('/video/<vid_id>')
def video_page(vid_id):
    image_ext = next((ext for ext in ['jpg', 'png', 'webp', 'gif'] if os.path.exists(os.path.join(app.config['IMAGE_FOLDER'], f'{vid_id}.{ext}'))), None)
    if not image_ext:
        return "Image not found", 404
    
    player_url = f"https://{request.host}/player/{vid_id}"
    image_url = f"https://{request.host}/static/images/{vid_id}.{image_ext}"
    
    twitter_site = '@yourusername'  # Replace with your actual X handle
    title = f'Video {vid_id}'
    description = 'An uploaded video'
    width = 640
    height = 360
    
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <meta name="twitter:card" content="player">
        <meta name="twitter:site" content="{twitter_site}">
        <meta name="twitter:title" content="{title}">
        <meta name="twitter:description" content="{description}">
        <meta name="twitter:image" content="{image_url}">
        <meta name="twitter:player" content="{player_url}">
        <meta name="twitter:player:width" content="{width}">
        <meta name="twitter:player:height" content="{height}">
    </head>
    <body>
        <h1>{title}</h1>
        <p>Share this link on X to see the Player Card.</p>
        <iframe src="{player_url}" width="{width}" height="{height}" frameborder="0"></iframe>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/player/<vid_id>')
def player(vid_id):
    video_path = f'/static/videos/{vid_id}.mp4'
    image_ext = next((ext for ext in ['jpg', 'png', 'webp', 'gif'] if os.path.exists(os.path.join(app.config['IMAGE_FOLDER'], f'{vid_id}.{ext}'))), None)
    if not image_ext:
        return "Image not found", 404
    poster_url = f'/static/images/{vid_id}.{image_ext}'
    
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Video Player</title>
        <style>
            body {{ margin: 0; padding: 0; overflow: hidden; }}
            video {{ width: 100%; height: 100vh; object-fit: contain; }}
        </style>
    </head>
    <body>
        <video controls poster="{poster_url}">
            <source src="{video_path}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </body>
    </html>
    '''
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)
