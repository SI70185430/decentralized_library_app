import { getCsrfToken } from "@/lib/api/csrf";
import { apiErrorFromResponse, apiErrorFromUnknown } from "@/lib/api/errors";
import type { AuthUser, AuthUserResponse } from "./types";

export async function login(
  employeeId: string,
  password: string,
): Promise<AuthUserResponse> {
  try {
    const csrfToken = await getCsrfToken();
    const response = await fetch("/api/auth/login/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({ employee_id: employeeId, password }),
    });

    if (!response.ok) {
      throw await apiErrorFromResponse(response);
    }

    return (await response.json()) as AuthUserResponse;
  } catch (error) {
    throw apiErrorFromUnknown(error);
  }
}

export async function logout() {
  try {
    const csrfToken = await getCsrfToken();
    const response = await fetch("/api/auth/logout/", {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken,
      },
    });

    if (!response.ok) {
      throw await apiErrorFromResponse(response);
    }
  } catch (error) {
    throw apiErrorFromUnknown(error);
  }
}

export async function getCurrentUser(): Promise<AuthUser | null> {
  try {
    const response = await fetch("/api/auth/me/");

    if (response.status === 401 || response.status === 403) {
      return null;
    }

    if (!response.ok) {
      throw await apiErrorFromResponse(response);
    }

    return ((await response.json()) as AuthUserResponse).user;
  } catch (error) {
    throw apiErrorFromUnknown(error);
  }
}
