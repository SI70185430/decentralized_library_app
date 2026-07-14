export function normalizeBackendOrigin(origin: string): string {
  return origin.replace(/\/$/, "");
}
