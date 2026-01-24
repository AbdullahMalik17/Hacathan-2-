'use client';

import { useEffect, useState, useRef } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { fetchLogs } from '@/app/actions';

export default function AgentTerminal() {
  const [logs, setLogs] = useState<any[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const loadLogs = async () => {
      const data = await fetchLogs();
      setLogs(data);
    };

    loadLogs();
    const interval = setInterval(loadLogs, 2000); // Poll every 2s
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="bg-black border border-green-900 rounded-lg overflow-hidden font-mono text-xs shadow-[0_0_20px_rgba(0,255,0,0.1)]">
      <div className="bg-green-900/20 px-4 py-2 border-b border-green-900 flex justify-between items-center">
        <span className="text-green-500 font-bold flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          ORCHESTRATOR TERMINAL
        </span>
        <span className="text-green-700">v2.0.0 (PLATINUM)</span>
      </div>
      <ScrollArea className="h-[300px] p-4 bg-black/90">
        <div className="space-y-1">
          {logs.map((log, i) => (
            <div key={i} className="flex gap-2 text-green-400/80 hover:text-green-400 transition-colors">
              <span className="text-green-700 shrink-0">
                [{new Date(log.timestamp).toLocaleTimeString()}]
              </span>
              <span className="text-blue-500 font-bold shrink-0 w-24">
                {log.actor?.toUpperCase()}
              </span>
              <span className="text-yellow-600 shrink-0 w-24">
                {log.action}
              </span>
              <span className="text-gray-300 break-all">
                {typeof log.details === 'string' ? log.details : JSON.stringify(log.details)}
                {log.error && <span className="text-red-500 ml-2">ERROR: {log.error}</span>}
              </span>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
      </ScrollArea>
    </div>
  );
}
