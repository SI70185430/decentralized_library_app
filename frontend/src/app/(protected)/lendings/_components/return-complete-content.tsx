import Image from "next/image";
import Link from "next/link";

import { Button } from "@/components/ui/button";

export function ReturnCompleteContent() {
  return (
    <div className="space-y-7">
      <div
        data-ui-id="img_return_complete"
        className="relative mx-auto h-36 w-48 overflow-hidden rounded-md"
      >
        <Image
          src="/images/return-complete.png"
          alt="返却処理完了"
          fill
          sizes="192px"
          className="object-contain"
        />
      </div>

      <p data-ui-id="txt_book_return" className="text-left text-lg font-semibold">
        ご利用ありがとうございました。<br />
        返却処理が完了しました。
      </p>

      <Button
        asChild
        variant="default"
        className="mx-auto flex min-h-[58px] w-48 items-center justify-center rounded-[10px] border border-black bg-[#66f274] px-4 text-center text-2xl font-bold text-black hover:bg-[#66f274] hover:text-black"
      >
        <Link href="/home" data-ui-id="btn_home">
          ホームに戻る
        </Link>
      </Button>
    </div>
  );
}
