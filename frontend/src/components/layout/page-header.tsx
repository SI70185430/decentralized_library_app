import { BackButton } from "@/components/layout/back-button";
import { MobileMenu } from "@/components/layout/mobile-menu";

type PageHeaderProps = {
  title: string;
  backHref: string;
};

export function PageHeader({ title, backHref }: PageHeaderProps) {
  return (
    <header className="border-b bg-background">
      <div className="flex h-14 items-center gap-3 px-4">
        <BackButton href={backHref} />

        <h1 className="min-w-0 flex-1 truncate text-lg font-semibold">{title}</h1>

        <MobileMenu />
      </div>
    </header>
  );
}
