# 11-12-2026 4:14pm
Initialized the repository and devlog with initial plan.  Got the git repository initialised and started planning.
Mostly just trying to understand what the project is asking for.


# 11-13-2026 3:13pm
Start: plan to get the basic customer → teller meeting working before anything else, with 3 customers.
Main idea: teller_available is a counting semaphore starting at 0. Each free teller releases it, and customers block on it, which is how waiting in line works. The free_tellers queue tells the customer which teller it got, and the lock keeps two customers from grabbing the same one.
What you’ll see: customers pair with tellers, then the program hangs because the tellers loop forever waiting for more customers.
End: intro works, the hang is a known problem, and the next step is the transaction.



