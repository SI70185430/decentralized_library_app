"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiError, GENERIC_API_ERROR_MESSAGE, messageForFieldError } from "@/lib/api/errors";
import { login } from "@/lib/auth/client";
import type { LoginFormErrors } from "@/lib/auth/types";

function fieldError(errors: LoginFormErrors, field: string) {
  return errors[field]?.[0];
}

// 社員番号の入力にて空白を削除して全角数字を半角数字に変換
function normalizeEmployeeId(value: string) {
  return value
    .trim()
    .replace(/[０-９]/g, (char) => String.fromCharCode(char.charCodeAt(0) - 0xfee0));
}

function validateLoginForm(employeeId: string, password: string): LoginFormErrors {
  const errors: LoginFormErrors = {};
  const normalizedEmployeeId = normalizeEmployeeId(employeeId);

  if (!normalizedEmployeeId) {
    errors.employee_id = ["社員番号は必須です"];
  } else if (!/^\d+$/.test(normalizedEmployeeId)) {
    errors.employee_id = ["社員番号は数字のみで入力してください"];
  }

  if (!password) {
    errors.password = ["パスワードは必須です"];
  }

  return errors;
}

function toLoginFormErrors(error: ApiError): LoginFormErrors {
  return Object.fromEntries(
    Object.entries(error.fieldErrors).map(([field, codes]) => [
      field,
      codes.map((code) => messageForFieldError(field, code)),
    ]),
  );
}

export function LoginForm() {
  const router = useRouter();
  const [errors, setErrors] = useState<LoginFormErrors>({});
  const [submitError, setSubmitError] = useState<string>();
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: React.SubmitEvent<HTMLFormElement>) {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    const employeeId = String(formData.get("employee_id") ?? "");
    const password = String(formData.get("password") ?? "");

    // 再送信時に前回のエラー表示を削除
    setErrors({});
    setSubmitError(undefined);

    const validationErrors = validateLoginForm(employeeId, password);

    if (Object.keys(validationErrors).length) {
      setErrors(validationErrors);
      return;
    }

    setIsSubmitting(true);

    try {
      await login(normalizeEmployeeId(employeeId), password);
      router.replace("/home");
    } catch (error) {
      if (error instanceof ApiError && error.code === "VALIDATION_ERROR") {
        setErrors(toLoginFormErrors(error));
        return;
      }

      setSubmitError(error instanceof ApiError ? error.message : GENERIC_API_ERROR_MESSAGE);
    } finally {
      setIsSubmitting(false);
    }
  }

  const employeeIdError = fieldError(errors, "employee_id");
  const passwordError = fieldError(errors, "password");
  const nonFieldErrors = errors.non_field_errors ?? [];

  return (
    <div className="mx-auto min-h-dvh w-full max-w-[402px] bg-white px-[clamp(40px,14.9vw,60px)] pt-[clamp(56px,12dvh,88px)] pb-12 text-[#222]">
      <h1 className="text-center whitespace-nowrap text-[28px] leading-none font-bold tracking-[-0.04em]">
        分散型図書館アプリ
      </h1>

      <form className="mt-[clamp(72px,12dvh,104px)]" onSubmit={handleSubmit}>
        <div>
          <label htmlFor="employee_id" className="text-2xl leading-none font-semibold">
            社員番号
          </label>
          <Input
            id="employee_id"
            name="employee_id"
            type="text"
            inputMode="numeric"
            autoComplete="username"
            className="mt-3 h-11 rounded-none border border-black bg-[#e9e9e9] text-base shadow-none focus-visible:border-black focus-visible:ring-0"
            aria-invalid={employeeIdError ? true : undefined}
          />
          {employeeIdError ? (
            <p className="mt-2 text-sm text-destructive" role="alert">
              {employeeIdError}
            </p>
          ) : null}
        </div>

        <div className="mt-[clamp(40px,7dvh,64px)]">
          <label htmlFor="password" className="text-2xl leading-none font-semibold">
            パスワード
          </label>
          <Input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            className="mt-3 h-11 rounded-none border border-black bg-[#e9e9e9] text-base shadow-none focus-visible:border-black focus-visible:ring-0"
            aria-invalid={passwordError ? true : undefined}
          />
          {passwordError ? (
            <p className="mt-2 text-sm text-destructive" role="alert">
              {passwordError}
            </p>
          ) : null}
        </div>

        {nonFieldErrors.length ? (
          <div className="mt-6 space-y-1 text-sm text-destructive" role="alert">
            {nonFieldErrors.map((message) => (
              <p key={message}>{message}</p>
            ))}
          </div>
        ) : null}

        {submitError ? (
          <p className="mt-6 text-sm text-destructive" role="alert">
            {submitError}
          </p>
        ) : null}

        <div className="mt-[clamp(56px,9dvh,83px)] flex justify-center">
          <Button
            type="submit"
            className="h-[43px] w-44 rounded-[8px] border border-black bg-[#eef0ff] text-xl font-normal text-black shadow-none"
            disabled={isSubmitting}
          >
            {isSubmitting ? "ログイン中..." : "ログイン"}
          </Button>
        </div>
      </form>
    </div>
  );
}
