import threading
import random
import time
from collections import deque

NUM_TELLERS = 3
NUM_CUSTOMERS = 3   # bump to 50 in session 6

# ---------- output ----------
print_lock = threading.Lock()

def log(kind, id_, other, msg):
    with print_lock:
        print(f"{kind} {id_} [{other}]: {msg}", flush=True)

# ---------- shared resources ----------
door = threading.Semaphore(2)        # 2 customers through the door at a time
safe = threading.Semaphore(2)        # 2 tellers in the safe at a time
manager = threading.Semaphore(1)     # 1 teller with the manager at a time

# ---------- bank opening ----------
teller_ready = threading.Semaphore(0)   # main waits for 3 of these

# ---------- the line ----------
teller_available = threading.Semaphore(0)  # count of free tellers; customers block here = waiting in line
queue_lock = threading.Lock()
free_tellers = deque()                     # which tellers are free

# ---------- per-teller handshake ----------
customer_arrived = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
ask_txn          = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
txn_given        = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
txn_done         = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]
customer_left    = [threading.Semaphore(0) for _ in range(NUM_TELLERS)]

# shared variables for passing data
teller_cust = [None] * NUM_TELLERS
teller_txn = [None] * NUM_TELLERS

done = False


def teller(t):
    first = True
    while True:
        log("Teller", t, "", "ready to serve")
        with queue_lock:
            free_tellers.append(t)
        teller_available.release()
        if first:
            teller_ready.release()
            first = False

        log("Teller", t, "", "waiting for a customer")
        customer_arrived[t].acquire()
        if done:
            log("Teller", t, "", "leaving for the day")
            return

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
    time.sleep(random.uniform(0, 0.100))

    log("Customer", c, "", "going to bank.")
    door.acquire()
    log("Customer", c, "", "entering bank.")
    door.release()

    log("Customer", c, "", "getting in line.")
    teller_available.acquire()            # blocks if no teller is free
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

    log("Customer", c, "", "goes to door")
    door.acquire()
    log("Customer", c, "", "leaves the bank")
    door.release()


def main():
    global done
    tellers = [threading.Thread(target=teller, args=(i,)) for i in range(NUM_TELLERS)]
    for th in tellers:
        th.start()

    for _ in range(NUM_TELLERS):          # bank opens when all 3 are ready
        teller_ready.acquire()

    customers = [threading.Thread(target=customer, args=(i,)) for i in range(NUM_CUSTOMERS)]
    for th in customers:
        th.start()
    for th in customers:
        th.join()

    done = True
    for t in range(NUM_TELLERS):          # wake tellers so they can exit
        customer_arrived[t].release()
    for th in tellers:
        th.join()

    print("The bank closes for the day.")


if __name__ == "__main__":
    main()