from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


def success_response():
    return Response(
        {"detail": "OK"},
        status=status.HTTP_200_OK,
    )


class BookListView(APIView):
    def get(self, request):
        return success_response()


class GenreListView(APIView):
    def get(self, request):
        return success_response()


class BookDetailView(APIView):
    def get(self, request, pk):
        return success_response()
