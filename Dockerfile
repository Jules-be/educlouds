FROM python:3.8
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir numpy pandas
CMD ["python", "your_script.py"]    