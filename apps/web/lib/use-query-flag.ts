"use client";

import { useSyncExternalStore } from "react";

const subscribe = () => () => undefined;

export function useQueryFlag(name: string) {
  return useSyncExternalStore(
    subscribe,
    () => new URLSearchParams(window.location.search).get(name) === "1",
    () => false,
  );
}
