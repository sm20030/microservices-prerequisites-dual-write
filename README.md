# Architectural Tradeoffs: Monolith ACID vs. Microservice Dual-Writes

A practical reference to show the operational and data-consistency trade-offs between monolithic database transactions and microservices distributed network boundaries.

---

## The Core Problem: The Dual-Write Trap

When going from a monolithic system to microservices, you exchange in-memory function calls and ACID(Atomicity, Consistency, Isolation, and Durability) database transactions for asynchronous network calls and independent service databases.

```text
[ MONOLITH ]
User Request ---> [ Single ACID Transaction ] ---> ( Orders Table + Inventory Table + Audit Table )
* Fast, atomic, zero network hops.

[ MICROSERVICES ]
User Request ---> [ Order Service ] --(DB Write)---> [ Order DB ]
                       |
                  (Network Hop / REST / SQS)
                       v
                  [ Inventory Service ] --(DB Write)---> [ Inventory DB ]
* Risk: Network timeout after Order DB write creates state corruption!
