import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import login as django_login
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from .models import Cart, AdminInventory, Signup, Transaction, TransactionItem, RemovedTransaction, Tracking, StockInTransaction, PurchaseOrder, Booking, APLogs, ABlog, UBlog, DeletedTracking, DeletedTrackingItem, UTlogs, UTlogItem, Supplier
from .serializers import AdminInventorySerializer
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_protect
from rest_framework.decorators import api_view
from rest_framework import status
from django.utils.timezone import localtime, now, datetime  # Helps format datetime correctly
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date
from django.views.decorators.http import require_POST, require_GET
from django.utils.timezone import localdate
from django.db.models import Sum
from .supabase_client import supabase  # Adjust path if needed


# Landing Page View
def landing_page(request):
    return render(request, 'myApp/index.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            response = supabase.auth.sign_in_with_password({
                'email': email,
                'password': password
            })

            user = response.user
            session = response.session

            if not user or not session:
                messages.error(request, "Login failed. Invalid credentials or unverified email.")
                return redirect('login')

            if user.email_confirmed_at is None:
                messages.error(request, "Please verify your email before logging in.")
                return redirect('login')

            # Save Supabase session
            request.session['access_token'] = session.access_token
            request.session['user_email'] = email

            if email.endswith('@admin.com'):
                return redirect('admin_dashboard')
            
            elif email.endswith('@staff.com'):
                return redirect('staff_dashboard')
            
            else:
                return redirect('user_dashboard')

        except Exception as e:
            messages.error(request, f"Login error: {str(e)}")
            return redirect('login')

    return render(request, 'myapp/login.html')



# Sign Up View
def sign_up(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            response = supabase.auth.sign_up({
                'email': email,
                'password': password
            })

            if not response.user:
                messages.error(request, "Sign up failed. Please try again.")
                return redirect('signup')

            messages.success(request, "Account created! Check your email to verify before logging in.")
            return redirect('login')

        except Exception as e:
            messages.error(request, f"Sign up error: {str(e)}")
            return redirect('signup')

    return render(request, 'myapp/signup.html')


# Dashboard and other Page Views

def staff_dashboard(request):
    user_email = request.session.get('user_email')  # <-- new line added
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    return render(request, "myapp/staff-dashboard.html", {
        'email': user_email,     # <-- new line added
        'username': username,    # <-- new line added
    })

def staff_ordering(request):
    user_email = request.session.get('user_email')  # <-- new line added
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    return render(request, "myapp/staff-ordering.html", {
        'email': user_email,     # <-- new line added
        'username': username,    # <-- new line added
    })


def admin_dashboard(request):
    user_email = request.session.get('user_email')  # <-- new line added
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    return render(request, "myapp/admin-dashboard.html", {
        'email': user_email,     # <-- new line added
        'username': username,    # <-- new line added
    })


def staff_booking(request):
    user_email = request.session.get('user_email')  # <-- new line added
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    online_bookings = Booking.objects.all().order_by('-booked_at')

    in_session_people = Booking.objects.filter(status='In-Session').aggregate(Sum('people_count'))['people_count__sum'] or 0
    booked_online_count = Booking.objects.filter(status='Approved').count()
    today = localdate()
    today_booked_count = Booking.objects.filter(status='Approved', booking_date=today).count()
    total_capacity = 10
    pending_booking_count = Booking.objects.filter(status='Pending').count()

    context = {
        'online_bookings': online_bookings,
        'in_session_people': in_session_people,
        'booked_online_count': booked_online_count,
        'today_booked_count': today_booked_count,
        'pending_booking_count': pending_booking_count,
        'email': user_email,     # <-- new line added
        'username': username,    # <-- new line added
    }
    return render(request, 'myApp/staff-booking.html', context)


def staff_pos(request):
    user_email = request.session.get('user_email')  # <-- new line added
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    pos_orders = Tracking.objects.filter(source='pos').order_by('-created_at')
    return render(request, 'myapp/staff-pos.html', {
        'pos_orders': pos_orders,
        'email': user_email,     # <-- new line added
        'username': username,    # <-- new line added
    })


def staff_booking_logs(request):
    user_email = request.session.get('user_email')  # <-- new line added
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    ablogs = ABlog.objects.all().order_by('-removed_at')
    return render(request, 'myApp/staff-booking-logs.html', {
        'ablogs': ablogs,
        'email': user_email,     # <-- new line added
        'username': username,    # <-- new line added
    })


def staff_pos_history(request):
    user_email = request.session.get('user_email')  # <-- new line added
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    return render(request, 'myApp/staff-pos-history.html', {
        'email': user_email,     # <-- new line added
        'username': username,    # <-- new line added
    })


def staff_ordering_logs(request):
    user_email = request.session.get('user_email')  # <-- new line added
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    logs = DeletedTracking.objects.all().order_by('-deleted_at')
    return render(request, 'myApp/staff-ordering-logs.html', {
        'logs': logs,
        'email': user_email,     # <-- new line added
        'username': username,    # <-- new line added
    })



def user_dashboard(request):
    email = request.session.get('user_email', 'Guest')

    # Optional: extract username before @
    username = email.split('@')[0] if '@' in email else email

    return render(request, 'myapp/user-dashboard.html', {'email': email, 'username': username})



def admin_ordering(request):
    user_email = request.session.get('user_email')  # <-- new line added
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    return render(request, "myapp/admin-ordering.html", {
        'email': user_email,     # <-- new line added
        'username': username,    # <-- new line added
    })



def user_ordering(request):
    email = request.session.get('user_email', 'Guest')
    username = email.split('@')[0] if '@' in email else email

    return render(request, "myapp/user-ordering.html", {
        'email': email,
        'username': username
    })



def admin_booking(request):
    user_email = request.session.get('user_email')  # <-- new line added
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    online_bookings = Booking.objects.all().order_by('-booked_at')

    # In-Session Tracker
    in_session_people = Booking.objects.filter(status='In-Session').aggregate(Sum('people_count'))['people_count__sum'] or 0

    # Booked (Online) Tracker
    booked_online_count = Booking.objects.filter(status='Approved').count()

    # Today Booked Tracker
    today = localdate()
    today_booked_count = Booking.objects.filter(status='Approved', booking_date=today).count()

    # Available Tracker (assuming a total capacity of 10 - adjust as needed)
    total_capacity = 10
    pending_booking_count = Booking.objects.filter(status='Pending').count()

    context = {
        'online_bookings': online_bookings,
        'in_session_people': in_session_people,
        'booked_online_count': booked_online_count,
        'today_booked_count': today_booked_count,
        'pending_booking_count': pending_booking_count,
        'email': user_email,     # <-- new line added
        'username': username,    # <-- new line added
    }
    return render(request, 'myApp/admin-booking.html', context)



def admin_pos(request):
    user_email = request.session.get('user_email')  # <-- new line added
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    pos_orders = Tracking.objects.filter(source='pos').order_by('-created_at')  # optional ordering
    return render(request, 'myapp/admin-pos.html', {
        'pos_orders': pos_orders,
        'email': user_email,     # <-- new line added
        'username': username,    # <-- new line added
    })



def user_about(request):
    user_email = request.session.get('user_email')
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    return render(request, 'myapp/user-about.html', {
        'email': user_email,    # <-- new line added
        'username': username,   # <-- new line added
    })



def admin_inventory(request):
    user_email = request.session.get('user_email')  # <-- new line added
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    return render(request, 'myapp/admin-inventory.html', {
        'email': user_email,     # <-- new line added
        'username': username,    # <-- new line added
    })


def admin_purchasing(request):
    user_email = request.session.get('user_email')  # <-- new line added
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    return render(request, 'myapp/admin-purchasing.html', {
        'email': user_email,     # <-- new line added
        'username': username,    # <-- new line added
    })



def user_settings(request):
    user_email = request.session.get('user_email')
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    return render(request, 'myapp/user-settings.html', {
        'email': user_email,    # <-- new line added
        'username': username,   # <-- new line added
    })


def admin_logout(request):
    request.session.flush()
    return redirect('login')

def user_logout(request):
    request.session.flush()
    return redirect('login')


def user_ordering_checkout(request):
    # --- New code added below ---
    user_email = request.session.get('user_email')
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added
    # --- End new code ---

    # Get the cart data from the session
    cart = request.session.get('cart', [])
    
    # Initialize the empty cart message
    empty_cart_message = None

    # Get the selected items from the request (e.g., using request.GET or request.POST)
    selected_ids = request.GET.getlist('selected_items')  # assuming you pass selected items as a list of IDs in the query string
    
    # If the cart is empty, display a message
    if not cart:
        empty_cart_message = "Your cart is empty. Please add items before proceeding."

    # If selected items are passed, filter the cart to show only those
    if selected_ids:
        cart = [item for item in cart if str(item['id']) in selected_ids]  # assuming each cart item has an 'id' field
    
    # Calculate the total price of the selected items
    total_price = sum(item['price'] * item['quantity'] for item in cart) if cart else 0

    # Pass the filtered cart, total_price, empty_cart_message, email, and username to the template context
    return render(request, 'myApp/user-ordering-checkout.html', {
        'cart': cart,
        'total_price': total_price,
        'empty_cart_message': empty_cart_message,  # Pass the message to template
        'email': user_email,                        # <-- new line added
        'username': username,                       # <-- new line added
    })


def remove_from_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        # Retrieve the cart from the session
        cart = request.session.get('cart', [])
        
        # Find and remove the item
        cart = [item for item in cart if item['id'] != product_id]
        
        # Save the updated cart back to the session
        request.session['cart'] = cart
        
        # Calculate the new total price
        total_price = sum(item['price'] * item['quantity'] for item in cart)

        return JsonResponse({'success': True, 'new_total_price': total_price})

def empty_cart(request):
    # Clear the cart from the session
    request.session['cart'] = []  # Clear the session cart

    # Optionally, show a message or a redirect
    messages.info(request, "Your cart has been emptied.")
    
    # Redirect to a page where you notify the user that the cart is empty
    return redirect('empty-cart-notification')  # Redirect to a separate page or show a message



def user_ordering_tracking(request):
    email = request.session.get('user_email', 'Guest')
    username = email.split('@')[0] if '@' in email else email

    return render(request, 'myapp/user-ordering-tracking.html', {
        'email': email,
        'username': username
    })



def user_ordering_cart(request):
    return render(request, 'user-ordering/cart.html')


@csrf_protect
def store_cart(request):
    if request.method == 'POST':
        try:
            cart_data = json.loads(request.body)
            # Do something with the cart data (like saving it to a session or database)
            return JsonResponse({"message": "Cart stored successfully!"}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)

    return JsonResponse({"error": "Invalid method."}, status=405)

# API ViewSet for AdminInventory using the serializer
class AdminInventoryViewSet(viewsets.ModelViewSet):
    queryset = AdminInventory.objects.all()
    serializer_class = AdminInventorySerializer

    @action(detail=False, methods=['get'])
    def search(self, request):
        search_query = request.GET.get('search', '')  # Get search term from the query string

        if search_query:
            # Try to filter by ID or name (case-insensitive)
            try:
                search_query_int = int(search_query)
                # Search by ID if the query is a valid integer
                products = AdminInventory.objects.filter(id=search_query_int)
            except ValueError:
                # If the search query is not an integer, search by name
                products = AdminInventory.objects.filter(name__icontains=search_query)
        else:
            # If no search term, return all products
            products = AdminInventory.objects.all()

        # Serialize the filtered products
        serialized_products = AdminInventorySerializer(products, many=True)
        return Response(serialized_products.data)

def checkout(request):
    if request.method == "POST":
        data = json.loads(request.body)
        cart = data.get("cart", [])
        payment_mode = data.get("payment_mode", "Cash")
        tracking_id = data.get("tracking_id", "")  # Ensure tracking_id is passed

        if not cart:
            return JsonResponse({"error": "Cart is empty!"}, status=400)

        if not tracking_id:
            return JsonResponse({"error": "Tracking ID is required!"}, status=400)

        try:
            # Fetch or create a Tracking instance
            tracking_instance, created = Tracking.objects.get_or_create(
                tracking_id=tracking_id,
                defaults={
                    "customer_email": request.session.get("user_email", ""),

                    "customer_phone": data.get("customer_phone", ""),
                    "customer_address": data.get("customer_address", ""),
                    "total_price": sum(item["price"] * item["quantity"] for item in cart),
                    "payment_method": payment_mode
                }
            )

            # Generate a unique Transaction ID
            transaction_id = f"TXN-{int(timezone.now().timestamp())}"

            total_price = sum(item["price"] * item["quantity"] for item in cart)

            # Create the Transaction and associate it with the Tracking instance
            transaction = Transaction.objects.create(
                transaction_id=transaction_id,
                tracking=tracking_instance,  # Link the transaction to the Tracking instance
                total_price=total_price,
                payment_mode=payment_mode
            )

            # Create Transaction Items
            for item in cart:
                TransactionItem.objects.create(
                    transaction=transaction,
                    product_id=item["id"],
                    product_name=item["name"],
                    quantity=item["quantity"],
                    price=item["price"],
                    total_price=item["price"] * item["quantity"]
                )

            # Return success response
            return JsonResponse({
                "message": "Transaction completed!",
                "transaction_id": transaction_id,
                "tracking_id": tracking_instance.tracking_id
            })
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)



import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def save_transaction(request):
    try:
        data = request.data
        cart_items = data.get('cart_items', [])
        tracking_id_from_payload = data.get('tracking_id')

        if not tracking_id_from_payload:
            return Response({"success": False, "message": "Missing tracking_id in the request"}, status=400)

        customer_email = request.session.get('user_email', '')

        customer_phone = data.get('customer_phone', '')
        customer_address = data.get('customer_address', '')
        total_price_tracking = data.get('total_price', '0.00')
        payment_method = data.get('payment_mode', '')

        tracking_instance, created = Tracking.objects.get_or_create(
            tracking_id=tracking_id_from_payload,
            defaults={
                'customer_email': customer_email,
                'customer_phone': customer_phone,
                'customer_address': customer_address,
                'total_price': total_price_tracking,
                'payment_method': payment_method,
                'status': 'Pending',  # ✅ Comma added here
                'source': 'pos'       # ✅ This is now valid
            }
        )

        logger.info(f"Tracking instance: {tracking_instance}, Created: {created}, ID: {tracking_instance.id if tracking_instance else None}")

        transaction = Transaction(
            tracking=tracking_instance,
            transaction_id=data['transaction_id'],
            total_price=data['total_price'],
            payment_mode=data['payment_mode'],
            date_time=localtime(now())
        )
        transaction.save()

        for item in cart_items:
            product_id = item.get('id')
            if product_id is None:
                return Response({"success": False, "message": "Missing product ID"}, status=400)

            try:
                product = AdminInventory.objects.get(id=product_id)
            except AdminInventory.DoesNotExist:
                return Response({"success": False, "message": f"Product with ID {product_id} not found"}, status=404)

            try:
                item_quantity = int(item['quantity'])
            except (ValueError, TypeError):
                return Response({"success": False, "message": f"Invalid quantity value for {product.get('name', 'Unknown')}"}, status=400)

            if item_quantity <= 0:
                return Response({"success": False, "message": f"Quantity must be greater than 0 for {product.name}"}, status=400)

            if product.stock >= item_quantity:
                product.stock -= item_quantity
                product.save()
            else:
                return Response({"success": False, "message": f"Not enough stock for {product.name}"}, status=400)

            TransactionItem.objects.create(
                transaction=transaction,
                product_id=product.id,
                product_name=product.name,
                quantity=item_quantity,
                price=float(item['price']),
                total_price=float(item['price']) * item_quantity
            )

        return Response({"success": True, "message": "Transaction saved successfully!"}, status=200)

    except Exception as e:
        logger.error(f"Error saving transaction: {e}")
        return Response({"success": False, "message": str(e)}, status=400)


@api_view(['GET'])
def get_transactions(request):
    transactions = Transaction.objects.filter(tracking__source='pos').order_by('-id')

    transaction_list = []

    for transaction in transactions:
        items = TransactionItem.objects.filter(transaction=transaction)
        item_details = [
            {
                "product_id": item.product_id,
                "product_name": item.product_name,
                "quantity": item.quantity,
                "price": item.price
            } 
            for item in items
        ]

        tracking_instance = transaction.tracking
        tracking_id = tracking_instance.tracking_id if tracking_instance else None

        transaction_list.append({
            "transaction_id": transaction.transaction_id,
            "timestamp": localtime(transaction.date_time).strftime('%m/%d/%Y - %H:%M:%S') if transaction.date_time else None,
            "total_price": transaction.total_price,
            "payment_mode": transaction.payment_mode,
            "tracking_id": tracking_id,
            "items": item_details
        })

    return Response(transaction_list, status=status.HTTP_200_OK)




@csrf_exempt
@csrf_exempt
def remove_transaction(request, transaction_id):
    try:
        # Find the transaction
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        tracking_instance = transaction.tracking  # Get the related Tracking instance
        transaction_items = TransactionItem.objects.filter(transaction=transaction)

        if not transaction_items.exists():
            return JsonResponse({"success": False, "message": "No items found for this transaction."})

        # Store transaction details in RemovedTransaction
        for item in transaction_items:
            RemovedTransaction.objects.create(
                original_transaction_id=transaction.transaction_id,
                date_time=transaction.date_time,
                product_id=item.product_id,
                product_name=item.product_name,
                product_price=item.price,
                quantity=item.quantity,
                total_price=item.total_price,
                payment_mode=transaction.payment_mode
            )

        # Delete transaction items first
        transaction_items.delete()
        # Then delete the transaction
        transaction.delete()

        return JsonResponse({"success": True, "message": "Transaction removed successfully."})

    except Transaction.DoesNotExist:
        return JsonResponse({"success": False, "message": "Transaction not found."})

@csrf_exempt
def remove_all_transactions(request):
    if request.method == "DELETE":
        Transaction.objects.all().delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)


def admin_pos_history(request):
    user_email = request.session.get('user_email')  # <-- new line added
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    return render(request, 'myApp/admin-pos-history.html', {
        'email': user_email,     # <-- new line added
        'username': username,    # <-- new line added
    })


def get_removed_transactions(request):
    transactions = RemovedTransaction.objects.all().values(
        "date_time",
        "original_transaction_id",
        "product_id",
        "product_name",
        "product_price",
        "quantity",
        "total_price",
        "payment_mode",
        "date_removed"
    )
    return JsonResponse({"transactions": list(transactions)})

def clear_removed_transactions(request):
    if request.method == "DELETE":
        RemovedTransaction.objects.all().delete()  # Delete all transactions
        return JsonResponse({"success": True, "message": "All transactions cleared."})

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)

def save_tracking(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received data:", data) # Log the entire received data

            customer_email = request.session.get('user_email')

            customer_phone = data.get('customer_phone')
            customer_address = data.get('customer_address')
            total_price = Decimal(data.get('total_price', '0.00'))
            shipping_subtotal = Decimal(data.get('shipping_subtotal', '0.00'))
            payment_method = data.get('payment_method')
            order_items = data.get('order_items', [])
            frontend_tracking_id = data.get('tracking_id')

            if not all([customer_email, customer_phone, customer_address, payment_method, frontend_tracking_id]):
                return JsonResponse({'error': 'Missing required order details or tracking ID.'}, status=400)

            # 1. Create the Tracking record
            tracking = Tracking.objects.create(
                customer_email=customer_email,
                customer_phone=customer_phone,
                customer_address=customer_address,
                total_price=total_price,
                shipping_subtotal=shipping_subtotal,
                payment_method=payment_method,
                status='Pending',
                tracking_id=frontend_tracking_id,
                source='ordering'  # ✅ differentiate it
            )
            print("Tracking record created:", tracking.tracking_id)

            # 2. Create a Transaction record linked to the Tracking record
            transaction = Transaction.objects.create(
                tracking=tracking,
                transaction_id=f"TRN-{tracking.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                total_price=total_price,
                payment_mode=payment_method
            )
            print("Transaction record created:", transaction.transaction_id)

            # 3. Create TransactionItem records for each item in order_items
            print("Order items received:", order_items) # Log the order_items

            for item_data in order_items:
                print("Processing item:", item_data) # Log each item data
                price = Decimal(item_data.get('price', '0.00'))
                quantity = item_data.get('quantity', 0)
                TransactionItem.objects.create(
                    transaction=transaction,
                    product_name=item_data.get('name'),
                    price=price,
                    quantity=quantity,
                    total_price=price * quantity,
                    image=item_data.get('image', '')
                )
                print("TransactionItem created for:", item_data.get('name'))

            return JsonResponse({'message': 'Order saved successfully!', 'tracking_id': tracking.tracking_id}, status=201)

        except json.JSONDecodeError as e:
            print("JSONDecodeError:", e)
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except ValidationError as e:
            print("ValidationError:", e)
            return JsonResponse({'error': e.message_dict}, status=400)
        except Exception as e:
            print("Exception during save:", e)
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

def get_tracking(request):
    user_email = request.session.get('user_email')

    if user_email and user_email.endswith('@admin.com'):
        # Admin sees all ordering-based transactions only
        orders = Tracking.objects.prefetch_related('transactions__items').filter(source='ordering')
    else:
        # Regular users see only their own orders
        orders = Tracking.objects.prefetch_related('transactions__items').filter(
            customer_email=user_email, source='ordering'
        )

    order_data = []
    for order in orders:
        items_data = []
        for transaction in order.transactions.all():
            for item in transaction.items.all():
                items_data.append({
                    'name': item.product_name,
                    'price': str(item.price),
                    'quantity': item.quantity,
                })

        order_data.append({
            'id': order.id,
            'customer_email': order.customer_email,
            'customer_phone': order.customer_phone,
            'customer_address': order.customer_address,
            'total_price': str(order.total_price),
            'shipping_subtotal': str(order.shipping_subtotal),
            'payment_method': order.payment_method,
            'status': order.status,
            'created_at': order.created_at.isoformat() + 'Z',
            'products': items_data,
        })

    return JsonResponse(order_data, safe=False)



def get_tracking_orders(request):
    orders = Tracking.objects.all().values()
    return JsonResponse(list(orders), safe=False)

def update_order_status(request, order_id):
    if request.method == "PATCH":
        try:
            order = get_object_or_404(Tracking, id=order_id)
            data = json.loads(request.body)
            new_status = data.get("status")
            previous_status = order.status

            if new_status:
                order.status = new_status
                order.save()

                # Deduct stock only if status is updated to "Delivered" or "Claimed" AND it wasn't before
                if new_status in ["Delivered", "Claimed"] and previous_status not in ["Delivered", "Claimed"]:
                    for transaction in order.transactions.all():
                        for item in transaction.items.all():
                            try:
                                product = AdminInventory.objects.get(name=item.product_name)
                                product.stock = max(product.stock - item.quantity, 0)  # avoid negative
                                product.save()
                            except AdminInventory.DoesNotExist:
                                continue  # product not found

                return JsonResponse({"message": "Status updated successfully", "status": order.status})
            else:
                return JsonResponse({"error": "Invalid status"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def delete_order(request, order_id):
    if request.method == "DELETE":
        try:
            order = Tracking.objects.get(id=order_id)  # ✅ Ensure using Tracking
            order.delete()
            return JsonResponse({"message": "Order deleted successfully"}, status=200)
        except Tracking.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)

def admin_inventory_transactions(request):
    transactions = StockInTransaction.objects.all().order_by('-date_time')  # Sort by date_time in descending order
    return render(request, 'myApp/admin-inventory-transactions.html', {'transactions': transactions})
    

def record_transaction(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        transaction = StockInTransaction.objects.create(
            transaction_id=data['transactionId'],
            date_time=data['dateTime'],
            admin_name=data['adminName'],
            supplier_name=data['supplier'],
            product_name=data['productName'],
            stocks_added=data['stocksAdded'],
            note=data['note']
        )
        return JsonResponse({'message': 'Transaction recorded successfully!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def delete_transactions(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            transaction_ids = data.get('transaction_ids', [])
            
            # Delete selected transactions from the database
            StockInTransaction.objects.filter(transaction_id__in=transaction_ids).delete()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    
    return JsonResponse({"success": False, "error": "Invalid request"})

def admin_purchasing_order(request):
    if request.method == 'POST':
        supplier = request.POST.get('supplier')
        contact_person = request.POST.get('contact_person')
        contact_number = request.POST.get('contact_number')
        product_name = request.POST.get('product_name')
        cost_price = request.POST.get('cost_price')
        quantity = request.POST.get('quantity')
        total_purchase_cost = request.POST.get('total_purchase_cost')
        payment_status = request.POST.get('payment_status')
        payment_method = request.POST.get('payment_method')

        purchase_order = PurchaseOrder(
            supplier=supplier,
            contact_person=contact_person,
            contact_number=contact_number,
            product_name=product_name,
            cost_price=cost_price,
            quantity_ordered=quantity,
            total_purchase_cost=total_purchase_cost,
            payment_status=payment_status,
            payment_method=payment_method
        )
        purchase_order.save()
        return JsonResponse({'message': 'Purchase order created successfully!'})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def admin_purchasing_logs(request):
    user_email = request.session.get('user_email')  # <-- new line added
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    logs = APLogs.objects.all().order_by('-removed_at')
    return render(request, 'myApp/admin-purchasing-logs.html', {
        'logs': logs,
        'email': user_email,     # <-- new line added
        'username': username,    # <-- new line added
    })


@api_view(["DELETE"])
def delete_tracking(request, pk):
    tracking = get_object_or_404(Tracking, pk=pk)

    deleted_tracking = DeletedTracking.objects.create(
        original_id=tracking.id,
        customer_email=tracking.customer_email,
        customer_phone=tracking.customer_phone,
        customer_address=tracking.customer_address,
        total_price=tracking.total_price,
        shipping_subtotal=tracking.shipping_subtotal,
        payment_method=tracking.payment_method,
        status=tracking.status
    )

    for transaction in tracking.transactions.all():
        for item in transaction.items.all():
            DeletedTrackingItem.objects.create(
                tracking=deleted_tracking,
                product_name=item.product_name,
                price=item.price,
                quantity=item.quantity
            )

    tracking.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



def admin_ordering_logs(request):
    user_email = request.session.get('user_email')  # <-- new line added
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    logs = DeletedTracking.objects.all().order_by('-deleted_at')
    return render(request, 'myApp/admin-ordering-logs.html', {
        'logs': logs,
        'email': user_email,     # <-- new line added
        'username': username,    # <-- new line added
    })



def admin_purchasing_list_json(request):
    purchase_orders = PurchaseOrder.objects.all().order_by('-purchase_datetime')
    data = [
        {
            'id': po.id,
            'po_id': po.po_id,
            'purchase_datetime': po.purchase_datetime.isoformat(),
            'supplier': po.supplier,
            'contact_person': po.contact_person,
            'contact_number': po.contact_number,
            'product_name': po.product_name,
            'cost_price': str(po.cost_price),
            'quantity_ordered': po.quantity_ordered,
            'total_purchase_cost': str(po.total_purchase_cost),
            'payment_status': po.payment_status,
            'payment_method': po.payment_method,
            'order_status': po.order_status,
        }
        for po in purchase_orders
    ]
    return JsonResponse(data, safe=False)

from .models import AdminInventory, PurchaseOrder
from django.http import JsonResponse

def admin_purchasing_update_status(request, order_id=None):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id_to_update = data.get('order_id')
            new_status = data.get('order_status')

            if not order_id_to_update or not new_status:
                return JsonResponse({'error': 'Missing order ID or new status.'}, status=400)

            purchase_order = get_object_or_404(PurchaseOrder, id=order_id_to_update)
            old_status = purchase_order.order_status
            purchase_order.order_status = new_status
            purchase_order.save()

            # ✅ If Payment is Paid and Order is Completed
            if purchase_order.payment_status == "Paid" and new_status == "Completed" and old_status != "Completed":
                product_name = purchase_order.product_name
                quantity = purchase_order.quantity_ordered

                try:
                    product = AdminInventory.objects.get(name=product_name)
                    product.stock += quantity
                    product.save()

                    return JsonResponse({
                        'message': f'{quantity} stocks have been successfully added to {product_name}.',
                        'updated_stock': product.stock
                    })
                except AdminInventory.DoesNotExist:
                    return JsonResponse({'error': f'Product "{product_name}" not found in inventory.'}, status=404)

            return JsonResponse({'message': f'Order {purchase_order.po_id} status updated to {new_status}.'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def admin_purchasing_update_payment_status(request, order_id=None):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id_to_update = data.get('order_id')
            new_payment_status = data.get('payment_status')

            if not order_id_to_update or not new_payment_status:
                return JsonResponse({'error': 'Missing order ID or new payment status.'}, status=400)

            purchase_order = get_object_or_404(PurchaseOrder, id=order_id_to_update)
            purchase_order.payment_status = new_payment_status
            purchase_order.save()
            return JsonResponse({'message': f'Order {purchase_order.po_id} payment status updated to {new_payment_status}.'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except PurchaseOrder.DoesNotExist:
            return JsonResponse({'error': f'Purchase order with ID {order_id_to_update} not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def user_ordering_logs(request):
    user_email = request.session.get('user_email', 'Guest')
    username = user_email.split('@')[0] if '@' in user_email else user_email

    utlogs = UTlogs.objects.prefetch_related('items').filter(customer_email=user_email).order_by('-removed_at')

    return render(request, 'myApp/user-ordering-logs.html', {
        'utlogs': utlogs,
        'email': user_email,
        'username': username,
    })


def user_booking(request):
    user_email = request.session.get('user_email', 'Guest')
    bookings = Booking.objects.filter(customer_email=user_email).order_by('-booked_at')
    username = user_email.split('@')[0] if '@' in user_email else user_email
    
    return render(request, 'myApp/user-booking.html', {
        'bookings': bookings,
        'email': user_email,
        'username': username,
    })



@csrf_exempt
def save_booking(request):
    if request.method == 'POST':
        try:
            user_email = request.session.get('user_email')
            if not user_email:
                return JsonResponse({'error': 'User not logged in'}, status=403)

            booking_date = request.POST.get('bookingDate')
            people_count = request.POST.get('peopleCount')
            estimated_time = request.POST.get('estimatedTime')

            if not all([booking_date, people_count, estimated_time]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            Booking.objects.create(
                customer_email=user_email,
                booking_date=booking_date,
                people_count=people_count,
                estimated_time=estimated_time,
                booked_at=timezone.now()
            )

            return JsonResponse({'success': True})
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



def cancel_booking(request):
    if request.method == 'POST':
        booking_id = request.POST.get('bookingId')
        try:
            booking = Booking.objects.get(pk=booking_id)
            booking.status = 'Cancelled'
            booking.save()
            return JsonResponse({'success': True})
        except Booking.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Booking not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def remove_booking(request):
    if request.method == 'POST':
        booking_id = request.POST.get('bookingId')  # ID from body
        try:
            booking = Booking.objects.get(id=booking_id)

            # Log it in ABlog before deleting
            ABlog.objects.create(
                booking_id=booking.id,
                customer_email=booking.customer_email,
                date=booking.booking_date,
                people=booking.people_count,
                estimated_arrival_time=booking.estimated_time,
                booked_at=booking.booked_at,
                status=booking.status
            )

            booking.delete()
            return JsonResponse({'success': True})
        except Booking.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Booking not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})



        
@csrf_exempt
def delete_purchasing_transactions(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ids = data.get('ids', [])
        PurchaseOrder.objects.filter(id__in=ids).delete()
        return JsonResponse({'message': 'Deleted successfully.'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def approve_booking(request):
    if request.method == 'POST':
        booking_id = request.POST.get('bookingId')
        booking = get_object_or_404(Booking, id=booking_id)
        if booking.status == 'Pending':
            booking.status = 'Approved'
            booking.save()
            return JsonResponse({'success': True, 'new_status': booking.status})
        else:
            return JsonResponse({'success': False, 'error': 'Booking cannot be approved from its current status.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def seat_booking(request):
    if request.method == 'POST':
        booking_id = request.POST.get('bookingId')
        booking = get_object_or_404(Booking, id=booking_id)
        if booking.status == 'Approved':
            booking.status = 'In-Session'
            booking.save()
            return JsonResponse({'success': True, 'new_status': booking.status})
        else:
            return JsonResponse({'success': False, 'error': 'Booking cannot be seated from its current status.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def complete_booking(request):
    if request.method == 'POST':
        booking_id = request.POST.get('bookingId')
        booking = get_object_or_404(Booking, id=booking_id)
        if booking.status == 'In-Session':
            booking.status = 'Completed'
            booking.save()
            return JsonResponse({'success': True, 'new_status': booking.status})
        else:
            return JsonResponse({'success': False, 'error': 'Booking cannot be completed from its current status.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def cancel_booking_admin(request, booking_id):
    ...

    if request.method == 'POST':
        booking_id = request.POST.get('bookingId')
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = 'Cancelled'
        booking.save()
        return JsonResponse({'success': True, 'new_status': booking.status})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def undo_booking(request):
    if request.method == 'POST':
        booking_id = request.POST.get('bookingId')
        booking = get_object_or_404(Booking, id=booking_id)

        if booking.status == 'Approved':
            booking.status = 'Pending'
        elif booking.status == 'In-Session':
            booking.status = 'Approved'
        elif booking.status == 'Completed':
            booking.status = 'In-Session'
        # You might want to define what "undoing" a cancellation means.
        # For now, we'll leave it as is, meaning you can't undo a cancellation with this logic.
        elif booking.status == 'Cancelled':
            return JsonResponse({'success': False, 'error': 'Cannot undo a cancelled booking with this logic.'})
        else:
            return JsonResponse({'success': False, 'error': 'No previous action to undo from the current status.'})

        booking.save()
        return JsonResponse({'success': True, 'new_status': booking.status})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def admin_booking_counts(request):
    from .models import Booking
    total = Booking.objects.count()
    pending = Booking.objects.filter(status='Pending').count()
    approved = Booking.objects.filter(status='Approved').count()
    in_session = Booking.objects.filter(status='In-Session').count()
    completed = Booking.objects.filter(status='Completed').count()
    cancelled = Booking.objects.filter(status='Cancelled').count()
    return JsonResponse({
        'total': total,
        'pending': pending,
        'approved': approved,
        'in_session': in_session,
        'completed': completed,
        'cancelled': cancelled,
    })

def confirm_booking(request):
    if request.method == 'POST':
        booking_id = request.POST.get('bookingId')
        try:
            booking = get_object_or_404(Booking, pk=booking_id)
            booking.status = 'Approved'  # Changed to 'Approved' as per your tracker logic
            booking.save()
            return JsonResponse({'success': True, 'new_status': booking.status})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def booking_updates(request):
    bookings = Booking.objects.all()  # Adjust based on your query
    booking_data = [{
        'id': booking.id,
        'status': booking.status
    } for booking in bookings]
    
    return JsonResponse({'success': True, 'bookings': booking_data})

def admin_booking_logs(request):
    user_email = request.session.get('user_email')  # <-- new line added
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    # Fetch all the removed bookings (ABlogs)
    ablogs = ABlog.objects.all().order_by('-removed_at')

    # Render the page with context data
    return render(request, 'myApp/admin-booking-logs.html', {
        'ablogs': ablogs,
        'email': user_email,     # <-- new line added
        'username': username,    # <-- new line added
    })


def delete_booking(request):
    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        try:
            booking = Booking.objects.get(id=booking_id)
            booking.delete()
            return JsonResponse({"success": True})
        except Booking.DoesNotExist:
            return JsonResponse({"success": False, "error": "Booking not found"})
        

def user_booking_logs(request):
    """Display removed bookings (logs)."""
    user_email = request.session.get('user_email')
    username = user_email.split('@')[0] if '@' in user_email else user_email  # <-- new line added

    logs = UBlog.objects.filter(customer_email=user_email)  # <-- changed to use user_email variable

    return render(request, 'myApp/user-booking-logs.html', {
        'logs': logs,
        'email': user_email,      # <-- new line added
        'username': username,     # <-- new line added
    })
       

def delete_purchasing_transactions(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ids = data.get("ids", [])

            for transaction_id in ids:
                try:
                    purchase = PurchaseOrder.objects.get(id=transaction_id)

                    # Log the data in APLogs before deleting
                    APLogs.objects.create(
                        purchase_datetime=purchase.purchase_datetime,
                        po_id=purchase.po_id,
                        supplier=purchase.supplier,
                        contact_person=purchase.contact_person,
                        contact_number=purchase.contact_number,
                        product_name=purchase.product_name,
                        cost_price=purchase.cost_price,
                        quantity_ordered=purchase.quantity_ordered,
                        total_purchase_cost=purchase.total_purchase_cost,
                        payment_status=purchase.payment_status,
                        payment_method=purchase.payment_method,
                        order_status=purchase.order_status,
                        removed_at=timezone.now()
                    )

                    # Delete from original model
                    purchase.delete()

                except PurchaseOrder.DoesNotExist:
                    continue  # Skip missing records

            return JsonResponse({"status": "success", "message": "Transactions removed and logged."})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)


def user_remove_booking(request, booking_id):
    try:
        # Get the booking to remove
        booking = Booking.objects.get(id=booking_id)
        
        # Create an ABlog entry with the booking details
        UBlog_entry = UBlog(
            booking_id=booking.id,  # Use .id instead of .booking_id
            customer_email=booking.customer_email,  # Changed from booking.name
            date=booking.booking_date,  # Changed from booking.date
            people=booking.people_count,  # Changed from booking.people
            estimated_arrival_time=booking.estimated_time,  # Changed from booking.estimated_arrival_time
            status=booking.status,
            booked_at=booking.booked_at
        )
        UBlog_entry.save()

        # Remove the booking from the Booking model
        booking.delete()

        # Redirect or render the logs page with success message
        return redirect('user_booking_logs')
    
    except Booking.DoesNotExist:
        # Handle case where booking doesn't exist
        return redirect('user_booking')

@api_view(["DELETE"])
def clear_orders(request, pk):
    # Retrieve the order by primary key (pk)
    tracking = get_object_or_404(Tracking, pk=pk)

    # Create a log entry in UT logs
    ut_log = UTlogs.objects.create(
        booking_id=tracking.tracking_id,
        customer_email=tracking.customer_email,
        phone_number=tracking.customer_phone,
        delivery_address=tracking.customer_address,
        total_price=tracking.total_price,
        shipping_subtotal=tracking.shipping_subtotal,
        mode_of_payment=tracking.payment_method,
        removed_at=timezone.now()  # Timestamp of removal
    )

    # Save each product in UTlogItem
    for transaction in tracking.transactions.all():
        for item in transaction.items.all():
            UTlogItem.objects.create(
                tracking=ut_log,
                product_name=item.product_name,
                price=item.price,
                quantity=item.quantity
            )

    # After archiving order to UT logs, we delete the order
    tracking.delete()

    return Response({"success": True, "message": "Order archived to UT logs and deleted."})

@csrf_exempt
def clear_bookings(request):
    if request.method == "POST":
        data = json.loads(request.body)
        booking_ids = data.get("booking_ids", [])

        try:
            UBlog.objects.filter(booking_id__in=booking_ids).delete()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    
    return JsonResponse({"success": False, "error": "Invalid request method"})


def check_logged_in(request):
    return 'access_token' in request.session

def some_view(request):
    if not check_logged_in(request):
        return redirect('login')
    # continue with logic


@api_view(['GET'])
def admin_get_all_orders(request):
    orders = Tracking.objects.prefetch_related('transactions__items').filter(source='ordering')


    order_data = []
    for order in orders:
        items_data = []
        for transaction in order.transactions.all():
            for item in transaction.items.all():
                items_data.append({
                    'name': item.product_name,
                    'price': str(item.price),
                    'quantity': item.quantity,
                })

        order_data.append({
            'id': order.id,
            'customer_email': order.customer_email,
            'customer_phone': order.customer_phone,
            'customer_address': order.customer_address,
            'total_price': str(order.total_price),
            'shipping_subtotal': str(order.shipping_subtotal),
            'payment_method': order.payment_method,
            'status': order.status,
            'created_at': order.created_at.isoformat() + 'Z',
            'products': items_data,
        })

    return JsonResponse(order_data, safe=False)

@csrf_exempt
def return_order(request, order_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            qty = int(data['return_quantity'])
            reason = data['reason']

            order = get_object_or_404(PurchaseOrder, id=order_id)
            if qty > order.quantity_ordered:
                return JsonResponse({'error': 'Quantity exceeds original order.'}, status=400)

            order.quantity_ordered -= qty
            order.total_purchase_cost = order.quantity_ordered * order.cost_price
            order.save()

            # optionally log this return in a ReturnLog model

            return JsonResponse({
                'message': 'Return recorded.',
                'new_quantity': order.quantity_ordered,
                'new_total': str(order.total_purchase_cost)
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def supplier_api(request):
    if request.method == "GET":
        suppliers = Supplier.objects.all()
        data = [
            {
                "id": s.id,
                "name": s.name,
                "contact_person": s.contact_person,
                "contact_number": s.contact_number,
            }
            for s in suppliers
        ]
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body)
            name = body.get("name")
            contact_person = body.get("contact_person")
            contact_number = body.get("contact_number")

            if not name or not contact_person or not contact_number:
                return JsonResponse({"error": "Missing required fields."}, status=400)

            supplier, created = Supplier.objects.get_or_create(
                name=name,
                defaults={
                    "contact_person": contact_person,
                    "contact_number": contact_number
                }
            )
            if not created:
                return JsonResponse({"error": "Supplier already exists."}, status=409)

            return JsonResponse({
                "id": supplier.id,
                "name": supplier.name,
                "contact_person": supplier.contact_person,
                "contact_number": supplier.contact_number
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON."}, status=400)




