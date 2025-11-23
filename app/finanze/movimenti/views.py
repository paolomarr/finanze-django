from django.http import Http404
from django.db.models import Min, Max, Count
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from finanze.permissions import IsOwnerOrDeny, IsAuthenticatedSelfUser

from django.contrib.auth.models import User

from movimenti.serializers import CategorySerializer, MovementSerializer, SubcategorySerializer
from movimenti.models import AssetBalance, Category, Movement, Subcategory

from . import logger

def filterDict(request, accepted_filter_params: list[tuple]):
    params = request.query_params
    filterdict = {"user": request.user}
    for (param, column) in accepted_filter_params:
        raw_val = params.get(param, None)
        if raw_val is None:
            continue
        if column.endswith("__in"):
            val = raw_val.split(",")
        else:
            val = raw_val
        if val:
            filterdict[column] = val
    return filterdict

    
class MovementList(APIView):

    """
    List all movements, or create a new one.
    """
    def get(self, request):
        accepted_filter_params = [
            ("datefrom", "date__gte"),
            ("dateto", "date__lt"),
            ("description", "description_icontains"),
            ("category", "category_id__in"),
            ("subcategory", "subcategory_id__in"),
            ("minamount", "amount__gte"),
            ("maxamount", "amount__lte"),
        ]
        logger.debug(f"Request params: {request.query_params}")
        filterdict = filterDict(request, accepted_filter_params)
        logger.debug(f"Filter dict: {filterdict}")
        # overall, all-time stats
        alltime = {
            "count": Movement.objects.count(),
            "minDate": Movement.objects.all().aggregate(minDate=Min("date"))["minDate"],
            "maxDate": Movement.objects.all().aggregate(maxDate=Max("date"))["maxDate"],
        } 
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

        serializer = MovementSerializer(movements, many=True)

        filtered = {
            "count": len(serializer.data),
            "movements": serializer.data,
            "minDate": aggregates.get("minDate"), 
            "maxDate": aggregates.get("maxDate")
        }
        previous = {
            "count": 0,
        }
        if filterdict.get("date__gte"):
            previous_movements_query = Movement.objects.filter(user=request.user, date__lte=filterdict.get("date__gte"))
            aggregates = previous_movements_query.aggregate(minDate=Min("date"), maxDate=Max("date"), count=Count("id"))
            baseline = Movement.objects.balance_to_date(user=request.user, date=aggregates["maxDate"])
            
            previous = {
                "count": aggregates.get("count"),
                "minDate": aggregates.get("minDate"), 
                "maxDate": aggregates.get("maxDate"),
                "balance": {
                    "date": baseline[0],
                    "value": baseline[1],
                }
            }

        return Response({
            "filtered": filtered,
            "previous": previous,
            "alltime": alltime,
            })

    def post(self, request):
        # this will require proper CSRF handling
        serializer = MovementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class BalanceMovementList(generics.ListAPIView):
    permission_classes = [IsAdminUser|IsAuthenticatedSelfUser]
    balance_cat = Category.objects.get(category="BALANCE")
    queryset = Movement.objects.filter(category=balance_cat).order_by("-date")
    serializer_class = MovementSerializer

    def get(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(user=request.user)
        return self.list(request, *args, **kwargs)


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


class CategoryListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(user=request.user) | self.queryset.filter(user__isnull=True)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(user=[self.request.user])

class CategoryDetail(generics.RetrieveUpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SubcategoryListCreate(generics.ListCreateAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

    def perform_create(self, serializer):
        return serializer.save(user=[self.request.user])

class SubcategoryDetail(generics.RetrieveUpdateAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

    