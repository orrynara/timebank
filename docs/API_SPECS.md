# CanvasToon Builder API Integration Specifications (v1.0)

This document defines the technical specifications, cost structures, and implementation guides for AI models integrated into CanvasToon Builder via the Replicate Platform.

---

## 1. Replicate Platform Overview

* **Service:** Managed AI Model Hosting & Inference
* **Billing:** Per-second billing based on GPU hardware usage.
* **Hardware Cost Tiers:**
    * **CPU:** $0.000100/sec
    * **Nvidia T4:** $0.000225/sec (approx. $0.81/hr) - *Used for lightweight models*
    * **Nvidia A40:** $0.000575/sec (approx. $2.07/hr) - *Standard generation*
    * **Nvidia A100 (80GB):** $0.001400/sec (approx. $5.04/hr) - *High-end Video/LLM*
    * **Nvidia H100:** $0.001525/sec (approx. $5.49/hr) - *Flagship Video models*

---

## 2. Model Specifications

### A. PrunaAI Z-Image Turbo
* **Model ID:** `prunaai/z-image-turbo`
* **Type:** Text-to-Image (Hyper-Fast)
* **Est. Time:** 0.4s ~ 0.8s
* **Est. Cost:** < $0.001 (Negligible)
* **Best For:** Storyboarding, Ideation, Rapid Prototyping

#### Implementation
```python
import replicate

# Input Schema
input_data = {
    "prompt": "A storyboard sketch of a K-pop idol dancing, rough pencil style",
    "num_inference_steps": 4,  # Turbo specific
    "guidance_scale": 0.0,
    "height": 768,
    "width": 768
}

output = replicate.run("prunaai/z-image-turbo", input=input_data)
# Returns: List of output URIs







# CanvasToon Builder API Integration Specifications (v1.0)

This document defines the technical specifications, cost structures, and implementation guides for ALL AI models integrated into CanvasToon Builder.



## 1. Provider Overview

### 🅰️ AIML API
* **Role:** Text Generation (LLM) & Main Image Generation
* **Base URL:** `https://api.aimlapi.com/v1` (compatible with OpenAI SDK)
* **Billing:** Per token (LLM) or Per image generated.
* **Key Models:** GPT-4o, NanoBanana Pro

### 🅱️ Replicate Platform
* **Role:** Video Generation, Fast Image Preview, Utility (Inpainting)
* **Billing:** Per-second billing based on GPU hardware usage.
* **Key Models:** Hailuo, Seedance, Veo, Z-Image, LaMa

---

## 2. Text & Scenario (LLM)

### 🔹 GPT-4o
* **Provider:** **AIML API**
* **Model ID:** `gpt-4o`
* **Type:** LLM (Text Generation)
* **Role:** Scenario writing, Prompt engineering (Image/Video prompts)
* **Cost:** Input $5.00 / Output $15.00 (per 1M tokens)

#### Implementation (OpenAI SDK)
```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("AIML_API_KEY"),
    base_url="[https://api.aimlapi.com/v1](https://api.aimlapi.com/v1)"
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Create a video prompt..."}]
)
print(response.choices[0].message.content)
````

-----

## 3\. Image Generation Models

### 🔹 NanoBanana Pro (Main)

  * **Provider:** **AIML API**
  * **Model ID:** `google/nano-banana-pro` (Gemini 3 Pro based)
  * **Type:** Text-to-Image (High Quality)
  * **Role:** Generating main character cuts and final assets.
  * **Cost:** Approx. $0.04 \~ $0.08 per image

#### Implementation

```python
# Uses the same OpenAI-compatible client as GPT-4o
response = client.images.generate(
    model="google/nano-banana-pro",
    prompt="A detailed K-pop idol portrait...",
    size="1024x1792", # 9:16 aspect ratio
    n=1
)
print(response.data[0].url)
```

### 🔹 PrunaAI Z-Image Turbo (Preview)

  * **Provider:** **Replicate**
  * **Model ID:** `prunaai/z-image-turbo`
  * **Type:** Text-to-Image (Hyper-Fast)
  * **Role:** Rapid prototyping, Storyboarding, Idea sketches.
  * **Est. Time:** 0.4s \~ 0.8s
  * **Est. Cost:** \< $0.001 (Negligible)

#### Implementation

```python
import replicate

output = replicate.run(
    "prunaai/z-image-turbo",
    input={
        "prompt": "Rough sketch of a scene...",
        "num_inference_steps": 4,
        "height": 768, "width": 768
    }
)
# Returns: List of output URIs
```

-----

## 4\. Image Utility Models

### 🔹 Allenhooo LaMa

  * **Provider:** **Replicate**
  * **Model ID:** `allenhooo/lama`
  * **Type:** Image Inpainting / Watermark Removal
  * **Role:** Cleaning up text artifacts, logos, or unwanted objects.
  * **Est. Time:** 2s \~ 5s
  * **Est. Cost:** \~$0.002

#### Implementation

```python
import replicate

output = replicate.run(
    "allenhooo/lama",
    input={
        "image": open("path/to/original.png", "rb"),
        "mask": open("path/to/mask.png", "rb")
    }
)
# Returns: URI of cleaned image
```

-----

## 5\. Video Generation Models

### 🔹 MiniMax Hailuo 2.3 Fast (Action)

  * **Provider:** **Replicate**
  * **Model ID:** `minimax/hailuo-2.3-fast`
  * **Type:** Image-to-Video
  * **Role:** High-speed action scenes, Dynamic camera movements.
  * **Spec:** 10 seconds duration.
  * **Est. Cost:** \~$0.34 (for 10s)
  * **Key Param:** Uses `first_frame_image`.

#### Implementation

```python
import replicate

output = replicate.run(
    "minimax/hailuo-2.3-fast",
    input={
        "prompt": "Cyberpunk character running fast...",
        "first_frame_image": open("path/to/start.png", "rb"),
        "duration": 10
    }
)
```

### 🔹 Bytedance Seedance 1.0 Pro Fast (Motion)

  * **Provider:** **Replicate**
  * **Model ID:** `bytedance/seedance-1-pro-fast`
  * **Type:** Image-to-Video
  * **Role:** Character performance, Dancing, Walking (Human Motion).
  * **Spec:** 10 seconds duration.
  * **Est. Cost:** \~$0.60 (for 10s)
  * **Key Param:** Uses `source_image`.

#### Implementation

```python
import replicate

output = replicate.run(
    "bytedance/seedance-1-pro-fast",
    input={
        "prompt": "Girl dancing smoothly...",
        "source_image": open("path/to/character.png", "rb"),
        "width": 720, "height": 1280,
        "duration": 10,
        "fps": 24
    }
)
```

### 🔹 Google Veo 3.1 Fast (Cinematic)

  * **Provider:** **Replicate**
  * **Model ID:** `google/veo-3.1-fast`
  * **Type:** Image-to-Video
  * **Role:** Cinematic intros, Emotional scenes, High consistency.
  * **Spec:** 8 seconds duration (Fixed).
  * **Est. Cost:** \~$1.20 (for 8s)
  * **Key Param:** Uses `image`.

#### Implementation

```python
import replicate

output = replicate.run(
    "google/veo-3.1-fast",
    input={
        "prompt": "Cinematic dolly in...",
        "image": open("path/to/start.png", "rb"),
        "resolution": "720p",
        "aspect_ratio": "9:16"
    }
)


# CanvasToon Builder API Integration Specifications (v1.1)

This document defines the technical specifications, cost structures, and implementation guides for ALL AI models integrated into CanvasToon Builder.

---

## 1. Provider Overview

### 🅰️ AIML API (Primary - High Credits Available)
* **Role:** Text (LLM), Main Image Gen, **Action Video Gen**
* **Base URL:** `https://api.aimlapi.com`
* **Billing:** Per token or Per generation.
* **Key Models:** `gpt-4o`, `google/nano-banana-pro`, `minimax/hailuo-2.3-fast`

### 🅱️ Replicate Platform (Secondary)
* **Role:** Motion Video, Cinematic Video, Utility
* **Billing:** Per-second billing (GPU).
* **Key Models:** `bytedance/seedance-1-pro-fast`, `google/veo-3.1-fast`, `prunaai/z-image-turbo`, `allenhooo/lama`

---

## 2. Text & Scenario (AIML API)

### 🔹 GPT-4o
* **Provider:** **AIML API**
* **Model ID:** `gpt-4o`
* **Type:** LLM (Text Generation)
* **Role:** Scenario writing, Prompt engineering.
* **Cost:** ~$5.00 / 1M input tokens.

#### Implementation
```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("AIML_API_KEY"),
    base_url="[https://api.aimlapi.com/v1](https://api.aimlapi.com/v1)"
)
# Standard Chat Completion

3. Image Generation Models
🔹 NanoBanana Pro (Main)
Provider: AIML API

Model ID: google/nano-banana-pro

Type: Text-to-Image (High Quality)

Cost: ~$0.04 - $0.08 / image

Endpoint: v1/images/generations (OpenAI Compatible)

🔹 PrunaAI Z-Image Turbo (Preview)
Provider: Replicate

Model ID: prunaai/z-image-turbo

Type: Text-to-Image (Hyper-Fast)

Cost: < $0.001

4. Video Generation Models
🔹 MiniMax Hailuo 2.3 Fast (Action)
Provider: AIML API

Model ID: minimax/hailuo-2.3-fast

Type: Image-to-Video

Role: High-speed action, 10s duration.

Cost: Uses AIML Credits.

Endpoint: v2/video/generations

import requests
import os

url = "[https://api.aimlapi.com/v2/video/generations](https://api.aimlapi.com/v2/video/generations)"
payload = {
    "model": "minimax/hailuo-2.3-fast",
    "prompt": "Action scene...",
    "image_url": "data:image/jpeg;base64,...", # Requires Base64 or URL
    "duration": "10",
    "aspect_ratio": "9:16"
}
headers = {
    "Authorization": f"Bearer {os.getenv('AIML_API_KEY')}",
    "Content-Type": "application/json"
}
response = requests.post(url, json=payload, headers=headers)
# Returns: {"id": "...", "video_url": "..."} (Async or Sync depending on API)

🔹 Bytedance Seedance 1.0 Pro Fast (Motion)
Provider: Replicate

Model ID: bytedance/seedance-1-pro-fast

Type: Image-to-Video

Role: Character dance/motion.

Spec: 10 seconds.

🔹 Google Veo 3.1 Fast (Cinematic)
Provider: Replicate

Model ID: google/veo-3.1-fast

Type: Image-to-Video

Role: Cinematic intros.

Spec: 8 seconds.

5. Image Utility (Replicate)
🔹 Allenhooo LaMa
Provider: Replicate

Model ID: allenhooo/lama

Role: Inpainting / Watermark Removal.

