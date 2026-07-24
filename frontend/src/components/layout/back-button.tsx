import { ChevronLeft } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";

type BackButtonProps = {
  href: string;
};

export function BackButton({ href }: BackButtonProps) {
  return (
    <Button asChild variant="ghost" size="icon">
      <Link href={href} aria-label="前のページに戻る">
        <ChevronLeft className="size-8" />
      </Link>
    </Button>
  );
}
