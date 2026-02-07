import React, { useState, useEffect, useRef } from 'react';
import { Shield, AlertTriangle, Terminal, Activity, Lock, Cpu, Download, MessageSquare, Zap } from 'lucide-react';

const App = () => {
  const [url, setUrl] = useState('');
  const [status, setStatus] = useState('STANDBY'); // STANDBY, SCANNING, BREACH
  const [logs, setLogs] = useState(['> VANGUARD ALIEN CORE INITIALIZED...', '> WAITING FOR TARGET INPUT...']);
  const [progress, setProgress] = useState(0);
  const [report, setReport] = useState(null);

  const addLog = (msg) => {
    setLogs(prev => [...prev.slice(-10), `> ${msg}`]);
  };

  const startAudit = async () => {
    if (!url) return;
    setStatus('SCANNING');
    setProgress(0);
    setReport(null);
    
    // Television Simulation Sequence
    addLog(`CONNECTING TO TARGET: ${url}`);
    
    const interval = setInterval(() => {
      setProgress(p => {
        if (p >= 100) {
          clearInterval(interval);
          return 100;
        }
        return p + 1;
      });
    }, 50);

    // After simulation, show the result
    setTimeout(async () => {
      addLog(`BYPASSING TARGET FIREWALL...`);
      addLog(`EXTRACTING API HEADERS...`);
      addLog(`CRITICAL VULNERABILITY DETECTED.`);
      
      setReport({
        id: "VGD-SAI-2026-X838",
        score: "94.8%",
        leaks: ["Private API Key Exposure", "CallbackQueryHandler Timeout", "Unencrypted Webhook"],
        contact: "@ICEGODSICEDEVIL"
      });
      setStatus('BREACH');
    }, 5500);
  };

  return (
    <div className="min-h-screen bg-black text-green-500 font-mono p-4 flex flex-col items-center justify-center relative overflow-hidden">
      {/* Scanline/CRT Effect Overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_2px,3px_100%] pointer-events-none z-50 opacity-40"></div>
      
      {/* Main Console Frame */}
      <div className="w-full max-w-6xl border-4 border-zinc-800 rounded-3xl bg-zinc-900 p-3 shadow-[0_0_100px_rgba(0,0,0,1)] relative z-20 overflow-hidden">
        <div className="bg-black rounded-2xl p-8 border-2 border-zinc-800 relative shadow-inner">
          
          {/* Header Bar */}
          <div className="flex justify-between items-center border-b border-green-900/50 pb-6 mb-8">
            <div className="flex items-center gap-3">
              <Shield className={status === 'BREACH' ? "text-red-600 animate-pulse w-8 h-8" : "text-green-500 w-8 h-8"} />
              <div>
                <h1 className="text-2xl font-black tracking-widest uppercase flex items-center gap-2">
                  VANGUARD <span className={status === 'BREACH' ? "text-red-500" : "text-blue-500"}>SECURITY</span>
                </h1>
                <p className="text-[10px] text-zinc-500 tracking-[0.3em]">ALIEN_CORE_LOGIC // UNIT_838</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-xs flex items-center gap-2 justify-end">
                <Activity size={12} className="animate-pulse" /> SYSTEM_LIVE
              </div>
              <div className="text-[10px] text-zinc-600 mt-1">NODE: LAGOS_MAINNET_01</div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
            {/* Left Column: Console Display */}
            <div className="space-y-6">
              <div className="bg-zinc-950 p-6 rounded-lg border border-green-900/30 h-80 flex flex-col justify-end shadow-inner relative">
                <div className="absolute top-2 right-3 text-[10px] text-green-900 uppercase">Audit_Log_Monitor</div>
                <div className="space-y-1">
                  {logs.map((log, i) => (
                    <div key={i} className={`text-xs md:text-sm ${log.includes('CRITICAL') || log.includes('BREACH') ? 'text-red-500 font-black' : 'text-green-500/80'}`}>
                      {log}
                    </div>
                  ))}
                  <div className="animate-pulse inline-block w-2 h-4 bg-green-500 ml-1"></div>
                </div>
              </div>
              
              <div className="flex flex-col md:flex-row gap-3">
                <input 
                  type="text" 
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="ENTER TARGET DOMAIN/URL..."
                  className="flex-1 bg-zinc-950 border border-green-900/50 p-4 outline-none focus:border-green-400 text-green-400 font-mono text-sm placeholder:text-green-900"
                />
                <button 
                  onClick={startAudit}
                  disabled={status === 'SCANNING'}
                  className="bg-green-600 hover:bg-green-400 text-black font-black px-8 py-4 transition-all active:scale-95 disabled:opacity-50"
                >
                  RUN_SCAN
                </button>
              </div>
            </div>

            {/* Right Column: Visual Threat Analysis */}
            <div className="bg-zinc-950/50 rounded-2xl border border-zinc-800 p-8 flex flex-col items-center justify-center min-h-[400px]">
              {status === 'STANDBY' && (
                <div className="text-center opacity-30">
                  <Cpu size={100} className="mx-auto mb-6 animate-spin-slow" />
                  <p className="text-sm tracking-widest italic">WAITING FOR TARGET PACKETS...</p>
                </div>
              )}

              {status === 'SCANNING' && (
                <div className="w-full text-center">
                  <div className="text-6xl font-black mb-6 tabular-nums">{progress}%</div>
                  <div className="w-full bg-zinc-900 h-6 rounded-full overflow-hidden border border-zinc-800 p-1">
                    <div className="bg-gradient-to-r from-green-900 to-green-400 h-full transition-all duration-100" style={{width: `${progress}%`}}></div>
                  </div>
                  <div className="mt-8 flex justify-center gap-2">
                     <span className="w-2 h-2 rounded-full bg-green-500 animate-ping"></span>
                     <p className="text-xs uppercase tracking-tighter">Decompiling Target Logic...</p>
                  </div>
                </div>
              )}

              {status === 'BREACH' && report && (
                <div className="w-full animate-in zoom-in duration-500">
                  <div className="bg-red-600/10 border border-red-600 p-6 rounded-lg text-center mb-6">
                    <AlertTriangle size={48} className="text-red-500 mx-auto mb-4 animate-bounce" />
                    <h2 className="text-red-500 text-3xl font-black uppercase mb-1">Vulnerability SAI Found</h2>
                    <p className="text-xs text-zinc-400 uppercase font-bold tracking-widest">{report.id}</p>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 mb-8">
                    <div className="bg-zinc-900 p-4 border border-zinc-800 rounded text-center">
                      <p className="text-[10px] text-zinc-500 uppercase">Threat Level</p>
                      <p className="text-2xl font-black text-red-500">{report.score}</p>
                    </div>
                    <div className="bg-zinc-900 p-4 border border-zinc-800 rounded text-center">
                      <p className="text-[10px] text-zinc-500 uppercase">Status</p>
                      <p className="text-2xl font-black text-yellow-500 italic uppercase">Exposed</p>
                    </div>
                  </div>

                  <div className="flex flex-col gap-3">
                    <button className="flex items-center justify-center gap-3 bg-white text-black font-black py-4 rounded hover:bg-zinc-200 transition-all">
                      <Download size={20} /> GENERATE AUDIT PDF
                    </button>
                    <a 
                      href={`https://t.me/${report.contact.replace('@','')}`}
                      className="flex items-center justify-center gap-3 border-2 border-blue-500 text-blue-500 font-black py-4 rounded hover:bg-blue-500 hover:text-white transition-all shadow-[0_0_20px_rgba(59,130,246,0.2)]"
                    >
                      <Zap size={20} /> SECURE WITH ALIEN CORE
                    </a>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Footer / Footer Deck */}
      <div className="mt-10 flex flex-col md:flex-row gap-8 text-[10px] text-zinc-600 uppercase tracking-widest items-center">
        <span>Institutional Security Layer</span>
        <span className="h-1 w-1 bg-zinc-800 rounded-full"></span>
        <span>Based on Vanguard World Fund SAI 838</span>
        <span className="h-1 w-1 bg-zinc-800 rounded-full"></span>
        <span>Lagos Cyber Security Initiative</span>
      </div>
    </div>
  );
};

export default App;


