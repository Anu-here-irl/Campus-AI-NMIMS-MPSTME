# Database Management Systems — Semester V Academic Notes
Author: Dept of Computer Engineering & IT
Course Code: CS-503

## Chapter 1: Relational Model & Normalization
Normalization is the process of structuring relational schema to reduce data redundancy and eliminate update, insertion, and deletion anomalies.

### Normal Forms
1. **First Normal Form (1NF):** All attributes contain only atomic (indivisible) values. No repeating groups or nested multi-valued attributes allowed.
2. **Second Normal Form (2NF):** Schema must be in 1NF and every non-prime attribute must be fully functionally dependent on the entire primary key (no partial functional dependency).
3. **Third Normal Form (3NF):** Schema must be in 2NF and have no transitive functional dependencies (no non-prime attribute depends on another non-prime attribute). Condition: For every X -> A, either X is a superkey or A is a prime attribute.
4. **Boyce-Codd Normal Form (BCNF):** Stricter version of 3NF. For every non-trivial functional dependency X -> A, X must be a superkey.

## Chapter 2: Transaction Management & ACID Properties
A transaction is a logical unit of database processing that includes one or more database access operations.
### ACID Properties
- **Atomicity:** All-or-nothing principle. Either all operations of the transaction complete successfully, or the entire transaction is rolled back leaving the database unchanged. Managed by the Transaction Recovery component (Write-Ahead Logging / Undo Logs).
- **Consistency:** Execution of a transaction in isolation preserves database invariants and constraints (e.g., total account balance remain valid).
- **Isolation:** Concurrent transactions execute without mutual interference. Intermediate transaction states are invisible to other concurrent transactions. Managed by Concurrency Control components.
- **Durability:** Once a transaction commits, its updates persist permanently in secondary storage, even across system crashes or power failures. Managed by Redo Logging.

## Chapter 3: Concurrency Control & Indexing
### Two-Phase Locking (2PL)
Ensures conflict serializability by enforcing two distinct operational phases:
1. **Growing Phase:** Transaction may acquire new locks (shared or exclusive) but cannot release any lock.
2. **Shrinking Phase:** Transaction may release locks but cannot acquire new locks.
- **Strict 2PL:** Prevents cascading rollbacks by holding all exclusive (write) locks until the transaction commits or aborts.

### Indexing Structures
- **B-Tree & B+ Tree:** Balanced tree data structures optimized for systems reading and writing large blocks of memory. In a B+ Tree, all data records are stored strictly in leaf nodes linked sequentially, facilitating fast range queries and binary search lookups with O(log N) complexity.
- **Hash Index:** Provides O(1) average lookup time for point queries using hash functions, but does not support range scans.
