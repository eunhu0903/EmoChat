import smtplib
from email.mime.text import MIMEText
from core.config import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

def send_verification_email(to_email: str, code: str):
    subject = "[EmoChat] 이메일 인증 코드"
    body = f"""
안녕하세요!

EmoChat 이메일 인증 코드는 아래와 같습니다:

▶ 인증 코드: {code}

5분 이내로 입력해주세요.

감사합니다.
""".strip()

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_HOST_USER
    msg["To"] = to_email

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_HOST_USER, to_email, msg.as_string())
    except Exception as e:
        raise RecursionError(f"이메일 전송을 실패하였습니다. {e}")
    
