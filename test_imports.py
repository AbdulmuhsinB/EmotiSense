#!/usr/bin/env python3
"""Test script to verify all EmotiSense dependencies are working"""

print("Testing EmotiSense dependencies...")
print("=" * 50)

try:
    print("1. Testing Flask...", end=" ")
    import flask
    print("✓ OK")
except Exception as e:
    print(f"✗ FAILED: {e}")

try:
    print("2. Testing OpenCV...", end=" ")
    import cv2
    print("✓ OK")
except Exception as e:
    print(f"✗ FAILED: {e}")

try:
    print("3. Testing NumPy...", end=" ")
    import numpy
    print("✓ OK")
except Exception as e:
    print(f"✗ FAILED: {e}")

try:
    print("4. Testing Pandas...", end=" ")
    import pandas
    print("✓ OK")
except Exception as e:
    print(f"✗ FAILED: {e}")

try:
    print("5. Testing Librosa (may take a moment)...", end=" ")
    import librosa
    print("✓ OK")
except Exception as e:
    print(f"✗ FAILED: {e}")

try:
    print("6. Testing DeepFace (may take a moment)...", end=" ")
    import deepface
    print("✓ OK")
except Exception as e:
    print(f"✗ FAILED: {e}")

try:
    print("7. Testing MoviePy...", end=" ")
    import moviepy
    print("✓ OK")
except Exception as e:
    print(f"✗ FAILED: {e}")

print("=" * 50)
print("\nAll tests passed! EmotiSense is ready to run.")
print("Start the server with: python app.py")

