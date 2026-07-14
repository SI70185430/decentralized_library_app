from accounts.models import AppUser
from lending.models import Lending, Reservation

MAX_CONCURRENT_LENDING_AND_RESERVATION_COUNT = 10
LENDING_RESERVATION_LIMIT_ERROR_MESSAGE = "貸出中・予約中の合計冊数が上限の10冊に達しています"


def lock_user_and_get_current_usage(user: AppUser) -> int:
    """
    ユーザー行を lock し、未返却貸出と予約の合計数を返す。

    呼び出し元の transaction.atomic() 内で使用すること。呼び出し元が貸出または
    予約の作成を完了して transaction を commit するまで、ユーザー行の lock は
    保持される。
    """
    locked_user = AppUser.objects.select_for_update().only("pk").get(pk=user.pk)
    active_lending_count = Lending.objects.filter(
        user_id=locked_user.pk,
        returned_date__isnull=True,
    ).count()
    reservation_count = Reservation.objects.filter(user_id=locked_user.pk).count()
    return active_lending_count + reservation_count
