import { ControlTower, type RoadmapData } from "./control-tower";

const fallback: RoadmapData = {
  revision: "quantum-first-roadmap-v1-candidate",
  approval_status: "technical_candidate_unapproved",
  as_of: "2026-09-24",
  initiatives: [],
  capability_graph: { nodes: 12, edges: 10, critical_path: ["cap-03", "cap-04", "cap-05"] },
};

async function loadRoadmap(): Promise<RoadmapData> {
  const base = process.env.STRATEGY_API_URL || "http://127.0.0.1:8060";
  try {
    const response = await fetch(`${base}/v1/roadmap`, { cache: "no-store" });
    if (!response.ok) return fallback;
    return await response.json() as RoadmapData;
  } catch {
    return fallback;
  }
}

export default async function Home() {
  return <ControlTower data={await loadRoadmap()} />;
}

