import urllib.request
import io
import ssl
import os
from PIL import Image
from transformers import pipeline

os.environ['HF_HUB_ENABLE_HF_TRANSFER'] = '0'
ssl._create_default_https_context = ssl._create_unverified_context

def download_image(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    return Image.open(io.BytesIO(response.read())).convert('RGB')

def run_tests():
    print('Downloading test images...', flush=True)
    try:
        real_img = download_image('https://raw.githubusercontent.com/opencv/opencv/master/samples/data/lena.jpg')
        # This is a public URL to an AI-generated image
        fake_img = download_image('https://upload.wikimedia.org/wikipedia/commons/e/ea/Dog_-_AI-generated.jpg')
        print('Images downloaded successfully.', flush=True)
    except Exception as e:
        print('Error downloading images:', e, flush=True)
        return

    models_to_test = [
        'umm-maybe/AI-image-detector',
        'Organika/sdxl-detector',
        'jacoballessio/ai-image-detect-distilled',
        'Nahrawy/AI_Image_Detector'
    ]

    for model_name in models_to_test:
        print(f'\n--- Testing Model: {model_name} ---', flush=True)
        try:
            classifier = pipeline('image-classification', model=model_name)
            
            real_pred = classifier(real_img)
            print(f'Real Image Prediction: {real_pred}', flush=True)
            
            fake_pred = classifier(fake_img)
            print(f'Fake Image Prediction: {fake_pred}', flush=True)
        except Exception as e:
            print(f'Failed to test {model_name}: {e}', flush=True)

if __name__ == '__main__':
    run_tests()
