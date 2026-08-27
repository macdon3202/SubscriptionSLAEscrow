# Contract specification

## Roles

- Provider: authenticated plan registrant and payout recipient.
- Subscriber: authenticated payable subscription opener and refund recipient.
- Observer: any address that submits a bounded public evidence URL and immutable digest.
- Validator jury: classifies one observation's outage fact, duration and confidence.

## Settlement matrix

| Confirmed downtime | Outcome | Provider | Subscriber |
|---|---|---:|---:|
| below partial threshold | `SLA_MET` | 100% | 0% |
| partial to below full threshold | `PARTIAL_REFUND` | 70% | 30% |
| at or above full threshold | `FULL_REFUND` | 0% | 100% |

## Consensus binding

| Field | Consequence | Binding |
|---|---|---|
| outage | determines whether minutes accrue | comparative semantic agreement |
| duration_minutes | determines refund band | comparative semantic agreement |
| confidence | low confidence blocks automatic accounting | validated 0..100 |
| reason | audit explanation | bounded and stored |
| evidence URL/digest | source identity | locked before classification |

## Known limitations

- The current version settles on explicit subscriber cancellation rather than wall-clock period expiry.
- Public HTTPS evidence is paired with a submitted digest, but the runtime does not compute a cryptographic digest of fetched content in this revision.
- Low-confidence observations require a later operational review path; they do not add downtime.

