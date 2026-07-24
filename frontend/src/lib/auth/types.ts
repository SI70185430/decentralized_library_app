// frontendで扱うログインユーザーの型
export type AuthUser = {
  id: string;
  employee_id: number;
  username: string;
};

// login/me/等で使用する正常 response の型
export type AuthUserResponse = {
  user: AuthUser;
};

// ブラウザ上のログインフォームだけが扱う表示文言の型。
// Backend の validation code 型とは分離する。
export type LoginFormErrors = Record<string, string[]>;
