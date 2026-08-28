import json, os, sys, time
from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

ADDRESS = sys.argv[1]
URL = "https://gateway.pinata.cloud/ipfs/bafkreibfhuc7pviaoo25ep7anudcugotxpl3xbmjkosq3ms4tcesuk7glm"
def main():
    p=create_account(os.environ["SERVICE_LEDGER_KEY_A"]); s=create_account(os.environ["SERVICE_LEDGER_KEY_B"])
    c=create_client(chain=studionet,account=p,endpoint="https://studio.genlayer.com/api")
    def call(a,m,args,value=0):
        tx=c.write_contract(address=ADDRESS,function_name=m,account=a,args=args,value=value)
        for _ in range(160):
            i=c.get_transaction(str(tx)); st=i.get("status_name") or i.get("status")
            if st in ("ACCEPTED","FINALIZED","FAILED","REJECTED","CANCELLED"):
                print(json.dumps({"method":m,"tx":str(tx),"status":st,"result":i.get("result_name") or i.get("result")},sort_keys=True),flush=True); return
            time.sleep(3)
    call(p,"register_plan",["real-partial-incident",10**16,10,60,1000,100000])
    call(p,"bind_plan_service",[5,"real-partial-incident"]); call(p,"approve_source",[5,URL])
    call(s,"open_subscription",[5,100,200],10**16); call(s,"submit_observation",[4,URL,"svc-2026-08-28-001",150])
    call(p,"classify_observation",[3]); call(s,"close_evidence_window",[4]); call(s,"request_cancellation",[4]); call(p,"settle",[4])
if __name__ == "__main__": main()
