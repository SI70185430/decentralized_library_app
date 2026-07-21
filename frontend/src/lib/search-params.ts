export function getSingleSearchParam(
  value: string | string[] | undefined,
): string | null {
  if (!value || Array.isArray(value)) {
    return null;
  }

  const trimmedValue = value.trim();
  return trimmedValue || null;
}
