export type AuthUser = {
  id: string;
  employee_id: number;
  username: string;
};

export type AuthUserResponse = {
  user: AuthUser;
};

export type ApiValidationErrors = Record<string, string[]>;

export class ApiValidationError extends Error {
  errors: ApiValidationErrors;

  constructor(errors: ApiValidationErrors) {
    super("入力内容を確認してください");
    this.name = "ApiValidationError";
    this.errors = errors;
  }
}
