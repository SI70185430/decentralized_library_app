import {
  ApiValidationError,
  type ApiValidationErrors,
  type AuthUser,
  type AuthUserResponse,
} from "./types";

// CSRFトークン用cookieの値を取得
function getCsrfCookie() {
  return document.cookie
    .split("; ")
    .find((cookie) => cookie.startsWith("csrftoken="))
    ?.slice("csrftoken=".length);
}

function isValidationErrors(data: unknown): data is ApiValidationErrors {
  if (!data || typeof data !== "object" || Array.isArray(data)) {
    return false;
  }

  return Object.values(data).every(
    (value) =>
      Array.isArray(value) && value.every((item) => typeof item === "string"),
  );
}

async function requestCsrfToken() {
  const response = await fetch("/api/auth/csrf/");

  if (!response.ok) {
    throw new Error("CSRFトークンの取得に失敗しました");
  }
}

async function getCsrfToken() {
  let token = getCsrfCookie();

  if (!token) {
    await requestCsrfToken();
    token = getCsrfCookie();
  }

  if (!token) {
    throw new Error("CSRFトークンが見つかりません");
  }

  return token;
}

async function readJson(response: Response): Promise<unknown> {
  return response.json().catch(() => null);
}

export async function login(
  employeeId: string,
  password: string,
): Promise<AuthUserResponse> {
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
    const data = await readJson(response);

    if (isValidationErrors(data)) {
      throw new ApiValidationError(data);
    }

    throw new Error("ログインに失敗しました");
  }

  return (await response.json()) as AuthUserResponse;
}

export async function logout() {
  const csrfToken = await getCsrfToken();
  const response = await fetch("/api/auth/logout/", {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken,
    },
  });

  if (!response.ok) {
    throw new Error("ログアウトに失敗しました");
  }
}

export async function getCurrentUser(): Promise<AuthUser | null> {
  const response = await fetch("/api/auth/me/");

  if (response.status === 401 || response.status === 403) {
    return null;
  }

  if (!response.ok) {
    throw new Error("ユーザー情報の取得に失敗しました");
  }

  const data = (await response.json()) as AuthUserResponse;
  return data.user;
}
