# CanvasToon API Integration

???꾨줈?앺듃??CanvasToon_Builder??3媛吏 ?대?吏 ?앹꽦 API瑜??듯빀?⑸땲??

- **Replicate Z-Image Turbo** (Text-to-Image)
- **AIML Kling Image O1** (Image-to-Image Collage)
- **AIML NanoBanana** (Image-to-Image Edit)

## ?? Quick Start

### 1. ?섍꼍 ?ㅼ젙
```bash
# ?⑦궎吏 ?ㅼ튂
pip install -r requirements.txt

# .env ?뚯씪??API ???낅젰
# REPLICATE_API_TOKEN=your_token_here
# AIML_API_KEY=your_key_here
```

### 2. ?뚯뒪???ㅽ뻾
```bash
# Z-Image Turbo (Replicate)
python tests/test_z_image_custom.py

# Kling O1 (AIML)
python tests/test_kling_o1_debug.py

# NanoBanana (AIML)
python tests/test_aiml_i2i_nanobanana.py
```

### 3. ?곸꽭 媛?대뱶
?꾩껜 ?ъ슜 諛⑸쾿? [API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md) 李몄“

## ?뱥 API ??諛쒓툒
- **AIML API**: https://aimlapi.com/
- **Replicate**: https://replicate.com/

## ?좑툘 二쇱쓽?ы빆
- .env ?뚯씪? ?덈? Git??而ㅻ컠?섏? 留덉꽭??
- ?뚯뒪???뚯씪 ??寃쎈줈???ㅼ젣 ?꾨줈?앺듃??留욊쾶 ?섏젙?섏꽭??
