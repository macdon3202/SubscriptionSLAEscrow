import json, os, sys, time
from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

ADDRESS = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SUBSCRIPTION_ESCROW_ADDRESS", "")
WEI = 10**16
URL = "https://example.com/"
DIGEST = "sha256:example-status-observation-20260827"

def wait(client, tx, label):
    last = None
    for _ in range(120):
        info = client.get_transaction(str(tx))
        status = info.get("status_name") or info.get("status")
        result = info.get("result_name") or info.get("result")
        if (status, result) != last:
            print(json.dumps({"event": label, "tx": str(tx), "status": status, "result": result}, sort_keys=True), flush=True)
            last = (status, result)
        if status in ("FAILED", "REJECTED", "CANCELLED"):
            raise RuntimeError(f"{label} failed: {status} {result}")
        if status in ("ACCEPTED", "FINALIZED"):
            return info
        time.sleep(3)
    raise TimeoutError(label)

def main():
    if not ADDRESS:
        raise RuntimeError("Pass the deployed contract address")
    k1 = os.environ.get("SERVICE_LEDGER_KEY_A", "")
    k2 = os.environ.get("SERVICE_LEDGER_KEY_B", "")
    if not k1 or not k2:
        raise RuntimeError("Set SERVICE_LEDGER_KEY_A and SERVICE_LEDGER_KEY_B")
    provider, subscriber = create_account(k1), create_account(k2)
    client = create_client(chain=studionet, account=provider, endpoint="https://studio.genlayer.com/api")
    def send(account, method, args, value=0):
        tx = client.write_contract(address=ADDRESS, function_name=method, account=account, args=args, value=value)
        print(json.dumps({"event":"SUBMITTED", "method":method, "tx":str(tx)}, sort_keys=True), flush=True)
        return tx
    def read(method, args):
        return client.read_contract(address=ADDRESS, function_name=method, args=args, account=provider)
    plan = wait(client, send(provider, "register_plan", ["RPC Standard", WEI, 30, 120, 1000, 100000]), "PLAN")
    sub = wait(client, send(subscriber, "open_subscription", [0], WEI), "SUBSCRIPTION")
    obs = wait(client, send(subscriber, "submit_observation", [0, URL, DIGEST]), "OBSERVATION")
    classify = wait(client, send(provider, "classify_observation", [0]), "CLASSIFY")
    print(json.dumps({"event":"AFTER_CLASSIFY", "subscription":read("read_subscription", [0])}, default=str, sort_keys=True), flush=True)
    wait(client, send(subscriber, "request_cancellation", [0]), "CANCEL")
    wait(client, send(provider, "settle", [0]), "SETTLE")
    print(json.dumps({"event":"FINAL_READBACK", "subscription":read("read_subscription", [0])}, default=str, sort_keys=True), flush=True)

if __name__ == "__main__":
    main()
