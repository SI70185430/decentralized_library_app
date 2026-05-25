export default function TestLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <main className="mx-auto w-full max-w-7xl px-4 py-4">{children}</main>
    </div>
  );
}
