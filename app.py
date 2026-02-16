import streamlit as st
import os
import requests
import json
import time
from PIL import Image
from dotenv import load_dotenv

from streamlit_local_storage import LocalStorage
import datetime

load_dotenv()

st.set_page_config(page_title="AI Virtual Try-On", page_icon="🤖", layout="wide")

localS = LocalStorage()

env_api_key = os.getenv("NANOBANANA_API_KEY")
stored_api_key = localS.getItem("NANOBANANA_API_KEY")

api_key = env_api_key if env_api_key else stored_api_key

if not api_key:
    st.warning("API Key not found in environment or local storage.")
    st.markdown("### 🍌 Enter your NanoBanana API Key")
    st.markdown("You can get your API key from [NanoBanana API](https://nanobananaapi.ai/).")
    
    user_input_key = st.text_input("API Key", type="password")
    
    if st.button("Save API Key"):
        if user_input_key:
            localS.setItem("NANOBANANA_API_KEY", user_input_key)
            st.success("API Key saved! Reloading...")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Please enter a valid key.")
    st.stop()


col1, col2 = st.columns(2)

# Supported ratios mapping
SUPPORTED_RATIOS = {
    "1:1": 1.0,
    "9:16": 9/16,   # 0.5625
    "16:9": 16/9,   # 1.778
    "3:4": 3/4,     # 0.75
    "4:3": 4/3,     # 1.333
    "3:2": 3/2,     # 1.5
    "2:3": 2/3,     # 0.666
    "5:4": 5/4,     # 1.25
    "4:5": 4/5,     # 0.8
    "21:9": 21/9    # 2.333
}

def get_closest_ratio(width, height):
    target_ratio = width / height
    closest_ratio_str = "3:4" 
    min_diff = float('inf')
    
    for ratio_str, ratio_val in SUPPORTED_RATIOS.items():
        diff = abs(target_ratio - ratio_val)
        if diff < min_diff:
            min_diff = diff
            closest_ratio_str = ratio_str
            
    return closest_ratio_str

with col1:
    st.subheader("1. Person")
    person_image_file = st.file_uploader("Upload Person Image", type=["jpg", "jpeg", "png"], key="person")
    if person_image_file:
        st.image(person_image_file, caption="Person Reference", use_container_width=True)



with col2:
    st.subheader("2. Clothing")
    cloth_image_file = st.file_uploader("Upload Cloth Image", type=["jpg", "jpeg", "png"], key="cloth")
    if cloth_image_file:
        st.image(cloth_image_file, caption="Cloth Reference", use_container_width=True)

def upload_to_tmpfiles(file_obj):
    try:
        file_obj.seek(0)
        files = {'file': (file_obj.name, file_obj, file_obj.type)}
        response = requests.post('https://tmpfiles.org/api/v1/upload', files=files)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                url = data['data']['url']
                raw_url = url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                return raw_url
        
        st.error(f"Upload failed service response: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        st.error(f"Upload exception: {e}")
        return None

if st.button("Generate Result", type="primary"):
    if not api_key:
        st.error("API configuration error. Please check environment variables.")
    
    elif not person_image_file or not cloth_image_file:
         st.error("Please upload both Person and Cloth images.")
         
    else:
        try:
            with st.spinner("Processing images..."):
                st.write("Uploading images to secure host...")
                
                person_url = upload_to_tmpfiles(person_image_file)
                if not person_url:
                    st.error("Failed to upload Person image. Please try again.")
                    st.stop()
                    
                cloth_url = upload_to_tmpfiles(cloth_image_file)
                if not cloth_url:
                    st.error("Failed to upload Cloth image. Please try again.")
                    st.stop()
                
                generate_url = "https://api.nanobananaapi.ai/api/v1/nanobanana/generate"
                
                target_size = "3:4" 
                try:
                    person_image_file.seek(0) 
                    img = Image.open(person_image_file)
                    w, h = img.size
                    target_size = get_closest_ratio(w, h)
                except Exception as e:
                    st.warning(f"Could not detect image size, using default {target_size}. Error: {e}")

                full_prompt = f"""
Use the uploaded person image and the uploaded clothing image.

Goal: Replace only the clothing on the person with the uploaded clothing item.

Rules:
- Keep the person's face, body, pose, expression, hair, and proportions exactly the same.
- Keep the background, lighting, shadows, and camera angle unchanged.
- Do NOT modify skin tone, body shape, posture, or environment.
- Do NOT enhance, beautify, stylize, or edit anything else.
- Do NOT change fabric texture, color, logo, or design of the clothing.
- Preserve realistic wrinkles, folds, and natural fit.

Task:
Place the uploaded clothing naturally on the person as if they are wearing it.

Output:
A photorealistic image where only the clothing is changed.
Everything else must match the original person image perfectly.
High resolution, ultra-realistic.
"""
                
                payload = {
                    "prompt": full_prompt,
                    "numImages": 1,
                    "type": "IMAGETOIAMGE", 
                    "imageUrls": [person_url, cloth_url],
                    "image_size": target_size,
                    "callBackUrl": "https://example.com/callback"
                }
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }

                response = requests.post(generate_url, json=payload, headers=headers)
                
                if response.status_code != 200:
                    st.error(f"Task Creation Failed: {response.text}")
                    st.stop()
                
                res_json = response.json()
                if res_json.get("code") != 200:
                     st.error(f"Execution Error: {res_json.get('msg')}")
                     st.stop()
                     
                task_id = res_json.get("data", {}).get("taskId")
                if not task_id:
                    st.error("No Task ID returned.")
                    st.stop()
                
            poll_url = "https://api.nanobananaapi.ai/api/v1/nanobanana/record-info"
            
            with st.status("Generating High-Fidelity Result...", expanded=True) as status:
                st.write("Initializing secure model...")
                
                max_retries = 60
                for i in range(max_retries):
                    time.sleep(2)
                    
                    poll_res = requests.get(poll_url, params={"taskId": task_id}, headers=headers)
                    
                    if poll_res.status_code != 200:
                        continue
                        
                    poll_data = poll_res.json()
                    
                    success_flag = poll_data.get("data", {}).get("successFlag")
                    
                    if success_flag == 1:
                        status.update(label="Generation Complete!", state="complete", expanded=False)
                        st.balloons()
                        
                        result_url = poll_data["data"]["response"].get("resultImageUrl")
                        origin_url = poll_data["data"]["response"].get("originImageUrl")
                        
                        final_url = result_url if result_url else origin_url
                        
                        st.markdown("### ✨ Final Result")
                        st.image(final_url)
                        
                        try:
                            img_response = requests.get(final_url)
                            if img_response.status_code == 200:
                                st.download_button(
                                    label="Download Image",
                                    data=img_response.content,
                                    file_name="tryon_result.png",
                                    mime="image/png"
                                )
                        except Exception as e:
                            st.warning(f"Could not prepare download: {e}")
                        break
                        
                    elif success_flag == 0:
                        st.write(f"Processing... ({i+1}%)")
                        
                    elif success_flag in [2, 3]:
                        status.update(label="Generation Failed", state="error")
                        st.error("Model processing failed. Please try different images.")
                        break
                else:
                    st.error("Request timed out.")
                    
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

st.markdown("---")

with st.sidebar:
    st.header("Developer Credits")
    st.markdown("""
    **Developer:** Anubhav  
    ### Aka hex47i
    **Website:** [anubhavnath.dev](https://anubhavnath.dev)
    """)
    st.header("Tech Stack")
    st.markdown("""
    **Libraries:** Streamlit, Requests, Pillow  
    
    **APIs:** NanoBanana API, Tmpfiles.org
    """)



