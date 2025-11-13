
FROM python:3.10-slim


ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1


WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt


RUN addgroup --system app && adduser --system --ingroup app app


COPY . .


RUN chown -R app:app /app


USER app

EXPOSE 8001

CMD ["gunicorn", "--bind", "0.0.0.0:8001", "app.wsgi:application"]