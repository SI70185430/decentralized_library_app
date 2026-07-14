import { normalizeBackendOrigin } from "./origin";

const backendOrigin = process.env.BACKEND_ORIGIN;

if (!backendOrigin) {
  throw new Error("BACKEND_ORIGIN が設定されていません。");
}

export const apiOrigin = normalizeBackendOrigin(backendOrigin);
