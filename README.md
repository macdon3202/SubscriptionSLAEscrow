# Subscription SLA Escrow

Subscription SLA Escrow protects prepaid GEN for Web3 RPC, API, storage and DAO
membership services. Providers publish measurable SLA bands. Subscribers fund one
service period, attach public status evidence, and request cancellation. GenLayer
validators normalize each incident into an outage fact and duration; deterministic
contract logic then releases payment, applies a partial refund, or returns the full
deposit.

## Why GenLayer

Status pages and public incident logs use inconsistent language and time formats.
A deterministic contract cannot fetch those sources or interpret whether a service
was unavailable. GenLayer performs the web retrieval and semantic classification
inside the Intelligent Contract. The monetary outcome is derived from the
consensus-confirmed downtime total and the SLA thresholds registered on-chain.

## Architecture difference

This project is a period-based service accounting primitive, not a one-shot document
review. A subscription accumulates multiple independently classified observations.
Persistent state records per-observation duration and a running downtime total.
Consensus binds the outage fact and duration for each event; settlement itself is a
deterministic SLA calculation with three value-distribution outcomes. The frontend
is organized around provider plans, active subscription monitoring, incident history
and cancellation settlement rather than an evidence-review queue.

## State model

```text
Plan registration
  -> ACTIVE subscription funded with exact GEN
  -> zero or more PENDING observations
  -> CONFIRMED / NEEDS_REVIEW observations
  -> CANCELLATION_REQUESTED
  -> SLA_MET / PARTIAL_REFUND / FULL_REFUND
```

Partial breach returns 30% and pays 70% to the provider. A full-breach threshold
returns 100%. These percentages are explicit contract policy, while the provider
controls the duration thresholds when registering a plan.

## Local verification

```bash
python -c "import ast; ast.parse(open('contracts/SubscriptionSLAEscrow.py').read())"
pytest -q
cd frontend
npm install
npm run build
```

The current source revision adds settlement-party authorization and a confirmed
observation counter. The current Studionet deployment is
`0x00d30a829e5a51c88155a94020F2B7E5918363b3`; its deployment and lifecycle
transactions are recorded in `deployments/studionet.json`. The happy path and
negative transaction submissions are documented. A partial-refund settlement has
now been independently confirmed on-chain with a 70/30 provider/subscriber
transfer split; full-refund evidence is not claimed.
