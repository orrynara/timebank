from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import sys
import time
import requests

def main():
    # 1. 환경 설정
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set in .env")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # 2. 경로 설정
    INPUT_IMAGE_PATH = r"D:\coding 2025\timebank\assets\generated\flash_image_lotteworld.png"
    OUTPUT_VIDEO_PATH = r"D:\coding 2025\timebank\assets\generated\veo31_lotteworld.mp4"
    MODEL_ID = "veo-3.1-generate-preview"
    
    PROMPT_TEXT = "롯데월드에서 솜사탕을 들고 있는 kpop 여자 아이돌이 카메라를 향해 천천히 걸어오는 16:9 영상, 자연스러운 조명, 영화 같은 카메라 무빙, 짧은 인트로 샷"

    if not os.path.exists(INPUT_IMAGE_PATH):
        print(f"Error: Input image not found at {INPUT_IMAGE_PATH}")
        sys.exit(1)

    print(f"Reading image: {INPUT_IMAGE_PATH}")
    with open(INPUT_IMAGE_PATH, "rb") as f:
        image_bytes = f.read()

    print(f"Requesting video generation with model: {MODEL_ID}")
    
    try:
        # 사용자 가이드에 따른 image dict 구성
        # SDK가 types.Image 자동 변환을 지원하지 않을 경우를 대비해 딕셔너리 구조 사용 시도
        # 하지만 google-genai 최신 버전은 types 객체를 선호하므로 types.Image 사용
        image_input = types.Image(
            image_bytes=image_bytes,
            mime_type="image/png"
        )

        print("Sending request...")
        # Veo 3.1 호출
        response = client.models.generate_videos(
            model=MODEL_ID,
            prompt=PROMPT_TEXT,
            image=image_input,
            # config 설정이 필요할 수 있음
            config=types.GenerateVideosConfig(
                aspect_ratio="16:9"
            )
        )
        
        print("Response type:", type(response))
        print("Response dir:", dir(response))

        # 만약 response가 바로 결과 객체라면 (동기 방식)
        if hasattr(response, 'generated_videos') and response.generated_videos:
             result = response
             print("Response has generated_videos directly.")
        # LRO 폴링 로직 구현 (SDK가 자동으로 처리해주지 않는 경우 수동 폴링)
        elif hasattr(response, 'name') and response.name:
            print(f"Operation Name: {response.name}")
            operation_name = response.name
            
            # 수동 폴링 시작
            while True:
                try:
                    # 'str' object has no attribute 'name' 에러가 발생하는 것으로 보아
                    # client.operations.get() 내부에서 operation 객체를 기대하는 것으로 추정됨
                    # 하지만 operation_name은 문자열임.
                    
                    # SDK 내부 구현을 추측해볼 때, operation_name 문자열을 바로 get에 넘기면 안 되고
                    # operation 객체 자체를 넘기거나, 아니면 올바른 파라미터 이름을 찾아야 함.
                    
                    # 공식 SDK 최신 버전에서는 client.operations.get(name=...) 이 맞아야 하는데
                    # 에러 메시지: 'str' object has no attribute 'name' 은 SDK 내부 validator가
                    # 인자로 들어온 문자열(operation_name)에서 .name 속성을 찾으려다 실패하는 것 같음.
                    # 즉, operation_name(문자열) 대신 response 객체(Operation 객체)를 넘겨야 할 수도 있음.
                    
                    print(f"Polling with operation object (response)...")
                    op_status = client.operations.get(operation=response)
                    
                    print(f"Status: done={op_status.done}, error={op_status.error}")
                    
                    if op_status.done:
                        if op_status.error:
                             print(f"Operation failed with error: {op_status.error}")
                             sys.exit(1)
                        # 완료되면 result 필드나 response 필드를 확인
                        result = op_status.result
                        # 만약 result가 없고 response 필드에 데이터가 있다면
                        if not result and op_status.response:
                             result = op_status.response
                        break
                    
                    time.sleep(5)
                except Exception as poll_err:
                    print(f"Polling error with object: {poll_err}")
                    
                    # 실패 시 문자열로 다시 시도하되, name 키워드 사용
                    try:
                        print(f"Polling with name string: {operation_name}")
                        op_status = client.operations.get(name=operation_name)
                        print(f"Status: done={op_status.done}")
                        if op_status.done:
                             result = op_status.result
                             break
                        time.sleep(5)
                    except Exception as e2:
                        print(f"Polling error with string: {e2}")
                        sys.exit(1)


        else:
             print("Unknown response structure.")
             result = response

        print("\nGeneration complete!")
        
        # 결과 처리
        saved = False
        
        # result 구조 디버깅용 출력
        # print(result)

        if hasattr(result, 'generated_videos') and result.generated_videos:
            for video in result.generated_videos:
                # URL 방식
                # SDK 구조에 따라 video.video가 없을 수도 있고 바로 video.uri일 수도 있음
                # 출력된 로그를 보면 video=Video(uri='...') 형태임
                
                target_uri = None
                if hasattr(video, 'video') and hasattr(video.video, 'uri') and video.video.uri:
                     target_uri = video.video.uri
                elif hasattr(video, 'uri') and video.uri:
                     target_uri = video.uri
                
                if target_uri:
                    print(f"Downloading video from: {target_uri}")
                    # API Key가 필요한지 확인 (일반적으로 public URL이거나 인증 헤더 필요)
                    # Veo 결과 URL은 일반적으로 인증 없이 다운로드 가능하거나, SDK client를 통해 받아야 함.
                    # requests로 시도하되, 실패하면 헤더 추가 고려
                    
                    # 403 Forbidden 에러 발생 -> API Key 인증 헤더 추가 시도
                    headers = {}
                    if api_key:
                        headers["x-goog-api-key"] = api_key
                    
                    resp = requests.get(target_uri, headers=headers)
                    
                    if resp.status_code == 200:
                        with open(OUTPUT_VIDEO_PATH, "wb") as f:
                            f.write(resp.content)
                        saved = True
                        break
                    else:
                        print(f"Download failed with status {resp.status_code}")
                        # 실패 시 다른 헤더 조합 시도 (Authorization: Bearer 방식 등은 Oauth 토큰 필요하므로 API Key 방식 우선)
                        # 만약 API Key를 query param으로 넘겨야 할 수도 있음
                        if "?" in target_uri:
                            target_uri_with_key = f"{target_uri}&key={api_key}"
                        else:
                            target_uri_with_key = f"{target_uri}?key={api_key}"
                        
                        print(f"Retrying with key in query param...")
                        resp2 = requests.get(target_uri_with_key)
                        if resp2.status_code == 200:
                             with open(OUTPUT_VIDEO_PATH, "wb") as f:
                                f.write(resp2.content)
                             saved = True
                             break
                        else:
                            print(f"Retry failed with status {resp2.status_code}")

                
                # Blob/Bytes 방식
                elif hasattr(video, 'video') and hasattr(video.video, 'blob') and video.video.blob:
                    with open(OUTPUT_VIDEO_PATH, "wb") as f:
                        f.write(video.video.blob)
                    saved = True
                    break
        
        if saved:
            print(f"Video saved to: {OUTPUT_VIDEO_PATH}")
        else:
            print("Failed to save video. No valid video data found in result.")
            print(f"Result: {result}")

    except Exception as e:
        print(f"An error occurred:")
        print(e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()