import { redirect } from "next/navigation";

import { getCurrentUser } from "@/lib/auth/server";

export default async function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const user = await getCurrentUser();

  if (!user) {
    redirect("/login");
  }

  return (
    <div className="min-h-screen bg-background">
      <main className="mx-auto w-full max-w-7xl px-4 py-4">{children}</main>
    </div>
  );
}
