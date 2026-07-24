import type { NextConfig } from "next";

import { normalizeBackendOrigin } from "./src/lib/api/origin";

const backendOrigin = process.env.BACKEND_ORIGIN;

if (!backendOrigin) {
  throw new Error("BACKEND_ORIGIN が設定されていません。");
}

const apiOrigin = normalizeBackendOrigin(backendOrigin);

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiOrigin}/api/:path*/`,
      },
    ];
  },
};

export default nextConfig;
