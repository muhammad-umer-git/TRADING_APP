from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import RegisterSerializer, AccountSerializer, PositionSerializer, LedgerSerializer, StockSerializer, TradeSerializer
from rest_framework.permissions import IsAuthenticated
from accounts.models import Account, Position, Ledger, Stock, Trade
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from decimal import Decimal
from .tasks import process_trade
from core.throttles import LoginThrottle, RegisterThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

class RegisterView(APIView):
    throttle_classes = [RegisterThrottle]  

    def post(self, request):
        serilaizer = RegisterSerializer(data = request.data)
        if serilaizer.is_valid():
            serilaizer.save()
            return Response({"message":"User has been Registered Successfully"}, status=status.HTTP_201_CREATED)
        return Response(serilaizer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(TokenObtainPairView):
    throttle_classes = [LoginThrottle]


class ProtectedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        account = request.user.account
        serializer = AccountSerializer(account)
        return Response ({
            "username" : request.user.username,
            "account" : serializer.data
        })



class AccountViewSets(viewsets.ModelViewSet):

    queryset = Account.objects.select_related("user").prefetch_related("positions", "ledger", "trades")
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
        
    @action(detail=True, methods=["get"])
    def ledger(self, request, pk=None):
        account = get_object_or_404(Account, pk=pk, user=request.user)
        ledger = account.ledger.all()
        serializer = LedgerSerializer(ledger, many=True)
        
        return Response(serializer.data)
        
    @action(detail=True, methods=["get"])
    def positions(self, request, pk=None):
        account = get_object_or_404(Account, pk=pk, user=request.user)
        positions =  account.positions.all()
        serializer = PositionSerializer(positions, many=True)

        return Response(serializer.data)


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all().order_by("id")
    serializer_class = StockSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["symbol", "exchange"]
    search_fields = ["symbol", "name"]
    ordering_fields = ["price", "symbol", "created_at"]
    ordering = ["symbol"]



    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def ingest(self, request):
        serializer = self.get_serializer(data = request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Stock ingested Successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    @action(detail=True, methods=["get"], url_path="detail", permission_classes=[AllowAny])
    def detail(self, request, pk=None):
        stock=self.get_object()
        key = f"stock:{stock.symbol}"
        data = cache.get(key)

        if data is None:
            serializer = StockSerializer(stock)
            data = serializer.data
            cache.set(key, data, timeout=600)
        return Response(data)

class TradeViewSet(viewsets.ModelViewSet):
    queryset = Trade.objects.select_related("account", "account__user").all()
    serializer_class = TradeSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def execute_trade(self, request):
        symbol = request.data.get("symbol")
        quantity = request.data.get("quantity")
        trade_type = request.data.get("trade_type")

        process_trade.delay(request.user.id, symbol, quantity, trade_type)
        return Response({"message": "Trade submitted for processing."})
