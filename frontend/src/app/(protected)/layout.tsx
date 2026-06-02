import { redirect } from "next/navigation";

import { getCurrentUser } from "@/lib/auth/server";

export default async function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const user = await getCurrentUser();

  if (!user) {
    redirect("/login");
  }

  return (
    <div className="min-h-dvh bg-white">
      <main className="mx-auto min-h-dvh w-full max-w-[402px] bg-white">{children}</main>
    </div>
  );
}
