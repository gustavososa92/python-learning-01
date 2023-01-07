FROM python:3

WORKDIR usr/src/app

COPY requirements.txt ./

RUN  pip install --upgrade pip

RUN pip install --no-cache-dir -U pip wheel setuptools

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-1.8.0-py3-none-any.whl

COPY . .

CMD ["python", "app.py"]