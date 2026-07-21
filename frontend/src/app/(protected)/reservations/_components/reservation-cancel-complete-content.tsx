import Image from "next/image";
import Link from "next/link";

type ReservationCancelCompleteContentProps = {
  title: string;
};

export function ReservationCancelCompleteContent({
  title,
}: ReservationCancelCompleteContentProps) {
  return (
    <div className="space-y-7">
      <div
        data-ui-id="img_cancel_complete"
        className="relative mx-auto h-36 w-48 overflow-hidden rounded-md"
      >
        <Image
          src="/images/cancel-complete.png"
          alt="予約キャンセル完了"
          fill
          sizes="192px"
          className="object-contain"
        />
      </div>

      <p data-ui-id="txt_cancel_reservation" className="text-left text-lg font-semibold">
        予約のキャンセルが完了しました。
      </p>

      <div className="space-y-2">
        <p className="text-sm font-semibold text-[#777]">タイトル</p>
        <p data-ui-id="lbl_title" className="text-xl font-bold break-words">
          {title}
        </p>
      </div>

      <Link
        href="/home"
        data-ui-id="btn_home"
        className="mx-auto flex min-h-[58px] w-48 items-center justify-center rounded-[10px] border border-black bg-[#66f274] px-4 text-center text-2xl font-bold text-black"
      >
        ホームに戻る
      </Link>
    </div>
  );
}
