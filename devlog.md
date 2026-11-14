# 11-12-2026 4:14pm
Initialized the repository and devlog with initial plan.  Got the git repository initialised and started planning.
Mostly just trying to understand what the project is asking for.


# 11-13-2026 3:13pm
Start: plan to get the basic customer → teller meeting working before anything else, with 3 customers.
Main idea: teller_available is a counting semaphore starting at 0. Each free teller releases it, and customers block on it, which is how waiting in line works. The free_tellers queue tells the customer which teller it got, and the lock keeps two customers from grabbing the same one.
What you’ll see: customers pair with tellers, then the program hangs because the tellers loop forever waiting for more customers.
End: intro works, the hang is a known problem, and the next step is the transaction.

# 11-13-2026 4:30pm
Start: plan to pass the transaction type between threads and add the shared resources.
Main idea: each teller gets its own set of semaphores, so signals for teller 0 can’t wake teller 1. Data moves through teller_cust and teller_txn, and the variable must be set before the release, or the other thread reads stale data.
Manager is Semaphore(1) and the safe is Semaphore(2). Each gets three log lines: going, using, done.
What you’ll see: the full transaction flow works for 3 customers, but it still hangs at the end.


# 11-13-2026 5:30pm


