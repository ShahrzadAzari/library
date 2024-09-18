from django.urls import path
from .views import BookListView, BookFilterView, AddReviewView, UpdateReviewView, DeleteReviewView, SuggestBooksView

urlpatterns = [
    path('book/list', BookListView.as_view(), name='book_list'),
    path('book', BookFilterView.as_view(), name='book_filter'),
    path('review/add', AddReviewView.as_view(), name='add_review'),
    path('review/update', UpdateReviewView.as_view(), name='update_review'),
    path('review/delete', DeleteReviewView.as_view(), name='delete_review'),
    path('suggest', SuggestBooksView.as_view(), name='suggest_books'),
]
