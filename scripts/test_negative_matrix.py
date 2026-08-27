import json, os, sys, time
from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

ADDRESS = sys.argv[1]
KEY_A = os.environ["SERVICE_LEDGER_KEY_A"]
KEY_B = os.environ["SERVICE_LEDGER_KEY_B"]
provider = create_account(KEY_A)
subscriber = create_account(KEY_B)
client = create_client(chain=studionet, account=provider, endpoint="https://studio.genlayer.com/api")

def run(account, method, args, value=0):
    tx = client.write_contract(address=ADDRESS, function_name=method, account=account, args=args, value=value)
    for _ in range(120):
        info = client.get_transaction(str(tx))
        status = info.get("status_name") or info.get("status")
        result = info.get("result_name") or info.get("result")
        if status in ("ACCEPTED", "FINALIZED"):
            print(json.dumps({"case": method, "tx": str(tx), "status": status, "result": result}, sort_keys=True), flush=True)
            return
        if status in ("FAILED", "REJECTED", "CANCELLED"):
            print(json.dumps({"case": method, "tx": str(tx), "status": status, "result": result}, sort_keys=True), flush=True)
            return
        time.sleep(3)

run(provider, "settle", [0])
run(provider, "request_cancellation", [0])
run(subscriber, "open_subscription", [0], 1)
run(subscriber, "classify_observation", [0])
