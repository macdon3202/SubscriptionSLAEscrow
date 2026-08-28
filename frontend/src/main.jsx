import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';
import { readSubscription, connectWallet, writeContract, waitTransaction } from './genlayer.js';

const DEFAULT_ADDRESS = import.meta.env.VITE_CONTRACT_ADDRESS || '';

function App() {
  const [page, setPage] = useState('home');
  const [address] = useState(localStorage.getItem('sla_address') || DEFAULT_ADDRESS);
  const [client, setClient] = useState(null);
  const [wallet, setWallet] = useState('');
  const [message, setMessage] = useState('Connect wallet to begin.');
  const [state, setState] = useState(null);
  const [ids, setIds] = useState({ plan: 0, subscription: 0, observation: 0 });
  const [evidence, setEvidence] = useState({ url: 'https://gateway.pinata.cloud/ipfs/bafkreibfhuc7pviaoo25ep7anudcugotxpl3xbmjkosq3ms4tcesuk7glm', digest: 'sha256:svc-2026-08-28-001' });
  const [plan, setPlan] = useState({ name: 'RPC Standard', price: '10000000000000000', partial: '30', full: '120', response: '1000', requests: '100000' });

  const act = async (method, args, value = 0n, readAfter = false) => {
    try {
      if (!client) throw new Error('Connect wallet first.');
      const tx = await writeContract(client, address, method, args, value);
      setMessage(`${method} submitted: ${tx}`);
      await waitTransaction(client, tx, (status, result) => setMessage(`${method}: ${status || 'PENDING'}${result ? ` / ${result}` : ''}`));
      if (readAfter) setState(await readSubscription(address, ids.subscription));
      setMessage(`${method} accepted; state synced.`);
    } catch (error) { setMessage(error.message); }
  };
  const field = (key, label) => <label key={key}>{label}<input value={plan[key]} onChange={(e) => setPlan({ ...plan, [key]: e.target.value })} /></label>;
  return <div className="app">
    <header><div><span className="eyebrow">SUBSCRIPTION SLA ESCROW</span><h1>Pay for uptime you can verify.</h1><p className="lede">Prepaid GEN is settled against public incident evidence and on-chain SLA rules.</p></div><div className="network"><span className="dot"/><a href={`https://explorer-studio.genlayer.com/address/${address || DEFAULT_ADDRESS}`} target="_blank" rel="noreferrer">Studionet</a><button onClick={async () => { try { const result = await connectWallet(); setClient(result.client); setWallet(result.account); setMessage('Wallet connected.'); } catch (error) { setMessage(error.message); } }}>{wallet ? `${wallet.slice(0, 8)}…` : 'Connect wallet'}</button></div></header>
    <nav><button className={page === 'home' ? 'active' : ''} onClick={() => setPage('home')}>Overview</button><button className={page === 'provider' ? 'active' : ''} onClick={() => setPage('provider')}>Provider plan</button><button className={page === 'subscriber' ? 'active' : ''} onClick={() => setPage('subscriber')}>Subscriber flow</button><button className={page === 'how' ? 'active' : ''} onClick={() => setPage('how')}>How it works</button></nav>
    <main>
      {page === 'home' && <section className="hero"><div><span className="pill">ON-CHAIN SERVICE PROTECTION</span><h2>Cancellation is backed by evidence, not a support ticket.</h2><p>Status pages use inconsistent language. GenLayer interprets outage evidence; deterministic code applies SLA refund bands.</p></div><div className="flow"><div><b>01</b><span>Fund period</span></div><div><b>02</b><span>Observe incidents</span></div><div><b>03</b><span>Settle SLA</span></div></div></section>}
      {page === 'provider' && <section className="panel"><span className="eyebrow">PROVIDER PLAN</span><h2>Register SLA thresholds</h2><p>Publish the policy that determines settlement.</p><div className="formgrid">{Object.entries({ name: 'Plan name', price: 'Period price (wei)', partial: 'Partial refund after minutes', full: 'Full refund after minutes', response: 'Response limit (ms)', requests: 'Request limit' }).map(([key, label]) => field(key, label))}</div><button className="primary" onClick={() => act('register_plan', [plan.name, BigInt(plan.price), BigInt(plan.partial), BigInt(plan.full), BigInt(plan.response), BigInt(plan.requests)])}>Register plan</button><p className="notice">{message}</p></section>}
      {page === 'subscriber' && <section className="panel"><span className="eyebrow">SUBSCRIBER FLOW</span><h2>Fund, observe, settle</h2><div className="formgrid"><label>Plan ID<input type="number" value={ids.plan} onChange={(e) => setIds({ ...ids, plan: Number(e.target.value) })} /></label><label>Subscription ID<input type="number" value={ids.subscription} onChange={(e) => setIds({ ...ids, subscription: Number(e.target.value) })} /></label><label>Observation ID<input type="number" value={ids.observation} onChange={(e) => setIds({ ...ids, observation: Number(e.target.value) })} /></label><label>Evidence URL<input value={evidence.url} onChange={(e) => setEvidence({ ...evidence, url: e.target.value })} /></label><label>Evidence digest<input value={evidence.digest} onChange={(e) => setEvidence({ ...evidence, digest: e.target.value })} /></label><label>Observed at (minutes)<input type="number" value={150} readOnly /></label></div><div className="actions"><button className="primary" onClick={() => act('open_subscription', [BigInt(ids.plan), 100n, 200n], BigInt(plan.price), true)}>Open subscription</button><button onClick={() => act('submit_observation', [BigInt(ids.subscription), evidence.url, evidence.digest, 150n], 0n, true)}>Submit observation</button><button onClick={() => act('classify_observation', [BigInt(ids.observation)], 0n, true)}>Classify</button><button onClick={() => act('close_evidence_window', [BigInt(ids.subscription)], 0n, true)}>Close evidence</button><button onClick={() => act('request_cancellation', [BigInt(ids.subscription)], 0n, true)}>Cancel</button><button onClick={() => act('settle', [BigInt(ids.subscription)], 0n, true)}>Settle</button><button onClick={async () => { try { setState(await readSubscription(address, ids.subscription)); setMessage('Readback confirmed.'); } catch (error) { setMessage(error.message); } }}>Sync state</button></div><p className="notice">{message}</p>{state && <pre>{JSON.stringify(state, (_, value) => typeof value === 'bigint' ? value.toString() : value, 2)}</pre>}</section>}
      {page === 'how' && <section className="panel"><span className="eyebrow">HOW IT WORKS</span><h2>A service period with an auditable exit.</h2><div className="steps"><div><b>1. Publish</b><p>A provider registers price, response limit, request limit, and two downtime thresholds.</p></div><div><b>2. Fund</b><p>A subscriber locks the exact period price in GEN.</p></div><div><b>3. Observe</b><p>Public status evidence is submitted with a single-use digest and classified by GenLayer.</p></div><div><b>4. Settle</b><p>Accumulated downtime maps to full payment, a partial refund, or a full refund.</p></div></div></section>}
    </main><footer><span>Subscription SLA Escrow</span><span>Contract state is the source of truth.</span></footer>
  </div>;
}
createRoot(document.getElementById('root')).render(<App />);
