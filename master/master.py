import csv
import datetime
import requests
import time
from flask import Flask


CONTAINERS = 3
START = 1
END = 10**12
ENDPOINTS = ['http://localhost:5001', 'http://localhost:5002', 'http://localhost:5003']
app = Flask(__name__)

# Divide work between containers by generating ranges of values
def get_ranges(start, end, divisor):
    step = (end - start) // divisor
    ranges = [(start + i*step, start + (i+1)*step - 1) for i in range(divisor)]
    ranges[-1] = (ranges[-1][0], end)
    return ranges

# Log resource utilization to CSV file
def log_resource_utilization(cpu_percent, mem_percent):
    with open('resource_utilization.csv', mode='a') as file:
        writer = csv.writer(file)
        now = datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S')
        writer.writerow([now, cpu_percent, mem_percent])

primes = []
@app.route('/')
def main():
    global primes
    while True:
        # Divide work between containers
        ranges = get_ranges(START, END, CONTAINERS)
        results = []
        for i in range(CONTAINERS):
            start, end = ranges[i]
            print(f'{ENDPOINTS[i]}/generate?from={start}&to={end}')
            url = f'{ENDPOINTS[i]}/generate?from={start}&to={end}'
            requests.get(url)
            time.sleep(60)
            # Log resource utilization to CSV file
            monitor_url = f'{ENDPOINTS[i]}/monitor?k=1'
            monitor_result = requests.get(monitor_url).json()
            cpu_percent = monitor_result["CPU Usage"]
            mem_percent = monitor_result["Memory Usage"]
            log_resource_utilization(cpu_percent, mem_percent)

            # Get primes from container
            primes_url = f'{ENDPOINTS[i]}/get'
            result = requests.get(primes_url).json()
            results.append(result)

        # Merge results and remove duplicates
        primes = []
        for result in results:
            primes += result['primes']
        primes = sorted(list(set(primes)))
        with open('result.csv', mode='a') as file:
            writer = csv.writer(file)
            writer.writerow([primes])
        # Wait for 2 minutes before querying containers again
        time.sleep(120)
    return 'OK'

if __name__ == '__main__':
    app.run()
