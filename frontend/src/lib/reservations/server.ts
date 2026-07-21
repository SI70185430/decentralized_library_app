import { cookies } from "next/headers";

import { apiOrigin } from "@/lib/api/config";
import type { ReservationDetailResponse } from "@/lib/reservations/types";

const RESERVATION_DETAIL_SERVER_FETCH_ERROR_MESSAGE = "予約情報の取得に失敗しました。";

export async function fetchReservationDetailForServer(
  reservationId: string,
): Promise<ReservationDetailResponse | null> {
  const cookieStore = await cookies();

  let response: Response;

  try {
    response = await fetch(`${apiOrigin}/api/reservations/${reservationId}/`, {
      headers: {
        cookie: cookieStore.toString(),
      },
      cache: "no-store",
    });
  } catch {
    throw new Error(RESERVATION_DETAIL_SERVER_FETCH_ERROR_MESSAGE);
  }

  if (response.status === 404) {
    return null;
  }

  if (response.status !== 200) {
    throw new Error(RESERVATION_DETAIL_SERVER_FETCH_ERROR_MESSAGE);
  }

  try {
    return (await response.json()) as ReservationDetailResponse;
  } catch {
    throw new Error(RESERVATION_DETAIL_SERVER_FETCH_ERROR_MESSAGE);
  }
}
