import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

working_models = []
print("Testing models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        try:
            model = genai.GenerativeModel(m.name)
            response = model.generate_content("Say 'hi'")
            print(f"✅ {m.name} WORKS: {response.text.strip()}")
            working_models.append(m.name)
            break # Just need one!
        except Exception as e:
            print(f"❌ {m.name} FAILED: {str(e)[:50]}")

if working_models:
    print(f"\nFOUND WORKING MODEL: {working_models[0]}")
else:
    print("\nNO MODELS WORKED WITH THIS API KEY.")
