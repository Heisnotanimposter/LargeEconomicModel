"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";

interface Agent {
  id: string;
  name: string;
  role: string;
  status: "idle" | "running" | "success" | "error";
  color: string;
}

export default function MarketingStudio() {
  // Setup project details
  const [projectName, setProjectName] = useState("ZBDD-Solver");
  const [projectDesc, setProjectDesc] = useState(
    "Zero-Suppressed Binary Decision Diagram solver that integrates directly with Physics-Informed Neural Networks to speed up constraint optimization by 15x."
  );
  const [apiKey, setApiKey] = useState("");
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<"strategy" | "copy" | "seo" | "qa">("strategy");

  // Agent states
  const [agents, setAgents] = useState<Agent[]>([
    {
      id: "strategist",
      name: "Campaign Strategist",
      role: "Audience segmentation & launch roadmaps",
      status: "idle",
      color: "border-blue-500 text-blue-400 bg-blue-950/20"
    },
    {
      id: "copywriter",
      name: "Technical Copywriter",
      role: "Drafts Show HN, subreddit segmentations, and LinkedIn posts",
      status: "idle",
      color: "border-purple-500 text-purple-400 bg-purple-950/20"
    },
    {
      id: "seo",
      name: "SEO Auditor",
      role: "Optimizes GitHub topics and indexing keywords",
      status: "idle",
      color: "border-emerald-500 text-emerald-400 bg-emerald-950/20"
    },
    {
      id: "responder",
      name: "Social Responder",
      role: "Drafts Q&A answers to handle community feedback",
      status: "idle",
      color: "border-rose-500 text-rose-400 bg-rose-950/20"
    }
  ]);

  // Campaign Output
  const [campaign, setCampaign] = useState<{
    strategy: string;
    copy: string;
    seo: string;
  } | null>(null);

  // Q&A simulator states
  const [qaQuestion, setQaQuestion] = useState("Why not use traditional solvers like Gurobi instead of ZBDDs?");
  const [qaAnswer, setQaAnswer] = useState("");
  const [qaLoading, setQaLoading] = useState(false);

  const consoleEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (consoleEndRef.current) {
      consoleEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs]);

  // Run Campaign Generation Pipeline
  const handleLaunchCampaign = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;

    setLoading(false);
    setCampaign(null);
    setLogs([]);
    setAgents(prev => prev.map(a => ({ ...a, status: "idle" })));

    setLoading(true);
    
    // Simulate Agent Step Logs
    const logSteps = [
      { agent: "strategist", text: "⚡ Strategist: Initializing campaign parameters..." },
      { agent: "strategist", text: "⚡ Strategist: Fetching project metadata..." },
      { agent: "strategist", text: "⚡ Strategist: Analyzing target personas (ML researchers vs C++ systems engineers)..." },
      { agent: "strategist", text: "⚡ Strategist: Strategy draft completed." },
      { agent: "copywriter", text: "✍️ Copywriter: Initializing templates for Show HN and subreddits..." },
      { agent: "copywriter", text: "✍️ Copywriter: Writing Hacker News submission comment hook..." },
      { agent: "copywriter", text: "✍️ Copywriter: Drafting r/MachineLearning and r/cpp custom segmentation files..." },
      { agent: "copywriter", text: "✍️ Copywriter: Copywriting output generated." },
      { agent: "seo", text: "🔍 SEO Auditor: Performing GitHub search audit..." },
      { agent: "seo", text: "🔍 SEO Auditor: Identifying high-traffic keywords (physics-informed-ml, cuda)..." },
      { agent: "seo", text: "🔍 SEO Auditor: Generating README structured badge designs..." },
      { agent: "seo", text: "🔍 SEO Auditor: Audit complete." }
    ];

    // Trigger API call
    try {
      // Step-by-step log output simulation
      let logIndex = 0;
      const runLogs = () => {
        if (logIndex < logSteps.length) {
          const step = logSteps[logIndex];
          setLogs(prev => [...prev, step.text]);
          
          setAgents(prev => prev.map(a => {
            if (a.id === step.agent) {
              return { ...a, status: "running" };
            }
            // Mark previous as success
            const prevAgentIndex = prev.findIndex(item => item.id === step.agent);
            if (prevAgentIndex > 0) {
              const prevAgent = prev[prevAgentIndex - 1];
              if (prevAgent.status === "running") {
                prevAgent.status = "success";
              }
            }
            return a;
          }));

          logIndex++;
          setTimeout(runLogs, 600);
        } else {
          // Finalize status
          setAgents(prev => prev.map(a => a.id !== "responder" ? { ...a, status: "success" } : a));
          fetchCampaignData();
        }
      };

      runLogs();

    } catch (err) {
      setLogs(prev => [...prev, "❌ Error: Failed to execute agent workflows."]);
      setLoading(false);
    }
  };

  const fetchCampaignData = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/marketing/campaigns", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_name: projectName,
          project_desc: projectDesc,
          api_key: apiKey
        })
      });
      const data = await res.json();
      if (data.status === "success") {
        setCampaign(data.campaign);
        setLogs(prev => [...prev, "🎉 Success: All agents successfully compiled results."]);
      } else {
        setLogs(prev => [...prev, "❌ Error: API request failed."]);
      }
    } catch (e) {
      setLogs(prev => [...prev, "❌ Error: Connection to agent backend failed."]);
    } finally {
      setLoading(false);
    }
  };

  // Run Q&A Responder Simulation
  const handleAskQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!qaQuestion.trim() || qaLoading) return;

    setQaLoading(true);
    setQaAnswer("");
    setAgents(prev => prev.map(a => a.id === "responder" ? { ...a, status: "running" } : a));

    try {
      const res = await fetch("http://localhost:8000/api/v1/marketing/simulate-qa", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_name: projectName,
          question: qaQuestion,
          api_key: apiKey
        })
      });
      const data = await res.json();
      if (data.status === "success") {
        setQaAnswer(data.answer);
        setAgents(prev => prev.map(a => a.id === "responder" ? { ...a, status: "success" } : a));
      } else {
        setQaAnswer("Error generating reply.");
        setAgents(prev => prev.map(a => a.id === "responder" ? { ...a, status: "error" } : a));
      }
    } catch (err) {
      setQaAnswer("Error: Backend offline.");
      setAgents(prev => prev.map(a => a.id === "responder" ? { ...a, status: "error" } : a));
    } finally {
      setQaLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#060608] text-zinc-100 font-sans">
      {/* Top Nav Header */}
      <header className="border-b border-zinc-800 bg-[#0c0c0e]/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-baseline space-x-3">
            <h1 className="text-xl font-bold tracking-tighter text-white">
              LEM <span className="text-zinc-500 font-normal">Command Room</span>
            </h1>
            <span className="text-xs bg-zinc-800 px-2 py-0.5 rounded font-mono text-zinc-400">Marketing Studio</span>
          </div>
          <nav className="flex space-x-6 text-sm font-medium">
            <Link href="/" className="text-zinc-400 hover:text-white transition">
              Macro API Center
            </Link>
            <Link href="/marketing-team" className="text-white border-b-2 border-white pb-4 -mb-4 transition">
              AI Marketing Team
            </Link>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Control Panel: Form Inputs & Active Agents */}
        <div className="lg:col-span-1 space-y-6">
          
          {/* Campaign Input Section */}
          <section className="bg-[#0b0b0d] border border-zinc-800 rounded-xl p-5 shadow-2xl">
            <h2 className="text-md font-semibold text-white mb-4 flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-blue-500"></span> Launch Campaign
            </h2>
            <form onSubmit={handleLaunchCampaign} className="space-y-4">
              <div>
                <label className="block text-xs font-mono text-zinc-400 mb-1">PROJECT NAME</label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  className="w-full bg-[#121215] border border-zinc-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-zinc-500 transition"
                  placeholder="e.g. ZBDD-Solver"
                  required
                />
              </div>
              
              <div>
                <label className="block text-xs font-mono text-zinc-400 mb-1">PROJECT DESCRIPTION</label>
                <textarea
                  value={projectDesc}
                  onChange={(e) => setProjectDesc(e.target.value)}
                  rows={4}
                  className="w-full bg-[#121215] border border-zinc-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-zinc-500 transition"
                  placeholder="Describe your tech platform features..."
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-mono text-zinc-400 mb-1 flex justify-between">
                  <span>GEMINI API KEY (OPTIONAL)</span>
                  <span className="text-[10px] text-zinc-500 font-sans">Using mock solver if empty</span>
                </label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="w-full bg-[#121215] border border-zinc-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-zinc-500 transition"
                  placeholder="AI Key..."
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 rounded-lg bg-white text-black font-semibold text-sm hover:bg-zinc-200 active:bg-zinc-300 disabled:opacity-50 transition"
              >
                {loading ? "Running Agent loops..." : "Start Marketing Team"}
              </button>
            </form>
          </section>

          {/* Marketing Team Grid */}
          <section className="bg-[#0b0b0d] border border-zinc-800 rounded-xl p-5 shadow-2xl">
            <h2 className="text-md font-semibold text-white mb-4">Active Marketing Agents</h2>
            <div className="space-y-3">
              {agents.map((agent) => (
                <div
                  key={agent.id}
                  className={`border rounded-lg p-3 flex items-start gap-3 transition ${agent.color}`}
                >
                  <div className="mt-1">
                    {agent.status === "running" ? (
                      <span className="flex h-2.5 w-2.5 relative">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-current opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-current"></span>
                      </span>
                    ) : agent.status === "success" ? (
                      <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 inline-block"></span>
                    ) : agent.status === "error" ? (
                      <span className="h-2.5 w-2.5 rounded-full bg-rose-500 inline-block"></span>
                    ) : (
                      <span className="h-2.5 w-2.5 rounded-full bg-zinc-600 inline-block"></span>
                    )}
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-white">{agent.name}</h3>
                    <p className="text-[11px] text-zinc-400">{agent.role}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>

        </div>

        {/* Right Content Panels: Execution Console & Content Outputs */}
        <div className="lg:col-span-2 space-y-6">

          {/* Terminal Console Output */}
          <section className="bg-[#0c0c0f] border border-zinc-800 rounded-xl overflow-hidden shadow-2xl font-mono text-xs flex flex-col h-[200px]">
            <div className="bg-[#121216] px-4 py-2 border-b border-zinc-800 flex justify-between items-center">
              <span className="text-zinc-400 text-[10px]">AGENT EXECUTION TERMINAL LOGS</span>
              <div className="flex gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-zinc-800"></span>
                <span className="h-2.5 w-2.5 rounded-full bg-zinc-800"></span>
              </div>
            </div>
            <div className="p-4 flex-1 overflow-y-auto space-y-1.5 text-zinc-400">
              {logs.length === 0 ? (
                <div className="text-zinc-600 italic">Initialize marketing team above to view agent logic logs...</div>
              ) : (
                logs.map((log, index) => (
                  <div key={index} className="leading-relaxed animate-[fadeIn_0.2s_ease-out]">
                    {log}
                  </div>
                ))
              )}
              <div ref={consoleEndRef} />
            </div>
          </section>

          {/* Campaign Outputs Hub */}
          <section className="bg-[#0b0b0d] border border-zinc-800 rounded-xl overflow-hidden shadow-2xl flex flex-col min-h-[400px]">
            
            {/* Tabs */}
            <div className="bg-[#121216] px-4 border-b border-zinc-800 flex gap-4 text-xs font-mono">
              <button
                onClick={() => setActiveTab("strategy")}
                className={`py-3 font-semibold transition ${
                  activeTab === "strategy" ? "text-white border-b border-white" : "text-zinc-500 hover:text-zinc-300"
                }`}
              >
                1. CAMPAIGN STRATEGY
              </button>
              <button
                onClick={() => setActiveTab("copy")}
                className={`py-3 font-semibold transition ${
                  activeTab === "copy" ? "text-white border-b border-white" : "text-zinc-500 hover:text-zinc-300"
                }`}
              >
                2. COPYWRITING ASSETS
              </button>
              <button
                onClick={() => setActiveTab("seo")}
                className={`py-3 font-semibold transition ${
                  activeTab === "seo" ? "text-white border-b border-white" : "text-zinc-500 hover:text-zinc-300"
                }`}
              >
                3. SEO AUDIT
              </button>
              <button
                onClick={() => setActiveTab("qa")}
                className={`py-3 font-semibold transition ${
                  activeTab === "qa" ? "text-white border-b border-white" : "text-zinc-500 hover:text-zinc-300"
                }`}
              >
                4. SOCIAL Q&A PLAYGROUND
              </button>
            </div>

            {/* Content Body */}
            <div className="p-6 flex-1 bg-[#0b0b0d]">
              <AnimatePresence mode="wait">
                
                {/* Campaign Data Tabs */}
                {activeTab !== "qa" && (
                  <motion.div
                    key={activeTab}
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -4 }}
                    className="relative h-full"
                  >
                    {!campaign ? (
                      <div className="h-[250px] flex flex-col justify-center items-center text-zinc-500 text-sm italic">
                        <span>No content generated. Start the agents to compile files.</span>
                      </div>
                    ) : (
                      <div className="relative">
                        <button
                          onClick={() => {
                            const textToCopy = 
                              activeTab === "strategy" ? campaign.strategy :
                              activeTab === "copy" ? campaign.copy : campaign.seo;
                            navigator.clipboard.writeText(textToCopy);
                            alert("Copied to clipboard!");
                          }}
                          className="absolute right-0 top-0 text-[10px] bg-zinc-800 text-zinc-300 px-2.5 py-1 rounded hover:bg-zinc-700 transition"
                        >
                          Copy Text
                        </button>
                        <pre className="text-sm font-mono text-zinc-300 whitespace-pre-wrap leading-relaxed pt-8 overflow-y-auto max-h-[350px]">
                          {activeTab === "strategy" && campaign.strategy}
                          {activeTab === "copy" && campaign.copy}
                          {activeTab === "seo" && campaign.seo}
                        </pre>
                      </div>
                    )}
                  </motion.div>
                )}

                {/* Social Q&A Tab */}
                {activeTab === "qa" && (
                  <motion.div
                    key="qa"
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -4 }}
                    className="space-y-4"
                  >
                    <div>
                      <h3 className="text-xs font-mono text-zinc-400 mb-2">SIMULATE COMMUNITY QUESTION</h3>
                      <form onSubmit={handleAskQuestion} className="flex gap-2">
                        <input
                          type="text"
                          value={qaQuestion}
                          onChange={(e) => setQaQuestion(e.target.value)}
                          className="flex-1 bg-[#121215] border border-zinc-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-zinc-500 transition"
                          placeholder="Ask a critical technical question about the repo..."
                        />
                        <button
                          type="submit"
                          disabled={qaLoading}
                          className="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 active:bg-zinc-600 text-sm font-medium text-white transition disabled:opacity-50"
                        >
                          {qaLoading ? "Thinking..." : "Test Agent Response"}
                        </button>
                      </form>
                    </div>

                    <div className="bg-[#121215] border border-zinc-800 rounded-xl p-5 min-h-[160px] flex flex-col justify-between">
                      <div>
                        <div className="text-[10px] font-mono text-zinc-500 mb-2">SOCIAL RESPONDER AGENT OUTLET</div>
                        {qaLoading ? (
                          <div className="flex space-x-1.5 items-center text-zinc-500 text-sm italic">
                            <span className="animate-bounce">●</span>
                            <span className="animate-bounce [animation-delay:0.2s]">●</span>
                            <span className="animate-bounce [animation-delay:0.4s]">●</span>
                            <span className="ml-1 text-xs">Formulating response...</span>
                          </div>
                        ) : qaAnswer ? (
                          <p className="text-sm text-zinc-300 leading-relaxed font-mono whitespace-pre-wrap">{qaAnswer}</p>
                        ) : (
                          <div className="text-zinc-600 italic text-sm">Ask a question above to test the agent response.</div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                )}

              </AnimatePresence>
            </div>
          </section>

        </div>

      </main>
    </div>
  );
}
