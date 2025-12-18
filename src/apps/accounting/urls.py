from django.urls import path

from . import views

app_name = 'apps.accounting'

urlpatterns = [
    # Petty Cash Transaction
    path('petty-cash/transaction/attach/create', views.PettyCashTransactionAttachDocCreate.as_view(),
         name='petty_cash_transaction__create_attachment_doc'),

    path('petty-cash/transaction/status/create', views.PettyCashTransactionStatusCreate.as_view(),
         name='petty_cash_transaction_status__create'),

    path('petty-cash/transaction/create', views.PettyCashTransactionCreate.as_view(),
         name='petty_cash_transaction__create'),

    path('petty-cash/transaction/<int:pk>/update', views.PettyCashTransactionUpdate.as_view(),
         name='petty_cash_transaction__update'),

    path('petty-cash/transaction/list', views.PettyCashTransactionList.as_view(),
         name='petty_cash_transaction__list'),

    path('petty-cash/transaction/<int:pk>/detail', views.PettyCashTransactionDetail.as_view(),
         name='petty_cash_transaction__detail'),

    # Document

    path('document/create', views.DocumentCreate.as_view(),
         name='document__create'),

    path('document/<int:pk>/update', views.DocumentUpdate.as_view(),
         name='document__update'),

    path('document/list', views.DocumentList.as_view(),
         name='document__list'),

    path('document/<int:pk>/detail', views.DocumentDetail.as_view(),
         name='document__detail'),

    path('document/status/create', views.DocumentStatusCreate.as_view(),
         name='document_status__create'),
]
