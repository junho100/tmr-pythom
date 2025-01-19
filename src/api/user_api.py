import requests
from urllib.parse import quote

API_BASE_URL = "http://localhost:8080"  # 실제 API 서버 URL로 변경해주세요

def verify_user(user_id):
    try:
        # URL 인코딩 및 API 엔드포인트 구성
        encoded_id = quote(user_id)
        response = requests.get(
            f"{API_BASE_URL}/api/subjects/check",
            params={'id': encoded_id},
            headers={'Content-Type': 'application/json'}
        )

        if not response.ok:
            return False, f"HTTP 오류! 상태: {response.status_code}"

        data = response.json()

        if data.get('is_exists'):
            return True, "로그인 성공"
        else:
            return False, "존재하지 않는 사용자입니다"

    except requests.exceptions.RequestException as e:
        return False, f"로그인 실패: {str(e)}"