# ---------------------------------------------------------------
# 학생 과제: 아래 각 줄이 무엇을 하는지 주석으로 설명을 달아보세요.
# ---------------------------------------------------------------

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m appuser
USER appuser

ENV APP_TITLE="정하은 DevOps 방명록" \
    THEME_COLOR="#8B5CF6"

EXPOSE 5000

CMD ["python", "app.py"]
