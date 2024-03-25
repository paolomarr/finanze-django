from django.http import Http404
from django.db.models import Min, Max
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from finanze.permissions import IsOwnerOrDeny, IsAuthenticatedSelfUser

from django.contrib.auth.models import User

from movimenti.serializers import CategorySerializer, MovementSerializer, SubcategorySerializer, UserSerializer
from movimenti.models import AssetBalance, Category, Movement, Subcategory


class MovementList(APIView):

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
        filterdict = self._filterDict(request)
            
        movements = Movement.objects.filter(**filterdict)
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

        aggregates = movements.aggregate(minDate=Min("date"), maxDate=Max("date"))

        baseline = AssetBalance.objects.balance_to_date(user=request.user, date=aggregates["minDate"])
        

        serializer = MovementSerializer(movements, many=True)
        return Response({"movements": serializer.data, "baseline": baseline, "minDate": aggregates.get("minDate"), "maxDate": aggregates.get("maxDate")})

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


class LoggedInUserDetail(UserList):
    permission_classes = [IsAdminUser|IsAuthenticatedSelfUser]
    
    def get(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(id=request.user.id)
        return super().get(request, *args, **kwargs)


class CategoryListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(user=request.user)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(user=[self.request.user])

class CategoryDetail(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SubcategoryListCreate(generics.ListCreateAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

    def perform_create(self, serializer):
        return serializer.save(user=[self.request.user])

class SubcategoryDetail(generics.RetrieveAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

