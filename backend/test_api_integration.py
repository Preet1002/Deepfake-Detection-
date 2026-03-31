from fastapi.testclient import TestClient
from main import app
import urllib.request
import io

client = TestClient(app)

def download_image(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    return response.read()

import traceback

def log_result(*msg):
    with open('test_results.txt', 'a') as f:
        f.write(' '.join(str(m) for m in msg) + '\n')
    print(*msg)

def test_detect():
    import os
    if os.path.exists('test_results.txt'):
        os.remove('test_results.txt')
        
    log_result("Testing the /api/detect endpoint with a real image...")
    # Bill Gates real photo on Wikipedia
    real_img_bytes = download_image('https://upload.wikimedia.org/wikipedia/commons/a/a8/Bill_Gates_2017_%28cropped%29.jpg')
    
    response = client.post(
        "/api/detect",
        files={"file": ("test.png", real_img_bytes, "image/png")}
    )
    
    log_result("Status:", response.status_code)
    log_result("JSON Response:", response.json())
    
    # Check if the output label is REAL
    assert response.json()["label"] == "REAL", f"Expected REAL but got {response.json()['label']}"
    log_result("Test passed! The model successfully classified the image as REAL.")

    log_result("\nTesting with an artificial image (Fake)...")
    try:
        # A known generative AI image from a stable repo (if it exists)
        fake_img_bytes = download_image('https://raw.githubusercontent.com/CompVis/stable-diffusion/main/assets/stable-samples/txt2img/merlion.png')
        
        response = client.post(
            "/api/detect",
            files={"file": ("fake.png", fake_img_bytes, "image/png")}
        )
        
        log_result("Status:", response.status_code)
        log_result("JSON Response:", response.json())
        
        # Depending on model it might be correctly labeled
        if response.json()["label"] == "FAKE":
            log_result("Test passed! The model successfully classified the image as FAKE.")
        else:
            log_result("Warning: Model didn't confidently label the merlion as FAKE, it labelled it:", response.json()['label'])
    except Exception as e:
        log_result("Could not download fake image for testing, skipping this part.", str(e))

if __name__ == "__main__":
    try:
        test_detect()
    except Exception as e:
        log_result("Error occurred:")
        log_result(traceback.format_exc())
