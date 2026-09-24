import type { EconomicResult, Room, Score } from "../domain/contracts";
async function read<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`/api/${path}`, { signal });
  if (!response.ok)
    throw new Error(
      `Evidence API unavailable (${response.status}). Check the local API and retry.`,
    );
  return response.json() as Promise<T>;
}
export const evidenceApi = {
  room: (signal?: AbortSignal) => read<Room>("room", signal),
  score: (scenario: string, dimension: string, multiplier: number) =>
    read<{ scores: Score[] }>(
      `score?${new URLSearchParams({ scenario, dimension, multiplier: String(multiplier) })}`,
    ),
  economics: (annualPrice: number) =>
    read<EconomicResult>(`economics?annual_price=${annualPrice}`),
};
