import math
import threading
from queue import Queue
from flask import Flask, request
import psutil

app = Flask(__name__)

primes = Queue()
lock = threading.Lock()


def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(math.sqrt(num)) + 1):
        if num % i == 0:
            return False
    return True


def generate_primes(from_num, to_num):
    for num in range(from_num, to_num + 1):
        if is_prime(num):
            with lock:
                primes.put(num)


def start_prime_generation(from_num, to_num):
    t = threading.Thread(target=generate_primes, args=(from_num, to_num))
    t.start()


@app.route('/generate', methods=['GET'])
def generate():
    data = request.json
    from_num = int(request.args.get('from'))
    to_num = int(request.args.get('to'))
    start_prime_generation(from_num, to_num)
    return "Generating Prime Numbers..."


@app.route('/monitor')
def monitor():
    k = int(request.args.get('k'))
    cpu_usage = psutil.cpu_percent(interval=k, percpu=False)
    memory_usage = psutil.virtual_memory().percent
    return {"CPU Usage": cpu_usage, "Memory Usage": memory_usage}


@app.route('/get')
def get():
    with lock:
        return {"primes": list(primes.queue)}


def main():
    app.run();


if __name__ == '__main__':
    main()
