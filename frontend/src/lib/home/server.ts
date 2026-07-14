import { cookies } from "next/headers";

import { apiOrigin } from "@/lib/api/config";
import type {
  CurrentLendingListItem,
  CurrentReservationListItem,
  HomeTabData,
  HomeTabFetchResult,
  LendingHistoryListItem,
} from "./types";

async function fetchHomeList<T>(
  path: string,
  cookieHeader: string,
): Promise<HomeTabFetchResult<T>> {
  try {
    const response = await fetch(`${apiOrigin}${path}`, {
      headers: {
        cookie: cookieHeader,
      },
      cache: "no-store",
    });

    if (response.status < 200 || response.status >= 300) {
      return { ok: false };
    }

    return {
      ok: true,
      data: (await response.json()) as T,
    };
  } catch {
    return { ok: false };
  }
}

export async function fetchHomeTabData(): Promise<HomeTabData> {
  const cookieHeader = (await cookies()).toString();
  const [currentLendings, currentReservations, lendingHistory] = await Promise.all([
    fetchHomeList<CurrentLendingListItem[]>("/api/me/lendings/current/", cookieHeader),
    fetchHomeList<CurrentReservationListItem[]>("/api/me/reservations/current/", cookieHeader),
    fetchHomeList<LendingHistoryListItem[]>("/api/me/lendings/history/", cookieHeader),
  ]);

  return {
    currentLendings,
    currentReservations,
    lendingHistory,
  };
}
