type BookSummaryCardProps = {
  lines: string[];
};

export function BookSummaryCard({ lines }: BookSummaryCardProps) {
  return (
    <article className="flex h-[214px] items-center rounded-[16px] border border-black bg-white px-9 text-black">
      <div className="flex h-[154px] w-[84px] shrink-0 items-center justify-center bg-[#d9d9d9] text-xl font-semibold">
        書影
      </div>

      <dl className="ml-11 min-h-[122px] space-y-7 text-[22px] leading-none font-semibold">
        {lines.map((line) => (
          <div key={line}>
            <dt className="sr-only">書籍情報</dt>
            <dd className="whitespace-pre-line">{line}</dd>
          </div>
        ))}
      </dl>
    </article>
  );
}
