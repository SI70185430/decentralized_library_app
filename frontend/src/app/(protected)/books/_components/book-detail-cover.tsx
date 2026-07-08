type BookDetailCoverProps = {
  title: string;
  coverImageUrl: string | null;
};

export function BookDetailCover({ title, coverImageUrl }: BookDetailCoverProps) {
  return (
    <div className="flex h-[250px] w-[148px] shrink-0 items-center justify-center overflow-hidden bg-[#d9d9d9] text-2xl font-semibold text-black">
      {coverImageUrl ? (
        // biome-ignore lint/performance/noImgElement: 書影URLは任意ドメインを受け取るため next/image の remotePatterns では制約が強すぎる
        <img
          src={coverImageUrl}
          alt={`${title}の書影`}
          referrerPolicy="no-referrer"
          className="h-full w-full object-cover"
        />
      ) : (
        "書影"
      )}
    </div>
  );
}
