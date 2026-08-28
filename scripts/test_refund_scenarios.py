import json, os, sys, time
from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

ADDRESS = sys.argv[1]
PARTIAL_URL = "https://gateway.pinata.cloud/ipfs/bafkreibll5syidsdpjjnjvbq7ip7jdc4xydelbnuswdwny7f6men4j72be"
FULL_URL = "https://gateway.pinata.cloud/ipfs/bafkreicemhvo2lohpi7yrlletmiap22qtuy2b6aqsjjo7niz44lilgp7qu"
WEI = 10**16
provider = subscriber = client = None

def wait(tx, label):
    for _ in range(160):
        info = client.get_transaction(str(tx))
        status = info.get("status_name") or info.get("status")
        result = info.get("result_name") or info.get("result")
        if status in ("ACCEPTED", "FINALIZED", "FAILED", "REJECTED", "CANCELLED"):
            print(json.dumps({"label": label, "tx": str(tx), "status": status, "result": result}, sort_keys=True), flush=True)
            if status in ("FAILED", "REJECTED", "CANCELLED"):
                raise RuntimeError(label)
            return
        time.sleep(3)
    raise TimeoutError(label)

def send(account, method, args, value=0):
    return client.write_contract(address=ADDRESS, function_name=method, account=account, args=args, value=value)

def scenario(name, url, plan_id, subscription_id, observation_id):
    wait(send(provider, "register_plan", [name, WEI, 10, 60, 1000, 100000]), name + ":plan")
    wait(send(provider, "bind_plan_service", [plan_id, name]), name + ":bind")
    wait(send(provider, "approve_source", [plan_id, url]), name + ":source")
    wait(send(subscriber, "open_subscription", [plan_id, 100, 200], WEI), name + ":open")
    wait(send(subscriber, "submit_observation", [subscription_id, url, name, 150]), name + ":observation")
    wait(send(provider, "classify_observation", [observation_id]), name + ":classify")
    wait(send(subscriber, "close_evidence_window", [subscription_id]), name + ":close")
    wait(send(subscriber, "request_cancellation", [subscription_id]), name + ":cancel")
    wait(send(provider, "settle", [subscription_id]), name + ":settle")

if __name__ == "__main__":
    provider = create_account(os.environ["SERVICE_LEDGER_KEY_A"])
    subscriber = create_account(os.environ["SERVICE_LEDGER_KEY_B"])
    client = create_client(chain=studionet, account=provider, endpoint="https://studio.genlayer.com/api")
    scenario("partial-fixture-20260827", PARTIAL_URL, 1, 1, 1)
    scenario("full-fixture-20260827", FULL_URL, 2, 2, 2)
