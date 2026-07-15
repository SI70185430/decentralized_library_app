import { cookies } from "next/headers";

import { apiOrigin } from "@/lib/api/config";
import type { LendingDetailResponse } from "@/lib/lending/types";

const LENDING_DETAIL_SERVER_FETCH_ERROR_MESSAGE = "貸出情報の取得に失敗しました。";

export async function fetchLendingDetailForServer(
  lendingId: string,
): Promise<LendingDetailResponse | null> {
  const cookieStore = await cookies();

  try {
    const response = await fetch(`${apiOrigin}/api/lendings/${lendingId}/`, {
      headers: {
        cookie: cookieStore.toString(),
      },
      cache: "no-store",
    });

    if (response.status === 404) {
      return null;
    }

    if (response.status !== 200) {
      throw new Error(LENDING_DETAIL_SERVER_FETCH_ERROR_MESSAGE);
    }

    return (await response.json()) as LendingDetailResponse;
  } catch {
    throw new Error(LENDING_DETAIL_SERVER_FETCH_ERROR_MESSAGE);
  }
}
