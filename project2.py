import threading
import random
import time
from collections import deque

NUM_TELLERS = 3
NUM_CUSTOMERS = 3   # start small

print_lock = threading.Lock()

def log(kind, id_, other, msg):
    with print_lock:
        print(f"{kind} {id_} [{other}]: {msg}", flush=True)

# the line
teller_available = threading.Semaphore(0)
queue_lock = threading.Lock()
free_tellers = deque()

# per-teller handshake
customer_arrived = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
teller_cust = [None] * NUM_TELLERS


def teller(t):
    while True:
        log("Teller", t, "", "ready to serve")
        with queue_lock:
            free_tellers.append(t)
        teller_available.release()

        log("Teller", t, "", "waiting for a customer")
        customer_arrived[t].acquire()
        c = teller_cust[t]
        log("Teller", t, f"Customer {c}", "serving a customer")


def customer(c):
    log("Customer", c, "", "getting in line.")
    teller_available.acquire()
    log("Customer", c, "", "selecting a teller.")
    with queue_lock:
        t = free_tellers.popleft()
    log("Customer", c, f"Teller {t}", "selects teller")

    teller_cust[t] = c
    log("Customer", c, f"Teller {t}", "introduces itself")
    customer_arrived[t].release()


def main():
    tellers = [threading.Thread(target=teller, args=(i,)) for i in range(NUM_TELLERS)]
    for th in tellers:
        th.start()

    customers = [threading.Thread(target=customer, args=(i,)) for i in range(NUM_CUSTOMERS)]
    for th in customers:
        th.start()
    for th in customers:
        th.join()


if __name__ == "__main__":
    main()