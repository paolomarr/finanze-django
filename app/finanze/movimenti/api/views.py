from django.http import Http404
from django.db.models import expressions
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from finanze.permissions import IsOwnerOrDeny, IsAuthenticatedSelfUser

from django.contrib.auth.models import User

from movimenti.serializers import CategorySerializer, MovementSerializer, UserSerializer
from movimenti.models import Category, Movement


class MovementList(APIView):
    permission_classes = [IsAuthenticated]

    def _filterDict(self, request):
        params = request.GET
        filterdict = {"user": request.user}
        accepted_filter_params = [
            ("datefrom", "date_gte"),
            ("dateto", "date_lt"),
            ("description", "description_icontains"),
            ("category", "category_id"),
            ("subcategory", "subcategory_id"),
        ]
        for (param, column) in accepted_filter_params:
            val = params.get(param)
            if val:
                filterdict[column] = val
        return filterdict

    """
    List all movements, or create a new one.
    """
    def get(self, request):
        movements = Movement.objects.filter(**(self._filterDict(request)))
        params = request.GET
        sort_field = params.get("sort_field", "-date")
        movements = movements.order_by(sort_field)
        sort_dir = params.get("sort_dir")
        if sort_dir:
            if sort_dir == "desc":
                movements = movements.expressions.desc()
            
        if params.get("all") is None:
            try:
                page = int(params.get("page", 1))
            except:
                page = 1
            try:
                size = max(2, int(params.get("size", 100)))
            except:
                size = 100
            start = (page-1)*size
            end = start + size
            movements = movements[start:end]
        serializer = MovementSerializer(movements, many=True)
        return Response(serializer.data)

    def post(self, request):
        # this will require proper CSRF handling
        serializer = MovementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class MovementDetail(APIView):
    permission_classes = [IsOwnerOrDeny]

    """
    Retrieve, update or delete a movement.
    """
    def get_object(self, pk):
        try:
            obj = Movement.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except Movement.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        movement = self.get_object(pk)
        serializer = MovementSerializer(movement)
        return Response(serializer.data)

    def put(self, request, pk):
        movement = self.get_object(pk)
        serializer = MovementSerializer(movement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        movement = self.get_object(pk)
        movement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserList(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser|IsAuthenticatedSelfUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CategoryList(APIView):
    """
    List all categories, or create a new one.
    """
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)