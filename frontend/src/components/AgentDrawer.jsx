import React from 'react';
import { Bot, Zap, Cpu, Activity, ShieldCheck, User, Sparkles } from 'lucide-react';

export default function AgentDrawer({ agent, isOpen, onClose, onRunAgent, isExecuting, executionResult }) {
  if (!isOpen || !agent) return null;

  const getStatusColor = (status) => {
    switch (status) {
      case 'autonomous':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40';
      case 'assisted':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      default:
        return 'bg-blue-500/20 text-blue-400 border-blue-500/40';
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 w-full max-w-md bg-slate-900/95 backdrop-blur-xl border-l border-slate-800 p-6 z-50 shadow-2xl flex flex-col justify-between transition-all duration-300">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white tracking-wide">{agent.name}</h2>
              <p className="text-xs text-slate-400 font-mono">ID: {agent.id}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-800 transition"
          >
            ✕
          </button>
        </div>

        {/* Metadata Badges */}
        <div className="grid grid-cols-2 gap-3 my-5">
          <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80">
            <span className="text-xs text-slate-400 block mb-1">Department</span>
            <span className="text-sm font-semibold text-cyan-300 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" /> {agent.department}
            </span>
          </div>

          <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80">
            <span className="text-xs text-slate-400 block mb-1">Execution Mode</span>
            <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getStatusColor(agent.status)} uppercase tracking-wider`}>
              {agent.status}
            </span>
          </div>
        </div>

        {/* Skill Details */}
        <div className="space-y-4">
          <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800/80">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" /> Primary Skill Set
            </h3>
            <p className="text-sm text-slate-200 font-medium">{agent.skill}</p>
          </div>

          <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800/80">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-cyan-400" /> Agent Description & Role
            </h3>
            <p className="text-sm text-slate-300 leading-relaxed">{agent.description}</p>
          </div>
        </div>

        {/* Execution Output Panel */}
        {executionResult && (
          <div className="mt-5 p-4 bg-emerald-950/20 border border-emerald-500/30 rounded-xl">
            <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5 mb-2">
              <Activity className="w-4 h-4 animate-pulse" /> Task Execution Output
            </h4>
            <div className="text-xs font-mono text-slate-300 bg-slate-950/80 p-3 rounded-lg border border-slate-800 space-y-1.5 max-h-40 overflow-y-auto">
              <p className="text-cyan-400"><strong>Reasoning:</strong> {executionResult.reasoning}</p>
              <p className="text-emerald-300"><strong>Output:</strong> {executionResult.output}</p>
              <div className="pt-1 flex justify-between text-[10px] text-slate-500 border-t border-slate-800">
                <span>Latency: {executionResult.metadata?.latency_ms || 120}ms</span>
                <span>Quantum Optimization: Enabled</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Action CTA */}
      <div className="pt-4 border-t border-slate-800">
        <button
          onClick={() => onRunAgent(agent.id)}
          disabled={isExecuting}
          className="w-full py-3 px-4 rounded-xl font-bold text-sm bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {isExecuting ? (
            <>
              <Activity className="w-4 h-4 animate-spin text-white" /> Executing Task...
            </>
          ) : (
            <>
              <Zap className="w-4 h-4" /> Run Agent Task
            </>
          )}
        </button>
      </div>
    </div>
  );
}
