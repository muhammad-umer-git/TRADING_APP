from django.urls import path
from accounts.api.views import RegisterView , ProtectedAPIView, AccountPositionsView, AccountLedgerView, StockIngestView, StockListView, StockDetailView, TradeView
from rest_framework_simplejwt.views import TokenObtainPairView , TokenRefreshView


urlpatterns = [
    path("auth/", RegisterView.as_view(), name="auth"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/protect/", ProtectedAPIView.as_view(), name="protected_view"),
    path("auth/protect/<int:account_id>/positions/", AccountPositionsView.as_view(), name="positions_view"),
    path("auth/protect/<int:account_id>/ledger/", AccountLedgerView.as_view(), name="ledger_view"),
    path("stock/ingest/", StockIngestView.as_view(), name="stock_ingest"),
    path("stocks/", StockListView.as_view(), name="stock_list"),
    path("stocks/<str:symbol>/", StockDetailView.as_view(), name="stock_detail"),
    path("trade/", TradeView.as_view(), name="trade")
]
