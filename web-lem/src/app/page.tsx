"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";

// LEM-Dark Nivo theme: thin lines (1px), subtle area gradients (10% → 0%)
const lemNivoTheme = {
  axis: {
    domain: { line: { stroke: "#71717a", strokeWidth: 1 } },
    ticks: { text: { fill: "#a1a1aa", fontSize: 10 } },
  },
  grid: { line: { stroke: "#27272a", strokeWidth: 0.5 } },
  crosshair: { line: { stroke: "#ffffff", strokeWidth: 1 } },
};

const ResponsiveLine = dynamic(
  () => import("@nivo/line").then((m) => m.ResponsiveLine),
  { ssr: false, loading: () => <div className="h-[280px] bg-lem-obsidian animate-pulse" /> }
);

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface SummaryData {
  indicators: Record<string, { value: number; name: string; unit?: string }>;
}

export default function CommandCenter() {
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/api/v1/analytics/summary/USA`)
      .then((r) => r.json())
      .then(setSummary)
      .catch(() => setSummary(null))
      .finally(() => setLoading(false));
  }, []);

  // Sample chart data for GDP trend
  const gdpChartData = [
    {
      id: "GDP",
      data: [
        { x: "2020-Q1", y: 21561 },
        { x: "2020-Q2", y: 19520 },
        { x: "2020-Q3", y: 21100 },
        { x: "2020-Q4", y: 21433 },
        { x: "2021-Q1", y: 22037 },
        { x: "2021-Q2", y: 22901 },
        { x: "2021-Q3", y: 23137 },
        { x: "2021-Q4", y: 23992 },
        { x: "2022-Q1", y: 23889 },
        { x: "2022-Q2", y: 23679 },
        { x: "2022-Q3", y: 23950 },
        { x: "2022-Q4", y: 24283 },
        { x: "2023-Q1", y: 24542 },
        { x: "2023-Q2", y: 24729 },
        { x: "2023-Q3", y: 24939 },
        { x: "2023-Q4", y: 25126 },
      ],
    },
  ];

  return (
    <div className="min-h-screen bg-lem-obsidian text-lem-white">
      {/* Header - sharp, bold */}
      <header className="border-b border-lem-silver-muted bg-[#0c0c0e]/80 backdrop-blur-md px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-baseline space-x-3">
            <h1 className="font-sans text-xl font-bold tracking-tighter">
              LEM <span className="text-lem-silver font-normal">Large Economic Model</span>
            </h1>
            <span className="font-mono text-xs text-lem-silver">Command Center</span>
          </div>
          <nav className="flex space-x-6 text-sm font-medium">
            <Link href="/" className="text-white border-b-2 border-white pb-4 -mb-4 transition">
              Macro API Center
            </Link>
            <Link href="/marketing-team" className="text-zinc-400 hover:text-white transition">
              AI Marketing Team
            </Link>
          </nav>
        </div>
      </header>

      <main className="p-6">
        {/* KPI row - Geist Mono for data */}
        <motion.section
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
        >
          {loading ? (
            <div className="col-span-4 py-12 text-center text-lem-silver">Loading...</div>
          ) : (
            summary?.indicators &&
            Object.entries(summary.indicators as Record<string, { value: number; name: string; unit?: string }>)
              .slice(0, 4)
              .map(([key, ind], i) => (
                <motion.div
                  key={key}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: i * 0.1 }}
                  className="border border-lem-silver-muted bg-lem-obsidian p-4"
                >
                  <p className="font-sans text-xs text-lem-silver mb-1">{ind.name}</p>
                  <p className="font-mono text-2xl font-bold tracking-tight">
                    {typeof ind.value === "number" ? ind.value.toLocaleString() : ind.value}
                    {ind.unit ? <span className="text-lem-silver font-sans text-sm ml-1">{ind.unit}</span> : null}
                  </p>
                </motion.div>
              ))
          )}
        </motion.section>

        {/* Chart - Nivo monotone */}
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="border border-lem-silver-muted bg-lem-obsidian p-6 h-[360px]"
        >
          <h2 className="font-sans text-sm font-bold text-lem-silver mb-4">GDP (USA) — Real GDP Billions</h2>
          <div className="h-[280px]">
            <ResponsiveLine
              data={gdpChartData}
              margin={{ top: 12, right: 24, bottom: 48, left: 56 }}
              xScale={{ type: "point" }}
              yScale={{ type: "linear", min: "auto", max: "auto" }}
              lineWidth={1}
              pointSize={0}
              pointBorderWidth={0}
              areaOpacity={0.1}
              areaBlendMode="normal"
              colors={["#ffffff"]}
              theme={lemNivoTheme}
              enableGridX={false}
              enableGridY={true}
              axisBottom={{
                tickSize: 0,
                tickPadding: 8,
              }}
              axisLeft={{
                tickSize: 0,
                tickPadding: 8,
              }}
              enableArea
              defs={[
                {
                  id: "gradient",
                  type: "linearGradient",
                  colors: [
                    { offset: 0, color: "rgba(255,255,255,0.1)" },
                    { offset: 100, color: "rgba(255,255,255,0)" },
                  ],
                },
              ]}
              fill={[{ match: "*", id: "gradient" }]}
            />
          </div>
        </motion.section>

        {/* Footer */}
        <footer className="mt-8 border-t border-lem-silver-muted pt-4">
          <p className="font-mono text-xs text-lem-silver">
            LEM Engine · Obsidian #0A0A0A · Geist Mono · Geist Sans
          </p>
        </footer>
      </main>
    </div>
  );
}
