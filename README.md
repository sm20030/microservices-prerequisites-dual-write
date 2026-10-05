# Architectural Tradeoffs: Monolith ACID vs. Microservice Dual-Writes

A practical reference to show the operational and data-consistency trade-offs between monolithic database transactions and microservices distributed network boundaries.

---

## The Core Problem: The Dual-Write Trap

When going from a monolithic system to microservices, you exchange in-memory function calls and ACID(Atomicity, Consistency, Isolation, and Durability) database transactions for asynchronous network calls and independent service databases.

## To run demo.py

python3 -m pip install fastapi uvicorn sqlalchemy pydantic

python3 demo.py

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
                       |
                  (Network Hop / REST / SQS)
                       v
                  [ Audit Service ] --(DB Write)---> [ Audit DB ]
* Risk: Network timeout after Order DB write creates state corruption!

```text
* For Mermaid.js graphic rendering
graph TD
    subgraph Monolith
        M_Req[User Request] --> M_Tx[Single ACID Transaction]
        M_Tx --> M_DB[(Orders, Inventory & Audit Tables)]
    end

    subgraph Microservices
        MS_Req[User Request] --> MS_Ord[Order Service]
        MS_Ord -->|DB Write| MS_ODB[(Order DB)]
        MS_Ord -->|Network Hop / SQS| MS_Inv[Inventory Service]
        MS_Inv -->|DB Write| MS_IDB[(Inventory DB)]
        MS_Inv -->|Network Hop / SQS| MS_Audit[Audit Service]
        MS_Audit -->|DB Write| MS_ADB[(Audit DB)]
    end
