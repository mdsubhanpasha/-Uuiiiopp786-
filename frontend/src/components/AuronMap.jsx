import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Cpu, Zap, Bot, Network, Sparkles, RefreshCw, BarChart2, Shield } from 'lucide-react';
import AgentDrawer from './AgentDrawer';
import VoiceWidget from './VoiceWidget';

// Custom Node for Central Quantum Brain
const QuantumBrainNode = ({ data }) => (
  <div className="relative group cursor-pointer">
    <div className="absolute -inset-1 rounded-full bg-gradient-to-r from-cyan-500 via-sky-400 to-blue-600 opacity-75 blur-md group-hover:opacity-100 transition duration-500 animate-pulse" />
    <div className="relative px-8 py-6 bg-slate-950 border-2 border-cyan-400 rounded-2xl shadow-2xl flex flex-col items-center justify-center text-center">
      <Handle type="source" position={Position.Bottom} className="w-3 h-3 bg-cyan-400 border-2 border-slate-950" />
      <div className="p-3 bg-cyan-500/20 text-cyan-400 rounded-xl mb-2 border border-cyan-500/40">
        <Cpu className="w-8 h-8 animate-spin" style={{ animationDuration: '8s' }} />
      </div>
      <h2 className="text-lg font-black text-white tracking-widest uppercase">QUANTUM BRAIN</h2>
      <p className="text-[10px] font-mono text-cyan-300 font-bold">AURON-4000 QISKIT QAOA</p>
      <div className="mt-2 text-[9px] bg-cyan-950/80 text-cyan-300 px-2 py-0.5 rounded-full border border-cyan-800/80">
        137 Active AI Agents
      </div>
    </div>
  </div>
);

// Custom Node for Departments
const DepartmentNode = ({ data }) => (
  <div className="px-5 py-3 rounded-xl bg-slate-900 border-2 border-purple-500/60 shadow-lg shadow-purple-500/10 flex items-center gap-3 cursor-pointer hover:border-purple-400 transition">
    <Handle type="target" position={Position.Top} className="w-2.5 h-2.5 bg-purple-400" />
    <Handle type="source" position={Position.Bottom} className="w-2.5 h-2.5 bg-purple-400" />
    <div className="p-2 bg-purple-500/20 text-purple-300 rounded-lg">
      <Network className="w-5 h-5" />
    </div>
    <div>
      <h3 className="text-sm font-bold text-white">{data.label}</h3>
      <p className="text-[10px] text-purple-300 font-mono">{data.count} Specialized Agents</p>
    </div>
  </div>
);

// Custom Node for Individual Leaf Agents
const AgentLeafNode = ({ data }) => {
  const getStatusDot = (status) => {
    switch (status) {
      case 'autonomous':
        return 'bg-emerald-400 shadow-emerald-400/50';
      case 'assisted':
        return 'bg-amber-400 shadow-amber-400/50';
      default:
        return 'bg-blue-400 shadow-blue-400/50';
    }
  };

  return (
    <div
      onClick={() => data.onSelectAgent(data.agent)}
      className="px-3 py-2 rounded-lg bg-slate-950/90 border border-slate-800 hover:border-cyan-400/80 shadow-md transition duration-200 cursor-pointer flex items-center gap-2 group hover:scale-105"
    >
      <Handle type="target" position={Position.Top} className="w-2 h-2 bg-cyan-500" />
      <span className={`w-2 h-2 rounded-full ${getStatusDot(data.agent.status)} shadow-sm`} />
      <div className="truncate max-w-[120px]">
        <div className="text-[11px] font-semibold text-slate-200 group-hover:text-cyan-300 truncate">
          {data.agent.name}
        </div>
        <div className="text-[9px] text-slate-500 font-mono truncate">{data.agent.skill}</div>
      </div>
    </div>
  );
};

const nodeTypes = {
  quantumBrain: QuantumBrainNode,
  department: DepartmentNode,
  agentLeaf: AgentLeafNode,
};

export default function AuronMap() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [companyData, setCompanyData] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);
  const [quantumResult, setQuantumResult] = useState(null);
  const [isOptimizing, setIsOptimizing] = useState(false);

  const handleSelectAgent = useCallback((agent) => {
    setSelectedAgent(agent);
    setExecutionResult(null);
    setIsDrawerOpen(true);
  }, []);

  const fetchCompanyData = async () => {
    try {
      const res = await fetch('/api/health');
      if (!res.ok) throw new Error('Backend offline');
      const data = await fetch('/');
      const json = await data.json();
      setCompanyData(json);
      generateGraphNodesAndEdges(json);
    } catch (err) {
      console.error('Error fetching company OS data:', err);
      // Fallback mock dataset
      fetch('/agents/registry').catch(() => {});
    }
  };

  useEffect(() => {
    fetchCompanyData();
  }, []);

  const generateGraphNodesAndEdges = (data) => {
    if (!data || !data.agents) return;

    const initialNodes = [];
    const initialEdges = [];

    // 1. Central Quantum Brain Node
    initialNodes.push({
      id: 'quantum_core',
      type: 'quantumBrain',
      position: { x: 1200, y: 50 },
      data: { label: 'QUANTUM BRAIN' },
    });

    // 2. Department Nodes (7 Departments)
    const departments = data.departments || [
      'Sales', 'Deals', 'Marketing', 'Operations', 'Intelligence', 'Customer', 'BackOffice'
    ];

    const deptSpacingX = 380;
    const deptStartY = 350;
    const startX = 1200 - ((departments.length - 1) * deptSpacingX) / 2;

    departments.forEach((dept, index) => {
      const deptNodeId = `dept_${dept.toLowerCase()}`;
      const deptX = startX + index * deptSpacingX;
      const deptY = deptStartY;

      const deptAgents = data.agents.filter((a) => a.department === dept);

      initialNodes.push({
        id: deptNodeId,
        type: 'department',
        position: { x: deptX, y: deptY },
        data: { label: dept, count: deptAgents.length },
      });

      // Edge from Central Brain to Department
      initialEdges.push({
        id: `e_core_${deptNodeId}`,
        source: 'quantum_core',
        target: deptNodeId,
        animated: true,
        style: { stroke: '#38bdf8', strokeWidth: 2 },
      });

      // 3. Agent Leaf Nodes
      const agentsPerRow = 4;
      const leafSpacingX = 150;
      const leafSpacingY = 70;
      const leafStartY = deptY + 120;
      const leafStartX = deptX - ((agentsPerRow - 1) * leafSpacingX) / 2;

      deptAgents.forEach((agent, agentIdx) => {
        const row = Math.floor(agentIdx / agentsPerRow);
        const col = agentIdx % agentsPerRow;
        const leafX = leafStartX + col * leafSpacingX;
        const leafY = leafStartY + row * leafSpacingY;

        initialNodes.push({
          id: agent.id,
          type: 'agentLeaf',
          position: { x: leafX, y: leafY },
          data: { agent, onSelectAgent: handleSelectAgent },
        });

        // Edge from Dept to Agent Leaf
        initialEdges.push({
          id: `e_${deptNodeId}_${agent.id}`,
          source: deptNodeId,
          target: agent.id,
          style: { stroke: '#64748b', strokeWidth: 1, opacity: 0.5 },
        });
      });
    });

    setNodes(initialNodes);
    setEdges(initialEdges);
  };

  const handleRunAgent = async (agentId) => {
    setIsExecuting(true);
    try {
      const res = await fetch(`/agents/${agentId}/run?task=Execute high-priority operational campaign`);
      const json = await res.json();
      setExecutionResult(json);
    } catch (e) {
      console.error('Error running agent:', e);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleRunQuantumOptimization = async () => {
    setIsOptimizing(true);
    try {
      const res = await fetch('/quantum/optimize?qubits=6');
      const json = await res.json();
      setQuantumResult(json.quantum_brain_result);
    } catch (e) {
      console.error('Quantum optimization error:', e);
    } finally {
      setIsOptimizing(false);
    }
  };

  return (
    <div className="w-screen h-screen relative bg-slate-950 overflow-hidden select-none">
      {/* Header Overlay */}
      <div className="absolute top-6 left-6 z-30 bg-slate-900/90 backdrop-blur-xl border border-slate-800 p-4 rounded-2xl shadow-2xl flex items-center justify-between gap-6 max-w-2xl">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-cyan-500/20 text-cyan-400 rounded-xl border border-cyan-500/40">
            <Sparkles className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl font-black text-white tracking-wider flex items-center gap-2">
              AURON-CORP-137Q
              <span className="text-[10px] px-2 py-0.5 rounded-md bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                AURON-4000
              </span>
            </h1>
            <p className="text-xs text-slate-400 font-mono">
              Mohammad Subhan Pasha | 137 AI Agents across 7 Departments
            </p>
          </div>
        </div>

        <button
          onClick={handleRunQuantumOptimization}
          disabled={isOptimizing}
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-purple-500/20 transition disabled:opacity-50"
        >
          {isOptimizing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
          QAOA Optimize
        </button>
      </div>

      {/* Quantum QAOA Result Modal / Banner */}
      {quantumResult && (
        <div className="absolute top-28 left-6 z-30 max-w-md bg-slate-900/95 backdrop-blur-xl border border-purple-500/40 p-4 rounded-2xl shadow-2xl space-y-2">
          <div className="flex justify-between items-center border-b border-slate-800 pb-2">
            <span className="text-xs font-bold text-purple-400 uppercase tracking-wider flex items-center gap-1.5">
              <BarChart2 className="w-4 h-4" /> Quantum QAOA Optimization Complete
            </span>
            <button onClick={() => setQuantumResult(null)} className="text-slate-400 hover:text-white text-xs">✕</button>
          </div>
          <div className="text-xs font-mono text-slate-300 space-y-1">
            <p><strong>Bitstring:</strong> [{quantumResult.optimal_bitstring?.join(', ')}]</p>
            <p><strong>Qubits:</strong> {quantumResult.qubits} | <strong>Depth:</strong> {quantumResult.quantum_circuit_depth}</p>
            <p className="text-purple-300"><strong>Primary Cluster:</strong> {quantumResult.workload_distribution?.quantum_cluster_a_primary?.join(', ')}</p>
          </div>
        </div>
      )}

      {/* Live Map React Flow Canvas */}
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.1}
        maxZoom={1.5}
        className="bg-transparent"
      >
        <Background color="#1e293b" gap={24} size={1} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            if (node.type === 'quantumBrain') return '#38bdf8';
            if (node.type === 'department') return '#a855f7';
            return '#22c55e';
          }}
          maskColor="rgba(2, 6, 23, 0.8)"
          className="bg-slate-900 border border-slate-800 rounded-xl"
        />
      </ReactFlow>

      {/* Slide-over Agent Drawer */}
      <AgentDrawer
        agent={selectedAgent}
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        onRunAgent={handleRunAgent}
        isExecuting={isExecuting}
        executionResult={executionResult}
      />

      {/* Floating VOX-AI Voice Control Widget */}
      <VoiceWidget
        onVoiceAgentExecuted={(payload) => {
          if (payload.agent_payload) {
            setSelectedAgent({
              id: payload.agent_payload.agent_id,
              name: payload.agent_payload.agent_name,
              department: payload.agent_payload.department,
              skill: payload.agent_payload.skill,
              status: payload.agent_payload.status,
              description: payload.spoken_response,
            });
            setExecutionResult(payload.agent_payload);
            setIsDrawerOpen(true);
          }
        }}
      />
    </div>
  );
}
