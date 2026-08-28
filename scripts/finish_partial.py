import json, os, sys, time
from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

ADDRESS = sys.argv[1]
def main():
    p = create_account(os.environ["SERVICE_LEDGER_KEY_A"])
    s = create_account(os.environ["SERVICE_LEDGER_KEY_B"])
    c = create_client(chain=studionet, account=p, endpoint="https://studio.genlayer.com/api")
    def send(a, method, args, value=0):
        tx = c.write_contract(address=ADDRESS, function_name=method, account=a, args=args, value=value)
        for _ in range(160):
            info = c.get_transaction(str(tx)); status = info.get("status_name") or info.get("status")
            if status in ("ACCEPTED", "FINALIZED", "FAILED", "REJECTED", "CANCELLED"):
                print(json.dumps({"method": method, "tx": str(tx), "status": status, "result": info.get("result_name") or info.get("result")}, sort_keys=True), flush=True)
                return
            time.sleep(3)
    send(p, "classify_observation", [2])
    send(p, "resolve_observation", [2, 1, 20])
    send(s, "close_evidence_window", [3])
    send(s, "request_cancellation", [3])
    send(p, "settle", [3])
if __name__ == "__main__": main()
