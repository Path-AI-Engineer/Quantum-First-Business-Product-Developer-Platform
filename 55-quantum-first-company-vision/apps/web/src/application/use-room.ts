"use client";
import { useCallback, useEffect, useState } from "react";
import type { Room, Score, EconomicResult } from "../domain/contracts";
import { evidenceApi } from "../infrastructure/evidence-api";
export function useRoom() {
  const [room, setRoom] = useState<Room | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [scores, setScores] = useState<Score[] | null>(null);
  const [economics, setEconomics] = useState<EconomicResult | null>(null);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    evidenceApi
      .room(controller.signal)
      .then(setRoom)
      .catch((reason) => {
        if (!controller.signal.aborted) setError(String(reason));
      });
    return () => controller.abort();
  }, [attempt]);
  const retry = useCallback(() => {
    setError("");
    setAttempt((a) => a + 1);
  }, []);
  const calculate = async (
    scenario: string,
    dimension: string,
    multiplier: number,
    price: number,
  ) => {
    setBusy(true);
    setError("");
    try {
      const [ranking, result] = await Promise.all([
        evidenceApi.score(scenario, dimension, multiplier),
        evidenceApi.economics(price),
      ]);
      setScores(ranking.scores);
      setEconomics(result);
    } catch (reason) {
      setError(String(reason));
    } finally {
      setBusy(false);
    }
  };
  return { room, error, busy, retry, calculate, scores, economics };
}
