FROM python:3.12-slim
WORKDIR /app
COPY server.py ./
COPY public ./public
RUN useradd -u 10001 -m studio && mkdir /data && chown studio:studio /data
USER studio
ENV DATA_DIR=/data PORT=8080
EXPOSE 8080
CMD ["python", "server.py"]
