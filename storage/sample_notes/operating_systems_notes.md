# Operating Systems — Semester V Academic Notes
Author: Dept of Computer Engineering & IT
Course Code: CS-502

## Chapter 1: Process Management & CPU Scheduling
A process is a program in execution containing program code, counter, registers, stack, and heap.
- **Process States:** New, Ready, Running, Waiting (Blocked), Terminated.
- **Process Control Block (PCB):** Data structure maintaining process state, PID, CPU registers, scheduling parameters, memory limits, and open file lists.

### CPU Scheduling Algorithms
1. **First-Come, First-Served (FCFS):** Non-preemptive algorithm executing jobs in arrival order. Can suffer from the Convoy Effect where short processes wait behind a long CPU burst job.
2. **Shortest Job First (SJF) & Shortest Remaining Time First (SRTF):** Selects process with minimal CPU burst duration. Provably optimal in minimizing average waiting time, but susceptible to starvation of longer processes.
3. **Round Robin (RR):** Preemptive algorithm designed for timesharing systems. Each process gets a fixed time quantum (slice). Balances responsiveness and context switching overhead.
4. **Priority Scheduling:** Processes are assigned priority integers. Lower numerical values often indicate higher priority. Solves starvation using Aging (gradually increasing waiting process priority).

## Chapter 2: Deadlocks & Synchronization
A deadlock occurs when a set of concurrent processes are blocked because each process holds a resource and waits for another resource held by another process.
### Four Necessary Conditions (Coffman Conditions)
1. **Mutual Exclusion:** At least one resource must be held in a non-shareable mode.
2. **Hold and Wait:** A process holds at least one resource while waiting to acquire additional resources held by other processes.
3. **No Preemption:** Resources cannot be forcibly taken from a process until it voluntarily releases them.
4. **Circular Wait:** A closed chain of processes exists such that each process holds a resource needed by the next process in the chain.

### Deadlock Handling Strategies
- **Deadlock Prevention:** Design protocols to invalidate at least one of the four Coffman conditions (e.g., ordering resource acquisition to eliminate circular wait).
- **Deadlock Avoidance (Banker's Algorithm):** Requires priori knowledge of maximum resource demands. Continuously evaluates if granting a resource keeps the system in a **Safe State** where all processes can complete.
- **Detection and Recovery:** Periodically builds a Resource Allocation Graph (RAG) to detect cycles, then aborts processes or preempts resources.

## Chapter 3: Memory Management & Virtual Memory
- **Paging:** Divides physical memory into fixed-sized blocks called **Frames** and logical memory into same-sized blocks called **Pages**. Eliminates external fragmentation.
- **Page Fault:** An interrupt generated when an executing process references a page not currently residing in physical RAM. Triggers the OS to fetch the page from disk swap space.
- **Page Replacement Algorithms:** FIFO (subject to Belady's Anomaly), Optimal (OPT - clairvoyant benchmark), and Least Recently Used (LRU - practical approximation using timestamping or stack).
