// frontendで扱うログインユーザーの型
export type AuthUser = {
  id: string;
  employee_id: number;
  username: string;
};

// ログインユーザーを基にしたAPI responseの型
// login/me/等で使用
export type AuthUserResponse = {
  user: AuthUser;
};

// DRFでのvalidetion errorをfrontendで扱うための型
// DRFではerrorのvalueは一般的にstring[]型
export type ApiValidationErrors = Record<string, string[]>;

// APIのvalidetion error内容を保持するclass
export class ApiValidationError extends Error {
  readonly errors: ApiValidationErrors;

  constructor(errors: ApiValidationErrors) {
    super("入力内容を確認してください");
    this.name = "ApiValidationError";
    this.errors = errors;
  }
}
