from django.urls import path

from . import views

app_name = "lending"

urlpatterns = [
    path("lendings/", views.LendingCreateView.as_view(), name="lending-create"),
    path(
        "lendings/<uuid:lending_id>/",
        views.LendingDetailView.as_view(),
        name="lending-detail",
    ),
    path(
        "lendings/<uuid:lending_id>/extend/",
        views.LendingExtendView.as_view(),
        name="lending-extend",
    ),
    path(
        "lendings/<uuid:lending_id>/return/",
        views.LendingReturnView.as_view(),
        name="lending-return",
    ),
    path(
        "me/lendings/current/",
        views.MyCurrentLendingListView.as_view(),
        name="my-current-lendings",
    ),
    path(
        "me/lendings/history/",
        views.MyLendingHistoryListView.as_view(),
        name="my-lending-history",
    ),
    # ------------------------------------------------
    path(
        "reservations/",
        views.ReservationCreateView.as_view(),
        name="reservation-create",
    ),
    path(
        "reservations/<uuid:reservation_id>/",
        views.ReservationDetailView.as_view(),
        name="reservation-detail",
    ),
    path(
        "reservations/<uuid:reservation_id>/cancel/",
        views.ReservationCancelView.as_view(),
        name="reservation-cancel",
    ),
    path(
        "reservations/<uuid:reservation_id>/convert-to-lending/",
        views.ReservationConvertToLendingView.as_view(),
        name="reservation-convert-to-lending",
    ),
    path(
        "me/reservations/current/",
        views.MyCurrentReservationListView.as_view(),
        name="my-current-reservations",
    ),
]
