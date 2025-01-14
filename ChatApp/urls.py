from django.urls import path
from .views import RegisterView, LoginView, ChatView, TokenBalanceView

urlpatterns = [
    path('register/v1/', RegisterView.as_view(), name='register'),
    path('login/v1/', LoginView.as_view(), name='login'),
    path('chat/v1/', ChatView.as_view(), name='chat'),
    path('tokens/v1/', TokenBalanceView.as_view(), name='token_balance'),
]