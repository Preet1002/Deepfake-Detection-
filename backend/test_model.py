import sys
print("Hello world", flush=True)

try:
    from transformers import pipeline
    print("Transformers loaded", flush=True)
    classifier = pipeline('image-classification', model='dima806/deepfake_vs_real_image_detection')
    print("Pipeline loaded", flush=True)
except Exception as e:
    print(f"Error: {e}", flush=True)
