import math
import threading
from queue import Queue
from flask import Flask, request
import psutil
import time

app = Flask(__name__)

primes = Queue()
log = []
lock = threading.Lock()


def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(math.sqrt(num)) + 1):
        if num % i == 0:
            return False
    return True


def generate_primes(from_num, to_num):
    print(f"Generating primes from {from_num} to {to_num}...")
    start_time = time.time()
    for num in range(from_num, to_num + 1):
        if is_prime(num):
            with lock:
                primes.put(num)
        
        elapsed_time = time.time() - start_time
        # print(elapsed_time)
        if elapsed_time >= 60: # log after every minute
            print('1 min has passed')
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            log.append({"time": elapsed_time, "cpu": cpu_percent, "memory": memory_percent})
            print(f"Logged at time: {elapsed_time:.2f}, logs count: {len(log)}")
            start_time = time.time()
        


def start_prime_generation(from_num, to_num):
    t = threading.Thread(target=generate_primes, args=(from_num, to_num))
    t.start()


@app.route('/generate', methods=['GET'])
def generate():
    from_num = int(request.args.get('from'))
    to_num = int(request.args.get('to'))
    start_prime_generation(from_num, to_num)
    return "Generating Prime Numbers..."


@app.route('/monitor')
def monitor():
    k = int(request.args.get('k'))
    logs_last_k_minutes = []
    with lock:
        for l in reversed(log):
            if k:
                logs_last_k_minutes.append(l)
                k -= 1 

    cpu_usage_sum = sum(l['cpu'] for l in logs_last_k_minutes)
    memory_usage_sum = sum(l['memory'] for l in logs_last_k_minutes)
    logs_count = len(logs_last_k_minutes)
    cpu_usage_avg = cpu_usage_sum / logs_count if logs_count > 0 else 0
    memory_usage_avg = memory_usage_sum / logs_count if logs_count > 0 else 0
    return {"CPU Usage": cpu_usage_avg, "Memory Usage": memory_usage_avg}



@app.route('/get')
def get():
    with lock:
        return {"primes": list(primes.queue)}


def main():
    app.run();


if __name__ == '__main__':
    main()
