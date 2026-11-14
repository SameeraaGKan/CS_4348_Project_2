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
safe = threading.Semaphore(2)
manager = threading.Semaphore(1)
queue_lock = threading.Lock()
free_tellers = deque()

# per-teller handshake
customer_arrived = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
teller_cust = [None] * NUM_TELLERS
ask_txn       = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
txn_given     = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
txn_done      = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
customer_left = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
teller_txn = [None] * NUM_TELLERS


def teller(t):
    while True:
        log("Teller", t, "", "ready to serve")
        with queue_lock:
            free_tellers.append(t)
        teller_available.release()

        log("Teller", t, "", "waiting for a customer")
        customer_arrived[t].acquire()
        c = teller_cust[t]
        cust = f"Customer {c}"
        log("Teller", t, cust, "serving a customer")
        log("Teller", t, cust, "asks for transaction")
        ask_txn[t].release()
        txn_given[t].acquire()
        txn = teller_txn[t]
        log("Teller", t, cust, f"handling {txn} transaction")

        if txn == "withdrawal":
            log("Teller", t, cust, "going to the manager")
            manager.acquire()
            log("Teller", t, cust, "getting manager's permission")
            time.sleep(random.uniform(0.005, 0.030))
            log("Teller", t, cust, "got manager's permission")
            manager.release()

        log("Teller", t, cust, "going to safe") 
        safe.acquire()
        log("Teller", t, cust, "enter safe")
        time.sleep(random.uniform(0.010, 0.050))
        log("Teller", t, cust, "leaving safe")
        safe.release()

        log("Teller", t, cust, f"finishes {txn} transaction.")
        log("Teller", t, cust, "wait for customer to leave.")
        txn_done[t].release()
        customer_left[t].acquire()


def customer(c):
    txn = random.choice(["deposit", "withdrawal"])
    log("Customer", c, "", f"wants to perform a {txn} transaction")

    log("Customer", c, "", "getting in line.")
    teller_available.acquire()
    log("Customer", c, "", "selecting a teller.")
    with queue_lock:
        t = free_tellers.popleft()
    tel = f"Teller {t}"
    log("Customer", c, tel, "selects teller")

    teller_cust[t] = c
    log("Customer", c, tel, "introduces itself")
    customer_arrived[t].release()

    ask_txn[t].acquire()
    teller_txn[t] = txn
    log("Customer", c, tel, f"asks for {txn} transaction")
    txn_given[t].release()

    txn_done[t].acquire()
    log("Customer", c, tel, "leaves teller")
    customer_left[t].release()


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