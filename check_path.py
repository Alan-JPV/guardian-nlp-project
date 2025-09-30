import os

# Use the path exactly as DVC is trying to find it
path = r'D:\Project btech related alan\Guardian-NLP\.dvc\gurdian-nlp-9a12a66ac0d3.json'

if os.path.exists(path):
    print("✅ SUCCESS: Python can find the file.")
else:
    print("❌ FAILED: Python CANNOT find the file. There might be a typo or permissions issue.")