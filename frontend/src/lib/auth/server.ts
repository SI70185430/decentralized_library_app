import { cookies } from "next/headers";

import { apiErrorFromResponse, apiErrorFromUnknown } from "@/lib/api/errors";
import { apiOrigin } from "@/lib/api/config";
import type { AuthUser, AuthUserResponse } from "./types";

export async function getCurrentUser(): Promise<AuthUser | null> {
  const cookieStore = await cookies();

  try {
    const response = await fetch(`${apiOrigin}/api/auth/me/`, {
      // Next.jsからDjangoへのrequestではcookieは自動的に付与はされない
      // そのため、明示的にcookie headerを付与している
      headers: {
        cookie: cookieStore.toString(),
      },
      cache: "no-store",
    });

    if (response.status === 401 || response.status === 403) {
      return null;
    }

    if (!response.ok) {
      throw await apiErrorFromResponse(response);
    }

    const data = (await response.json()) as AuthUserResponse;
    return data.user;
  } catch (error) {
    throw apiErrorFromUnknown(error);
  }
}
