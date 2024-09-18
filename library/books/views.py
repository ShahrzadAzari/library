from library.db import Database
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class BookListView(APIView):
    """
    This view shows list of books along with user's rating for each book.
    Only authenticated users can use this view.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id

        db = Database()
        conn = db.get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT books.id, title, author, genre, reviews.rating 
                FROM books LEFT JOIN reviews
                ON books.id = reviews.book_id AND reviews.user_id = %s
            """, [user_id])
            books = cur.fetchall()
            return Response({"books": books}, status=status.HTTP_200_OK)


class BookFilterView(APIView):
    """
    This view get a parameter named 'genre'. 
    Shows list of books with the specified genre along with user's rating for each book.
    only authenticated users can use this view.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        genre = request.query_params.get('genre', None)
        db = Database()
        conn = db.get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT books.id, title, author, genre, reviews.rating
                FROM books
                LEFT JOIN reviews
                ON books.id = reviews.book_id AND reviews.user_id = %s
                WHERE books.genre = %s 
            """, [user_id, genre])
            books = cur.fetchall()
            return Response({"books": books}, status=status.HTTP_200_OK)


class AddReviewView(APIView):
    """
    This view gets 'book_id' and 'rating' in the request body.
    Add the review with provided parameters.
    only authenticated users can use this view.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.id
        book_id = request.data.get("book_id")
        rating = request.data.get("rating")

        if user_id is None or book_id is None or rating is None:
            return Response({"message": "Wrong parameters"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rating = int(rating)
        except:
            return Response({"message": "Rating should be integer"}, status=status.HTTP_400_BAD_REQUEST)

        if rating < 1 or rating > 5:
            return Response({"message": "Rating should be between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)

        db = Database()
        conn = db.get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM books WHERE id=%s", [book_id])
            if cur.fetchone() is None:
                return Response({"message": "Wrong book_id"}, status=status.HTTP_400_BAD_REQUEST)

            cur.execute("SELECT id FROM reviews WHERE book_id=%s AND user_id=%s", [book_id, user_id])
            if cur.fetchone() is not None:
                return Response({"message": "Rating already exists"}, status=status.HTTP_400_BAD_REQUEST)

            cur.execute(
                """
                INSERT INTO reviews (user_id, book_id, rating) VALUES (%s, %s, %s)
                """,
                [user_id, book_id, rating]
            )
            conn.commit()
            return Response({"message": "Review added successfully"}, status=201)


class UpdateReviewView(APIView):
    """
    This view gets 'book_id' and 'rating' in the request body.
    update the review with provided parameters.
    only authenticated users can use this view.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.id
        book_id = request.data.get("book_id")
        new_rating = request.data.get("rating")

        if user_id is None or book_id is None or new_rating is None:
            return Response({"message": "Wrong parameters"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_rating = int(new_rating)
        except:
            return Response({"message": "Rating should be integer"}, status=status.HTTP_400_BAD_REQUEST)

        if new_rating < 1 or new_rating > 5:
            return Response({"message": "Rating should be between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)

        db = Database()
        conn = db.get_connection()
        with conn.cursor() as cur:

            cur.execute("SELECT id FROM reviews WHERE book_id=%s AND user_id=%s", [book_id, user_id])
            if cur.fetchone() is None:
                return Response({"message": "Review does not exists"}, status=status.HTTP_400_BAD_REQUEST)

            cur.execute(
                "UPDATE reviews SET rating = %s WHERE user_id = %s AND book_id = %s",
                [new_rating, user_id, book_id]
            )
            conn.commit()
            return Response({"message": "Review updated successfully"}, status=status.HTTP_200_OK)


class DeleteReviewView(APIView):
    """
    This view gets 'book_id' in the request body.
    Delete the review with provided parameters.
    only authenticated users can use this view.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = request.user.id
        book_id = request.data.get("book_id")

        db = Database()
        conn = db.get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM reviews WHERE user_id = %s AND book_id = %s",
                [user_id, book_id]
            )
            conn.commit()
            return Response({"message": "Review deleted successfully"}, status=status.HTTP_200_OK)


class SuggestBooksView(APIView):
    """
    This view suggests list of books.
    Suggestion is based on average rating of the user on each book genre.
    Only authenticated users can use this view.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id

        db = Database()
        conn = db.get_connection()

        with conn.cursor() as cur:
        # Get the genres user rated highest on
            cur.execute("""
                SELECT books.genre, AVG(reviews.rating) as avg_rating
                FROM reviews
                JOIN books ON reviews.book_id = books.id
                WHERE reviews.user_id = %s
                GROUP BY books.genre
                ORDER BY avg_rating DESC
                LIMIT 1
            """, [user_id])
            
            genre = cur.fetchone()
            if genre:
                genre = genre[0]
                cur.execute("SELECT books.id, title, author, genre FROM books WHERE genre = %s", [genre])

                suggested_books = cur.fetchall()
                return Response({"suggested_books": suggested_books}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "There is not enough data about you"}, status=status.HTTP_200_OK)
