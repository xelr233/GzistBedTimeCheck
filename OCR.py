import os
import httpx
import base64
from retrying import retry


session = httpx.Client()
url = "http://ip:port/ocr"


def get_env():
    api = os.getenv('OCR_API')
    return f"http://{api}/ocr"


url = get_env()


@retry(stop_max_attempt_number=3, wait_fixed=2000)
def ocr(img_base64) -> str | None:
    try:
        response = session.post(url, data={"image": img_base64}, timeout=3)
        response.raise_for_status()  # 检查HTTP请求是否成功
        body = response.json()
        if body.get("code") != 200:
            raise ValueError("API 返回错误代码: {}".format(body.get("code")))
        return body.get("data")
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as e:
        print("OCR 请求失败: ", e)
        return None


if __name__ == "__main__":
    try:
        with open("test.png", "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode()
        result = ocr(img_base64)
        if result is not None:
            print(result)
        else:
            print("OCR 处理未成功")
    except FileNotFoundError:
        print("文件 'test.png' 未找到")
    except Exception as e:
        print("发生错误: ", e)
