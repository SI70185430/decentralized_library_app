import { cookies } from "next/headers";

import type { AuthUser, AuthUserResponse } from "./types";

const apiOrigin = "http://127.0.0.1:8000";

export async function getCurrentUser(): Promise<AuthUser | null> {
  const cookieStore = await cookies();
  const response = await fetch(`${apiOrigin}/api/auth/me/`, {
    headers: {
      cookie: cookieStore.toString(),
    },
    cache: "no-store",
  });

  if (response.status === 401 || response.status === 403) {
    return null;
  }

  if (!response.ok) {
    throw new Error("ログイン状態の確認に失敗しました");
  }

  const data = (await response.json()) as AuthUserResponse;
  return data.user;
}
