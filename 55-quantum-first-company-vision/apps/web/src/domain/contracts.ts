export interface Source {
  id: string;
  title: string;
  publisher: string;
  url: string;
  accessed_on: string;
  scope: string;
}
export interface Evidence {
  id: string;
  source_id: string;
  paraphrase: string;
  stance: string;
  locator: string;
  confidence: string;
  limitations: string;
}
export interface Claim {
  id: string;
  text: string;
  kind: string;
  confidence: string;
  source_ids: string[];
  supporting_evidence: string[];
  opposing_evidence: string[];
  review_on: string;
}
export interface Entity {
  id: string;
  entity_type: string;
  title: string;
  description: string;
  status: string;
  claim_ids: string[];
  related_ids: string[];
  details: Record<string, unknown>;
}
export interface Opportunity {
  id: string;
  name: string;
  promise: string;
  classical_alternative: string;
  maturity_condition: string;
  kill_gate: string;
  primary_icp: string;
  secondary_icp: string;
  claim_ids: string[];
  opposing_claim_ids: string[];
  dimensions: Record<string, { low: number; high: number } | null>;
  rationale: Record<string, string>;
}
export interface Score {
  id: string;
  name: string;
  scenario: string;
  low: number;
  high: number;
  estimate: number;
  known_weight_fraction: number;
  unknown_dimensions: string[];
}
export interface EconomicResult {
  tam: number;
  sam: number;
  som: number;
  gross_margin: number;
  delivery_cost_per_customer: number;
  formulas: Record<string, string>;
  exclusions: string;
  classification: string;
}
export interface Room {
  corpus: {
    research_date: string;
    sources: Source[];
    evidence: Evidence[];
    claims: Claim[];
    entities: Entity[];
    opportunities: Opportunity[];
    approval: string;
  };
  protocol: {
    version: string;
    dimensions: {
      id: string;
      label: string;
      direction: string;
      weight: number;
    }[];
    unknown_rule: string;
  };
  audit: {
    status: string;
    sources: number;
    evidence: number;
    claims: number;
    overdue_claims: string[];
  };
  scores: Record<string, Score[]>;
  sensitivity: {
    reference_winner: string;
    intervals_overlap: boolean;
    rank_flips: string[];
    one_at_a_time_cases: number;
    stress_cases: {
      id: string;
      title: string;
      winner: string;
      scores: Score[];
    }[];
  };
  economics: Record<string, EconomicResult>;
  decision: Entity;
}
