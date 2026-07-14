type HomeBookSummary = {
  id: string;
  title: string;
  cover_image_url: string | null;
};

export type CurrentLendingListItem = {
  book: HomeBookSummary;
  due_date: string;
  book_copy_location: string;
};

export type CurrentReservationListItem = {
  book: HomeBookSummary;
  scheduled_date: string;
  expires_date: string;
};

export type LendingHistoryListItem = {
  lending_id: string;
  book: HomeBookSummary;
  borrowed_date: string;
  returned_date: string;
};

export type HomeTabFetchResult<T> =
  | { ok: true; data: T }
  | { ok: false };

export type HomeTabData = {
  currentLendings: HomeTabFetchResult<CurrentLendingListItem[]>;
  currentReservations: HomeTabFetchResult<CurrentReservationListItem[]>;
  lendingHistory: HomeTabFetchResult<LendingHistoryListItem[]>;
};
