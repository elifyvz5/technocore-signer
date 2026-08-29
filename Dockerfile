FROM python:3.12-slim

WORKDIR /srv

RUN pip install --no-cache-dir cryptography==50.0.0

COPY signer.py /srv/signer.py

CMD ["python", "/srv/signer.py"]
