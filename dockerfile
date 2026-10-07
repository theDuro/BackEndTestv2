FROM python:3.13.5

WORKDIR /BackEndTestv2

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "-m", "controller.application"]
