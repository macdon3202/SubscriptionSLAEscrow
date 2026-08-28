import json, os, sys, time
from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

ADDRESS = sys.argv[1]
PLAN_ID = int(os.environ.get("SERVICE_LEDGER_PLAN_ID", "0"))
SUBSCRIPTION_ID = int(os.environ.get("SERVICE_LEDGER_SUBSCRIPTION_ID", "0"))
provider = subscriber = client = None

def wait(tx, label):
    for _ in range(160):
        info = client.get_transaction(str(tx))
        status = info.get("status_name") or info.get("status")
        result = info.get("result_name") or info.get("result")
        if status in ("ACCEPTED", "FINALIZED", "FAILED", "REJECTED", "CANCELLED"):
            print(json.dumps({"label": label, "tx": str(tx), "status": status, "result": result}, sort_keys=True), flush=True)
            if status in ("FAILED", "REJECTED", "CANCELLED"): raise RuntimeError(label)
            return result
        time.sleep(3)
    raise TimeoutError(label)

def send(account, method, args, value=0):
    tx = client.write_contract(address=ADDRESS, function_name=method, account=account, args=args, value=value)
    print(json.dumps({"label":"SUBMITTED", "method":method, "tx":str(tx)}, sort_keys=True), flush=True)
    return tx

def main():
    global provider, subscriber, client
    provider = create_account(os.environ["SERVICE_LEDGER_KEY_A"])
    subscriber = create_account(os.environ["SERVICE_LEDGER_KEY_B"])
    client = create_client(chain=studionet, account=provider, endpoint="https://studio.genlayer.com/api")
    wait(send(provider, "register_plan", ["Review Test", 10**16, 30, 120, 1000, 100000]), "PLAN")
    wait(send(provider, "bind_plan_service", [PLAN_ID, "review-test-service"]), "BIND")
    wait(send(provider, "approve_source", [PLAN_ID, "https://example.com/404"]), "SOURCE")
    wait(send(subscriber, "open_subscription", [PLAN_ID, 100, 200], 10**16), "OPEN")
    wait(send(subscriber, "submit_observation", [SUBSCRIPTION_ID, "https://example.com/404", "sha256:review-resolution-20260828", 150]), "OBSERVE")
    result = wait(send(provider, "classify_observation", [SUBSCRIPTION_ID]), "CLASSIFY")
    if result == "NEEDS_REVIEW":
        wait(send(provider, "resolve_observation", [SUBSCRIPTION_ID, 0, 0]), "RESOLVE")
    wait(send(subscriber, "close_evidence_window", [SUBSCRIPTION_ID]), "CLOSE")
    wait(send(subscriber, "request_cancellation", [SUBSCRIPTION_ID]), "CANCEL")
    wait(send(provider, "settle", [SUBSCRIPTION_ID]), "SETTLE")

if __name__ == "__main__": main()
