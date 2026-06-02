"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ApiValidationError, type ApiValidationErrors } from "@/lib/auth/types";
import { login } from "@/lib/auth/client";

function fieldError(errors: ApiValidationErrors, field: string) {
  return errors[field]?.[0];
}

export function LoginForm() {
  const router = useRouter();
  const [errors, setErrors] = useState<ApiValidationErrors>({});
  const [formError, setFormError] = useState<string>();
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    const employeeId = String(formData.get("employee_id") ?? "");
    const password = String(formData.get("password") ?? "");

    setErrors({});
    setFormError(undefined);
    setIsSubmitting(true);

    try {
      await login(employeeId, password);
      router.replace("/home");
      router.refresh();
    } catch (error) {
      if (error instanceof ApiValidationError) {
        setErrors(error.errors);
        return;
      }

      setFormError(error instanceof Error ? error.message : "ログインに失敗しました");
    } finally {
      setIsSubmitting(false);
    }
  }

  const employeeIdError = fieldError(errors, "employee_id");
  const passwordError = fieldError(errors, "password");
  const nonFieldErrors = errors.non_field_errors ?? [];

  return (
    <Card className="w-full max-w-sm">
      <CardHeader>
        <CardTitle>ログイン</CardTitle>
        <CardDescription>社員番号とパスワードを入力してください。</CardDescription>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <label htmlFor="employee_id" className="text-sm font-medium">
              社員番号
            </label>
            <Input
              id="employee_id"
              name="employee_id"
              type="text"
              inputMode="numeric"
              autoComplete="username"
              aria-invalid={employeeIdError ? true : undefined}
            />
            {employeeIdError ? (
              <p className="text-sm text-destructive" role="alert">
                {employeeIdError}
              </p>
            ) : null}
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="text-sm font-medium">
              パスワード
            </label>
            <Input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              aria-invalid={passwordError ? true : undefined}
            />
            {passwordError ? (
              <p className="text-sm text-destructive" role="alert">
                {passwordError}
              </p>
            ) : null}
          </div>

          {nonFieldErrors.length > 0 ? (
            <div className="space-y-1 text-sm text-destructive" role="alert">
              {nonFieldErrors.map((message) => (
                <p key={message}>{message}</p>
              ))}
            </div>
          ) : null}

          {formError ? (
            <p className="text-sm text-destructive" role="alert">
              {formError}
            </p>
          ) : null}

          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? "ログイン中..." : "ログイン"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
