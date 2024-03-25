FROM python:3-slim
WORKDIR /usr/src/app
COPY http.reqs.txt ./
RUN python -m pip install --no-cache-dir -r http.reqs.txt
COPY ./complex_report_damage.py ./
CMD [ "python", "./complex_report_damage.py" ]