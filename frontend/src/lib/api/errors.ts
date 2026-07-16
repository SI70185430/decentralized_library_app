export const GENERIC_API_ERROR_MESSAGE =
  "処理に失敗しました。時間をおいて再度お試しください。";

export const API_ERROR_CODES = [
  "INVALID_CREDENTIALS",
  "ISBN_INVALID",
  "GENRE_NOT_FOUND",
  "RESERVATION_DATE_MUST_BE_FUTURE",
  "BOOK_NOT_FOUND",
  "LENDING_NOT_FOUND",
  "RESERVATION_NOT_FOUND",
  "BORROWING_LIMIT_REACHED",
  "ALREADY_BORROWING_BOOK",
  "ALREADY_RESERVING_BOOK",
  "NO_AVAILABLE_BOOK_COPY",
  "BOOK_COPY_ALREADY_RESERVED",
  "LENDING_EXTENSION_LIMIT_REACHED",
  "LENDING_ALREADY_RETURNED",
  "BOOK_COPY_NOT_ON_LOAN",
  "RESERVATION_NOT_STARTED",
  "RESERVATION_EXPIRED",
  "BOOK_COPY_NOT_RESERVED",
  "LENDING_STATE_CONFLICT",
  "REQUIRED",
  "BLANK",
  "INVALID",
  "AUTHENTICATION_REQUIRED",
  "FORBIDDEN",
  "NOT_FOUND",
  "VALIDATION_ERROR",
] as const;

export type ApiErrorCode = (typeof API_ERROR_CODES)[number];
export type ApiFieldErrors = Record<string, string[]>;

export type ApiValidationErrorResponse = {
  code: "VALIDATION_ERROR";
  field_errors: ApiFieldErrors;
};

export type ApiNonValidationErrorResponse = {
  code: string;
  field_errors?: never;
};

export type ApiErrorResponse =
  | ApiValidationErrorResponse
  | ApiNonValidationErrorResponse;

const API_ERROR_MESSAGES: Record<ApiErrorCode, string> = {
  INVALID_CREDENTIALS: "社員番号またはパスワードを確認してください。",
  ISBN_INVALID: "ISBNコードを確認してください。",
  GENRE_NOT_FOUND: "指定したジャンルを確認してください。",
  RESERVATION_DATE_MUST_BE_FUTURE: "予約日は明日以降の日付を指定してください。",
  BOOK_NOT_FOUND: "書籍が見つかりません。",
  LENDING_NOT_FOUND: "貸出情報が見つかりません。",
  RESERVATION_NOT_FOUND: "予約情報が見つかりません。",
  BORROWING_LIMIT_REACHED: "貸出・予約できる冊数の上限に達しています。",
  ALREADY_BORROWING_BOOK: "この書籍はすでに貸出中です。",
  ALREADY_RESERVING_BOOK: "この書籍はすでに予約中です。",
  NO_AVAILABLE_BOOK_COPY: "現在、貸出可能な蔵書がありません。",
  BOOK_COPY_ALREADY_RESERVED: "ほかの操作と重なりました。時間をおいて再度お試しください。",
  LENDING_EXTENSION_LIMIT_REACHED: "貸出延長回数の上限に達しています。",
  LENDING_ALREADY_RETURNED: "この貸出はすでに返却されています。",
  BOOK_COPY_NOT_ON_LOAN: "貸出状態を確認できませんでした。",
  RESERVATION_NOT_STARTED: "予約開始日以降に貸出へ変換してください。",
  RESERVATION_EXPIRED: "予約の取り置き期限が過ぎています。",
  BOOK_COPY_NOT_RESERVED: "予約状態を確認できませんでした。",
  LENDING_STATE_CONFLICT: "ほかの操作と状態が競合しました。再度お試しください。",
  REQUIRED: "入力が必要です。",
  BLANK: "入力が必要です。",
  INVALID: "入力内容を確認してください。",
  AUTHENTICATION_REQUIRED: "ログインが必要です。",
  FORBIDDEN: "この操作を実行する権限がありません。",
  NOT_FOUND: "対象が見つかりません。",
  VALIDATION_ERROR: "入力内容を確認してください。",
};

const FIELD_ERROR_MESSAGES: Record<
  string,
  Partial<Record<ApiErrorCode, string>>
> = {
  employee_id: {
    REQUIRED: "社員番号を入力してください。",
    BLANK: "社員番号を入力してください。",
    INVALID: "社員番号は数字で入力してください。",
    INVALID_CREDENTIALS: "社員番号またはパスワードを確認してください。",
  },
  password: {
    REQUIRED: "パスワードを入力してください。",
    BLANK: "パスワードを入力してください。",
    INVALID: "パスワードを確認してください。",
    INVALID_CREDENTIALS: "社員番号またはパスワードを確認してください。",
  },
  isbn: {
    REQUIRED: "ISBNコードを入力してください。",
    BLANK: "ISBNコードを入力してください。",
    INVALID: "ISBNコードを確認してください。",
    ISBN_INVALID: "ISBNコードを確認してください。",
  },
  genre: {
    REQUIRED: "ジャンルを選択してください。",
    BLANK: "ジャンルを選択してください。",
    INVALID: "ジャンルを確認してください。",
    GENRE_NOT_FOUND: "指定したジャンルを確認してください。",
  },
  book_id: {
    REQUIRED: "書籍を指定してください。",
    BLANK: "書籍を指定してください。",
    INVALID: "書籍の指定を確認してください。",
  },
  scheduled_date: {
    REQUIRED: "予約日を指定してください。",
    BLANK: "予約日を指定してください。",
    INVALID: "予約日の指定を確認してください。",
    RESERVATION_DATE_MUST_BE_FUTURE: "予約日は明日以降の日付を指定してください。",
  },
  non_field_errors: {
    INVALID_CREDENTIALS: "社員番号またはパスワードを確認してください。",
    INVALID: "入力内容を確認してください。",
  },
};

const API_ERROR_CODE_SET = new Set<string>(API_ERROR_CODES);

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function hasOwn(value: Record<string, unknown>, key: string): boolean {
  return Object.prototype.hasOwnProperty.call(value, key);
}

function isFieldErrors(value: unknown): value is ApiFieldErrors {
  return (
    isRecord(value) &&
    Object.values(value).every(
      (codes) =>
        Array.isArray(codes) && codes.every((code) => typeof code === "string"),
    )
  );
}

export function isApiErrorResponse(value: unknown): value is ApiErrorResponse {
  if (!isRecord(value) || typeof value.code !== "string" || hasOwn(value, "detail")) {
    return false;
  }

  if (value.code === "VALIDATION_ERROR") {
    return isFieldErrors(value.field_errors);
  }

  return !hasOwn(value, "field_errors");
}

export function isKnownApiErrorCode(value: string): value is ApiErrorCode {
  return API_ERROR_CODE_SET.has(value);
}

export function messageForApiErrorCode(code: string | null): string {
  if (code !== null && isKnownApiErrorCode(code)) {
    return API_ERROR_MESSAGES[code];
  }

  return GENERIC_API_ERROR_MESSAGE;
}

export function messageForFieldError(field: string, code: string): string {
  if (isKnownApiErrorCode(code)) {
    return FIELD_ERROR_MESSAGES[field]?.[code] ?? API_ERROR_MESSAGES[code];
  }

  return GENERIC_API_ERROR_MESSAGE;
}

function messageForFieldErrors(fieldErrors: ApiFieldErrors): string {
  const messages = Object.entries(fieldErrors).flatMap(([field, codes]) =>
    codes.map((code) => messageForFieldError(field, code)),
  );

  return messages.length > 0
    ? messages.join("\n")
    : messageForApiErrorCode("VALIDATION_ERROR");
}

type ApiErrorOptions = {
  status: number | null;
  code?: string | null;
  fieldErrors?: ApiFieldErrors;
};

export class ApiError extends Error {
  readonly status: number | null;
  readonly code: string | null;
  readonly fieldErrors: ApiFieldErrors;

  constructor({ status, code = null, fieldErrors = {} }: ApiErrorOptions) {
    const message =
      status !== null && status >= 500
        ? GENERIC_API_ERROR_MESSAGE
        : code === "VALIDATION_ERROR"
          ? messageForFieldErrors(fieldErrors)
          : messageForApiErrorCode(code);

    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.fieldErrors = fieldErrors;
  }
}

export function genericApiError(status: number | null = null): ApiError {
  return new ApiError({ status });
}

export async function apiErrorFromResponse(response: Response): Promise<ApiError> {
  let data: unknown;

  try {
    data = await response.json();
  } catch {
    return genericApiError(response.status);
  }

  if (!isApiErrorResponse(data)) {
    return genericApiError(response.status);
  }

  if (data.code === "VALIDATION_ERROR") {
    return new ApiError({
      status: response.status,
      code: data.code,
      fieldErrors: data.field_errors,
    });
  }

  return new ApiError({ status: response.status, code: data.code });
}

export function apiErrorFromUnknown(error: unknown): ApiError {
  return error instanceof ApiError ? error : genericApiError();
}
