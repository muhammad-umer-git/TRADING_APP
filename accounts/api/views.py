from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegisterSerializer, AccountSerializer, PositionSerializer, LedgerSerializer, StockSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from accounts.models import Account, Position, Ledger, Stock
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from decimal import Decimal
from accounts.api.tasks import process_trade

class RegisterView(APIView):
    def post(self, request):
        serilaizer = RegisterSerializer(data = request.data)
        if serilaizer.is_valid():
            serilaizer.save()
            return Response({"message":"User has been Registered Successfully"}, status=status.HTTP_201_CREATED)
        return Response(serilaizer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProtectedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        account = request.user.account
        serializer = AccountSerializer(account)
        return Response ({
            "username" : request.user.username,
            "account" : serializer.data
        })

class AccountPositionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, account_id):
        try:
            account = Account.objects.get(id=account_id, user=request.user)
        except Account.DoesNotExist:
            return Response({"error":"Account not found"}, status=status.HTTP_404_NOT_FOUND)

        positions = account.positions.all()
        serializer = PositionSerializer(positions, many=True) 
        return Response(serializer.data)

class AccountLedgerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, account_id):
        try:
            account = Account.objects.get(id=account_id, user=request.user)
        except Account.DoesNotExist:
            return Response({"error message":"Account not found"}, status=status.HTTP_404_NOT_FOUND)
        
        ledger = account.ledger.all()
        serializer = LedgerSerializer(ledger, many=True)
        return Response(serializer.data)
        

class StockIngestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StockSerializer(data = request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Stock ingested Successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class StockListView(generics.ListAPIView):
    queryset = Stock.objects.all().order_by("id")
    serializer_class = StockSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["symbol", "exchange"]
    permission_classes = [AllowAny]

class StockDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, symbol):
        key = f"stock:{symbol}"
        data = cache.get(key)

        if data is None:
            stock = get_object_or_404(Stock, symbol=symbol)
            serializer = StockSerializer(stock)
            data = serializer.data
            cache.set(key, data, timeout=600)
        return Response(data)

class TradeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        symbol = request.data.get("symbol")
        quantity = request.data.get("quantity")
        trade_type = request.data.get("trade_type")

        process_trade.delay(request.user.id, symbol, quantity, trade_type)
        return Response({"message": "Trade submitted for processing."})



# class TradeView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         symbol = request.data.get("symbol")
#         quantity = request.data.get("quantity")
#         side = request.data.get("side")

#         if not all([symbol, quantity, side]):
#             return Response({"error":"Missing required fields."}, status=400)
        
#         # if side not in ["buy", "sell"]:
#         #     return Response({"error":"Missing side. Must be 'buy' or 'sell'."}, status=400)

#         try:
#             stock = Stock.objects.get(symbol=symbol)
#         except Stock.DoesNotExist:
#             return Response({"error": "Stock not found"}, status=404)

#         account = request.user.account

#         try:
#             quantity = Decimal(quantity)
#         except:
#             return Response({"error": "Quantity must be a number."}, status=400)


#         if side == "buy":
#             total_cost = stock.price *quantity
#             if account.balance < total_cost:
#                 return Response({"error": "Insufficient balance."}, status=400)
            
#             account.balance -= total_cost
#             account.save()

#             Ledger.objects.create(
#                 account=account,
#                 transaction_type="withdraw",
#                 amount=total_cost
#             )

#             position = account.positions.filter(symbol=symbol).first()
#             if position:
#                 position.quantity += quantity
#                 position.average_price = stock.price
            
#             else:
#                 Position.objects.create(
#                     account=account,
#                     symbol=symbol,
#                     quantity=quantity,
#                     average_price=stock.price
#                 )
        
        
#         elif side == "sell":
#             total_revenue = stock.price * quantity

#             position = account.positions.filter(symbol=symbol).first()
#             if not position or position.quantity < quantity:
#                 return Response ({"error": "Not enough stock to sell."}, status=400)

#             account.balance+=total_revenue
#             account.save()

#             Ledger.objects.create(
#                 account=account,
#                 transaction_type="deposit",
#                 amount=total_revenue
#             )

#             position.quantity-=quantity
#             if position.quantity == 0:
#                 position.delete()
#             else:
#                 position.save()
        
#         else:
#             return Response({"error": "Side must be buy or sell"}, status=400)



#         return Response({
#             "message":f"Successfully executed {side} order",
#             "symbol": stock.symbol,
#             "name": stock.name,
#             "exchange": stock.exchange,
#             "price": stock.price,
#             "quantity": quantity,
#             "new_balance":account.balance       
#         }, status=200)