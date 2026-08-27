import { createClient } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';

export const CONTRACT_ADDRESS = import.meta.env.VITE_CONTRACT_ADDRESS || '';
export function makeReadClient() {
  return createClient({ chain: studionet });
}
export async function connectWallet() {
  if (!window.ethereum) throw new Error('Install a browser wallet such as MetaMask.');
  const [account] = await window.ethereum.request({ method: 'eth_requestAccounts' });
  const client = createClient({ chain: studionet, account, provider: window.ethereum });
  await client.connect('studionet');
  return { client, account };
}
export async function writeContract(client, address, functionName, args = [], value = 0n) {
  if (!address) throw new Error('Set a contract address first.');
  const tx = await client.writeContract({ address, functionName, args, value });
  return typeof tx === 'string' ? tx : (tx.txId || tx.hash || String(tx));
}
export async function waitTransaction(client, hash, onUpdate = () => {}) {
  for (let i = 0; i < 120; i += 1) {
    const info = await client.getTransaction({ hash });
    const status = info?.statusName || info?.status_name || info?.status;
    const result = info?.txExecutionResultName || info?.tx_execution_result_name || info?.resultName || info?.result_name;
    onUpdate(status, result);
    if (['FAILED', 'REJECTED', 'CANCELLED'].includes(status)) throw new Error(`Transaction failed: ${status}${result ? ` (${result})` : ''}`);
    if (status === 'ACCEPTED' || status === 'FINALIZED') return info;
    await new Promise((resolve) => setTimeout(resolve, 3000));
  }
  throw new Error('Transaction is still processing; keep the hash and sync again.');
}
export async function readSubscription(address, id) {
  if (!address) throw new Error('Set a contract address first.');
  const client = makeReadClient();
  return client.readContract({ address, functionName: 'read_subscription', args: [BigInt(id)] });
}
