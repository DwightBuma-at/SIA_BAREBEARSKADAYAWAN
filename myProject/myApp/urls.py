from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import AdminInventoryViewSet, save_transaction, get_transactions, remove_transaction, remove_all_transactions, admin_pos_history, get_removed_transactions, clear_removed_transactions, save_tracking, get_tracking, update_order_status, delete_transactions # Import the correct ViewSet

# Register the ViewSets with the router
router = DefaultRouter()
router.register(r'admininventory', AdminInventoryViewSet)  # Register AdminInventory ViewSet


urlpatterns = [
    # Define the login view with the correct path
    path('', views.landing_page, name='landing_page'),
    path('login/', views.login_view, name='login'),
    path('sign-up/', views.sign_up, name='signup'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin-ordering/', views.admin_ordering, name='admin_ordering'),
    path('user-ordering/', views.user_ordering, name='user_ordering'),
    path('admin-booking/', views.admin_booking, name='admin_booking'),
    path('user-booking/', views.user_booking, name='user_booking'),
    path('admin-pos/', views.admin_pos, name='admin_pos'),
    path('user-about/', views.user_about, name='user_about'),
    path('admin-inventory/', views.admin_inventory, name='admin_inventory'),
    path('admin-purchasing/', views.admin_purchasing, name='admin_purchasing'),
    path('user-settings/', views.user_settings, name='user_settings'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('user-logout/', views.user_logout, name='user_logout'),
    path('user-ordering-checkout/', views.user_ordering_checkout, name='user_ordering_checkout'),
    path('user-ordering-tracking/', views.user_ordering_tracking, name='user_ordering_tracking'),
    path('user-ordering/cart/', views.user_ordering_cart, name='user_ordering_cart'),
    path('store-cart/', views.store_cart, name='store_cart'),
    path('remove-product/', views.remove_from_cart, name='remove_from_cart'),
    path('empty-cart/', views.empty_cart, name='empty-cart'),
    path('api/save-transaction/', save_transaction, name='save_transaction'),  # Updated endpoint
    path('api/get-transactions/', get_transactions, name='get_transactions'),
    path('api/remove-transaction/<str:transaction_id>/', remove_transaction, name='remove_transaction'),
    path('api/remove-all-transactions/', remove_all_transactions, name="remove_all_transactions"),
    path('admin-pos-history/', views.admin_pos_history, name='admin_pos_history'),
    path('remove-transaction/<str:transaction_id>/', remove_transaction, name='remove_transaction'),
    path('api/removed-transactions/', get_removed_transactions, name='removed_transactions'),
    path('api/clear-removed-transactions/', clear_removed_transactions, name='clear_removed_transactions'),
    path("api/save-tracking/", save_tracking, name="save_tracking"),
    path("api/get-tracking/", get_tracking, name="get_tracking"),
    path('api/update-tracking/<int:order_id>/', update_order_status, name='update_tracking'),
    path('admin-inventory-transactions/', views.admin_inventory_transactions, name='admin_inventory_transactions'),
    path('api/admintransactions/', views.record_transaction, name='record_transaction'),
    path('delete_transactions/', delete_transactions, name='delete_transactions'),
    path('purchase-order/', views.admin_purchasing_order, name='admin_purchasing_order'),
    path('admin-purchasing-logs/', views.admin_purchasing_logs, name='admin_purchasing_logs'),  # Add this line
    path("api/delete-tracking/<int:pk>/", views.delete_tracking, name="delete_tracking"),
    path('admin-ordering-logs/', views.admin_ordering_logs, name='admin_ordering_logs'),
    path('admin-purchasing/list-json/', views.admin_purchasing_list_json, name='admin_purchasing_list_json'), # ADD THIS LINE
    path('admin-purchasing/update-status/<int:order_id>/', views.admin_purchasing_update_status, name='admin_purchasing_update_status'), # ADD THIS LINE
    path('admin-purchasing/update-payment-status/<int:order_id>/', views.admin_purchasing_update_payment_status, name='admin_purchasing_update_payment_status'),
    path('admin_purchasing_delete-transactions/', views.delete_purchasing_transactions, name='admin_purchasing_delete_transactions'),
    path('user-ordering-logs/', views.user_ordering_logs, name='user_ordering_logs'),
    path('admin-purchasing-logs/', views.admin_purchasing_logs, name='admin_purchasing_logs'),
    path("clear-bookings/", views.clear_bookings, name="clear_bookings"),
    path('api/admin-get-orders/', views.admin_get_all_orders, name='admin_get_orders'),
    path('api/return_order/<int:order_id>/', views.return_order, name='return_order'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff-ordering/', views.staff_ordering, name='staff_ordering'),
    path('staff-booking/', views.staff_booking, name='staff_booking'),
    path('staff-pos/', views.staff_pos, name='staff_pos'),
    path('staff-booking-logs/', views.staff_booking_logs, name='staff_booking_logs'),
    path('staff-pos-history/', views.staff_pos_history, name='staff_pos_history'),
    path('staff-ordering-logs/', views.staff_ordering_logs, name='staff_ordering_logs'),
    path('api/suppliers/', views.supplier_api, name='supplier_api'),



    



    path('user-booking/', views.user_booking, name='user_booking'),
    path('save-booking/', views.save_booking, name='save_booking'),
    path('cancel-booking/', views.cancel_booking, name='cancel_booking'),
    
    path('admin-booking/', views.admin_booking, name='admin_booking'),
    path('approve-booking/', views.approve_booking, name='approve_booking'),
    path('seat-booking/', views.seat_booking, name='seat_booking'),
    path('complete-booking/', views.complete_booking, name='complete_booking'),
    path('cancel-booking-admin/<int:booking_id>/', views.cancel_booking_admin, name='cancel_booking_admin'),

    path('admin-booking-counts/', views.admin_booking_counts, name='admin_booking_counts'),
    path('undo-booking/', views.undo_booking, name='undo_booking'),
    path('user-booking-updates/', views.booking_updates, name='booking_updates'),
    path('admin-booking-logs/', views.admin_booking_logs, name='admin_booking_logs'),
    
    path('delete-booking/', views.delete_booking, name='delete_booking'),
    path('user-booking-logs/', views.user_booking_logs, name='user_booking_logs'),
     path('admin-purchasing-delete-transactions/', views.delete_purchasing_transactions, name='admin_purchasing_delete_transactions'),
    path('admin-purchasing-logs/', views.admin_purchasing_logs, name='admin_purchasing_logs'),
    
    path('user-remove-booking/<int:booking_id>/', views.user_remove_booking, name='user_remove_booking'),
    path('api/clear-orders/<int:pk>/', views.clear_orders, name='clear_orders'),
    path('remove-booking/', views.remove_booking, name='remove_booking'),








    







    # API routes for admin inventory and sales using ViewSets (router handles these automatically)
    path('api/', include(router.urls)),  # Include the router's URLs for the API
]
