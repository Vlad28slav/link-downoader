FROM python:3.11

COPY . /project_linker

WORKDIR /project_linker

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]