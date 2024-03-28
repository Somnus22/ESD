FROM python:3-slim
WORKDIR /usr/src/app
COPY http.reqs.txt amqp.reqs.txt ./
RUN python -m pip install --no-cache-dir -r http.reqs.txt -r amqp.reqs.txt
COPY ./micro_car_inventory.py ./amqp_connection.py ./
CMD [ "python", "./micro_car_inventory.py" ]