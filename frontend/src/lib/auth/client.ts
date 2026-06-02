import {
  ApiValidationError,
  type ApiValidationErrors,
  type AuthUser,
  type AuthUserResponse,
} from "./types";

// 指定した名前のcookieの値を取得
function getCookie(name: string) {
  const value = document.cookie
    .split("; ")
    .find((cookie) => cookie.startsWith(`${name}=`))
    ?.slice(name.length + 1);

  return value ? decodeURIComponent(value) : undefined;
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
  const response = await fetch("/api/auth/csrf/", {
    credentials: "same-origin",
  });

  if (!response.ok) {
    throw new Error("CSRFトークンの取得に失敗しました");
  }
}

async function getCsrfToken() {
  let token = getCookie("csrftoken");

  if (!token) {
    await requestCsrfToken();
    token = getCookie("csrftoken");
  }

  if (!token) {
    throw new Error("CSRFトークンが見つかりません");
  }

  return token;
}

async function readJson(response: Response): Promise<unknown> {
  return response.json().catch(() => null);
}

function getDetailMessage(data: unknown) {
  if (
    data &&
    typeof data === "object" &&
    "detail" in data &&
    typeof data.detail === "string"
  ) {
    return data.detail;
  }
}

export async function login(employeeId: string | number, password: string) {
  const csrfToken = await getCsrfToken();
  const response = await fetch("/api/auth/login/", {
    method: "POST",
    credentials: "same-origin",
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

    const detailMessage = getDetailMessage(data);

    if (detailMessage) {
      throw new Error(detailMessage);
    }

    throw new Error("ログインに失敗しました");
  }

  return (await response.json()) as AuthUserResponse;
}

export async function logout() {
  const csrfToken = await getCsrfToken();
  const response = await fetch("/api/auth/logout/", {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify({}),
  });

  if (!response.ok) {
    const data = await readJson(response);
    const detailMessage = getDetailMessage(data);

    if (detailMessage) {
      throw new Error(detailMessage);
    }

    throw new Error("ログアウトに失敗しました");
  }
}

export async function getCurrentUser(): Promise<AuthUser | null> {
  const response = await fetch("/api/auth/me/", {
    credentials: "same-origin",
  });

  if (response.status === 401 || response.status === 403) {
    return null;
  }

  if (!response.ok) {
    const data = await readJson(response);
    const detailMessage = getDetailMessage(data);

    if (detailMessage) {
      throw new Error(detailMessage);
    }

    throw new Error("ユーザー情報の取得に失敗しました");
  }

  const data = (await response.json()) as AuthUserResponse;
  return data.user;
}
