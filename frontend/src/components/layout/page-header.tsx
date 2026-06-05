import { BackButton } from "@/components/layout/back-button";
import { MobileMenu } from "@/components/layout/mobile-menu";

type PageHeaderProps = {
  title: string;
  backHref?: string;
};

export function PageHeader({ title, backHref }: PageHeaderProps) {
  return (
    <header className="bg-[#95c8f3]">
      <div className="flex h-20 items-center px-5">
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex w-10 items-center">
            {backHref ? <BackButton href={backHref} /> : null}
          </div>

          <h1 className="truncate text-2xl leading-none font-semibold">
            {title}
          </h1>
        </div>

        <div className="ml-auto">
          <MobileMenu />
        </div>
      </div>
    </header>
  );
}
