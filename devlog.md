# 11-12-2026 4:14pm
Initialized the repository and devlog with initial plan.  Got the git repository initialised and started planning.
Mostly just trying to understand what the project is asking for.
Read through the spec a couple times. The big picture is 3 tellers, a bunch of customers, and a few shared things (door, manager, safe) that only let so many people use them at once. Basically it's all semaphores, so I need to figure out which semaphore does which job before I write anything.

# 11-13-2026 3:13pm
Start: plan to get the basic customer → teller meeting working before anything else, with 3 customers.
Main idea: teller_available is a counting semaphore starting at 0. Each free teller releases it, and customers block on it, which is how waiting in line works. The free_tellers queue tells the customer which teller it got, and the lock keeps two customers from grabbing the same one.
I started the semaphore at 0 on purpose, since at the start no teller is free yet. The count only goes up when a teller says it's ready, so a customer can't get through until there's actually someone to talk to.
What you’ll see: customers pair with tellers, then the program hangs because the tellers loop forever waiting for more customers.
End: intro works, the hang is a known problem, and the next step is the transaction. Customers and tellers match up correctly, so I'm not worried about the hang yet. I'll deal with it once the rest works.

# 11-13-2026 4:30pm
Start: plan to pass the transaction type between threads and add the shared resources.
Main idea: each teller gets its own set of semaphores, so signals for teller 0 can’t wake teller 1. Data moves through teller_cust and teller_txn, and the variable must be set before the release, or the other thread reads stale data.
If I used one shared semaphore for everyone, the wrong teller could wake up on someone else's customer. So every teller gets its own list entry (customer_arrived, ask_txn, txn_given, txn_done, customer_left) and the customer just uses the index of the teller it picked.
The order matters a lot here. The customer writes teller_txn[t] first and only then releases txn_given[t]. If it was the other way around the teller could wake up and read the old value.
Manager is Semaphore(1) and the safe is Semaphore(2). Each gets three log lines: going, using, done.
What you’ll see: the full transaction flow works for 3 customers, but it still hangs at the end.

# 11-13-2026 5:30pm
Plan: add the two shared resources.
Main idea: manager is Semaphore(1) and only withdrawals use it. Safe is Semaphore(2). Each has a sleep and three log lines: going, using, done.
Deposits skip the manager and go straight to the safe. The sleep inside each one is what makes the limit visible, since without it the teller would be in and out too fast to ever see two of them overlap.
What you’ll see: withdrawals take longer, and tellers queue up for the safe when 2 are already inside.
Reflect: how you checked that the limits held. I read through the log and looked for a third teller printing "enter safe" before any "leaving safe" from the first two, and for two tellers both inside "getting manager's permission" at once. Neither showed up, which is what the semaphores should guarantee, but it's nice to see it in the output too.

# 11-13-2026 6:30pm
Plan: make customers arrive at random times and go through the door.
Main idea: the door is Semaphore(2), used on the way in and on the way out. The random 0–100 ms delay spreads arrivals out.
Before this every customer started at the exact same moment, so the output looked really uniform. The random sleep happens before "going to bank" so the customers show up one at a time instead of all at once.
What you’ll see: output gets more interleaved and arrivals look less uniform.
Reflect: your choice to hold the door only while entering and leaving, not for the whole visit. If a customer held the door the whole time they were inside, only 2 people could be in the bank at once and the 3 tellers would never all be busy. The door is only a bottleneck for walking through it, so I acquire it, log, and release right away.

# 11-13-2026 7:30pm
Plan: make the bank open properly and fix the hang from Session 1.
Main idea: main waits for 3 teller_ready signals before starting customers. After the customers are joined, it sets done and wakes each teller so it can exit.
Opening: before this, customers could start before the tellers were even up. Now each teller releases teller_ready the first time it's ready, and main acquires it 3 times before it creates any customers.
Closing: main joins all the customers first, then sets done = True, then releases customer_arrived for each teller.
What you’ll see: “leaving for the day” three times, then “The bank closes for the day.”
Reflect: why the tellers were stuck, and why releasing customer_arrived fixes it. After the last customer left, every teller looped back around and blocked on customer_arrived[t].acquire(), waiting for a customer that was never coming. Since main was joining the tellers, it waited forever too. Releasing customer_arrived wakes them up, and because done is already True they see that and return instead of trying to serve someone. done has to be set before the release, same idea as before.

# 11-13-2026 10:00pm
Plan: run the full simulation and verify it.
Main idea: set NUM_CUSTOMERS = 50, run it multiple times, and use the grep checks (expect 50 and 3).
The 50 is how many customers "leaves the bank" should show up, and the 3 is how many tellers say "leaving for the day". If either number is off then a thread got stuck or skipped something.
What you’ll see: about 1100+ lines of output, and the counts match.
Reflect: I ran it 5 times. Every run gave exactly 50 "leaves the bank" and 3 "leaving for the day", and the program exited cleanly each time with no hangs. The output was 1141, 1135, 1129, 1144 and 1129 lines, so about 1136 on average. The count moves a little because withdrawals print a few extra manager lines and customers pick deposit or withdrawal at random. I expected around 350 lines at first, but each customer prints roughly 20 lines on their own, so it's more like 1100. Nothing weird showed up. One thing I'd change is the log format, the blank [] shows up on lines without another party and it looks a little off. Otherwise nothing needed to change once the closing fix was in.
