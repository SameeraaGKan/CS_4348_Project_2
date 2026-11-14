# CS 4348 Project 2: Bank Simulation

A thread-based bank simulation in Python. 3 teller threads serve 50 customer threads, synchronized only with `threading.Semaphore` (plus a lock for the teller queue and for printing).

## Run

```
python project2.py
```

Needs Python 3, no extra packages. It prints one line per action in the form `THREAD_TYPE ID [THREAD_TYPE ID]: MSG` and ends with `The bank closes for the day.`

Quick check (expect 50 and 3):

```
python project2.py | grep -c "leaves the bank"
python project2.py | grep -c "leaving for the day"
```

## How it works

| Semaphore | Purpose |
|---|---|
| `door` (2) | at most 2 customers going through the door at once |
| `safe` (2) | at most 2 tellers in the safe |
| `manager` (1) | one teller at a time with the manager (withdrawals only) |
| `teller_ready` (0) | main waits for all 3 tellers before customers start |
| `teller_available` (0) | count of free tellers; customers block here = waiting in line |
| `customer_arrived`, `ask_txn`, `txn_given`, `txn_done`, `customer_left` | one per teller, step-by-step handshake between a teller and its customer |

Customers and tellers pass data (customer id, transaction type) through the shared lists `teller_cust` and `teller_txn`, always written before the matching `release()`.

At closing, main joins all customers, sets `done`, and releases each teller's `customer_arrived` so the tellers see `done` and exit.

## Files

- `project2.py`: the simulation
- `devlog.md`: development log
