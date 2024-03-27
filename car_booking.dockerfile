FROM python:3-slim
WORKDIR /usr/src/app
COPY http.reqs.txt ./
RUN python -m pip install --no-cache-dir -r http.reqs.txt
COPY ./complex_car_booking.py ./invokes.py ./
CMD [ "python", "./complex_car_booking.py" ]