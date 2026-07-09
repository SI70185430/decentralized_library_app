// CSRFトークン用cookieの値を取得
export function getCsrfCookie() {
  return document.cookie
    .split("; ")
    .find((cookie) => cookie.startsWith("csrftoken="))
    ?.slice("csrftoken=".length);
}

export async function requestCsrfToken() {
  const response = await fetch("/api/auth/csrf/");

  if (!response.ok) {
    throw new Error("CSRFトークンの取得に失敗しました");
  }
}

export async function getCsrfToken() {
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
