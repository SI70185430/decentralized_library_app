import { cookies } from "next/headers";

import { apiOrigin } from "@/lib/api/config";
import type { LendingReturnPreviewResponse } from "@/lib/lending/types";

const LENDING_RETURN_PREVIEW_SERVER_FETCH_ERROR_MESSAGE = "貸出情報の取得に失敗しました。";

export async function fetchLendingReturnPreviewForServer(
  lendingId: string,
): Promise<LendingReturnPreviewResponse | null> {
  const cookieStore = await cookies();

  try {
    const response = await fetch(`${apiOrigin}/api/lendings/${lendingId}/return/`, {
      headers: {
        cookie: cookieStore.toString(),
      },
      cache: "no-store",
    });

    if (response.status === 404) {
      return null;
    }

    if (response.status !== 200) {
      throw new Error(LENDING_RETURN_PREVIEW_SERVER_FETCH_ERROR_MESSAGE);
    }

    return (await response.json()) as LendingReturnPreviewResponse;
  } catch {
    throw new Error(LENDING_RETURN_PREVIEW_SERVER_FETCH_ERROR_MESSAGE);
  }
}
