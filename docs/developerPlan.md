# 개발 계획 (Developer Plan)

---

## 2025년 12월 29일

### Q1. PG 결제와 웹 호스팅 서버 추천 (Firebase vs Vercel?)

**추천:** Streamlit Community Cloud (초기) 또는 Railway / Render (실운영)

**이유:**

- **Vercel:** Next.js(자바스크립트)에 최적화되어 있습니다. Streamlit(파이썬)은 계속 실행되어야 하는 '런타임'이 필요한데, Vercel은 'Serverless'라 Streamlit 구동이 까다롭고 느립니다.

- **Firebase:** 정적 호스팅(HTML/CSS) 중심이라 파이썬 백엔드(Streamlit)를 돌리려면 설정이 복잡합니다.

**결론:** 초기에는 **Streamlit Cloud(무료)**에 배포해서 투자자에게 보여주고, 실제 결제(PG)를 붙여 안정적으로 돌리려면 Railway(월 5불 내외) 같은 Docker 기반 호스팅이 가장 쉽고 강력합니다.

---

### Q2. Thirdweb (Web3 지갑/SNS 로그인) 이식

**의견:** 매우 훌륭합니다. 타임뱅크는 "자산 소유" 개념이 있으므로 Web3 지갑 로그인은 사업 정체성과 완벽하게 맞습니다.

**전략:** 기존에 성공하신 로직이 있다면, `modules/auth_manager.py`를 만들어 해당 로직(API 호출 등)을 이식하면 됩니다. Streamlit에서도 JS 연동이나 쿠키 처리가 가능합니다.

---

### Q3 & Q4. PDF 상품안내서 활용 (이미지 변환)

**전략:** "PDF를 쪼개서 이미지로 만드는 것"이 훨씬 효율적입니다.

**이유:**

- AI는 PDF 전체를 읽는 것보다, 잘라진 이미지(`spec_page_01.jpg`, `interior_page_03.jpg`)를 인식하고 배치하는 것을 훨씬 잘합니다.

**이렇게 하세요:** 

1. PDF를 페이지별 고화질 이미지(PNG/JPG)로 변환한 뒤, `assets/products/z5_model/` 폴더에 넣어주세요.
2. 그다음 Roo Code에게 "z5_model 폴더의 1번 이미지는 스펙 설명 옆에, 2번 이미지는 인테리어 섹션에 넣어줘" 라고 하면 디자인이 확 살아납니다.

---

### Q5. 디자인 고도화 (백오피스 이후)

**전략:** Streamlit은 기본 디자인이 투박합니다. `assets/style.css` 파일을 만들어야 합니다.

**제안:**

- 타임뱅크 로고의 네온 블루 & 퍼플 컬러를 메인 테마로 잡으시죠.
- 버튼을 둥글게 깎고(Border-radius), 그림자(Shadow)를 넣어 입체감을 줍니다.
- 백오피스 기능 구현이 끝나면, 제가 `style.css` 코드를 짜서 전체 분위기를 "미래지향적 핀테크/호텔" 느낌으로 바꿔드리겠습니다.

---
