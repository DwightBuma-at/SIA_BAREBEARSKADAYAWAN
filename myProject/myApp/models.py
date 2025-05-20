from django.db import models
from django.conf import settings  # Import settings to access AUTH_USER_MODEL
from django.core.exceptions import ValidationError  # Import ValidationError
from django.contrib.auth.models import User
from uuid import uuid4
from django.utils import timezone

# Admin Inventory Model
class AdminInventory(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Fixed the missing part here
    stock = models.IntegerField()
    image = models.ImageField(upload_to='inventory_images/', null=True, blank=True)

    def __str__(self):
        return self.name


# Order Model
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Updated here to use AUTH_USER_MODEL
    product = models.ForeignKey(AdminInventory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return f"Order #{self.id} by {self.user.email}"  # Changed to use email instead of username

    def update_inventory(self):
        # Reduce the stock of the product when an order is placed
        product = self.product
        product.stock -= self.quantity
        product.save()


# Email Validation function
def validate_com_email(value):
    if not value.endswith('.com'):
        raise ValidationError('Email must end with ".com"')
    if '@' not in value:
        raise ValidationError('Email must contain "@" symbol')


# Custom User Model and Manager
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create a custom manager for your user model
class SignupManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("The Email field must be set")
        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# Custom user model extending AbstractBaseUser and PermissionsMixin
class Signup(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, validators=[validate_com_email])  # Added email validation
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Optional: For admin privileges
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    objects = SignupManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    def __str__(self):
        return self.email

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"Cart of {self.user.username}"

from django.db import models

class Tracking(models.Model):
    ORDER_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    tracking_id = models.TextField(unique=True)  # Removed max_length
    customer_email = models.EmailField()

    customer_phone = models.TextField()
    customer_address = models.TextField()

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=50)

    status = models.CharField(choices=ORDER_STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=20, default='ordering')  # 'pos' or 'ordering'


    def __str__(self):
        return f"{self.customer_email} - Order ID: {self.id} ({self.status})"




class Transaction(models.Model):
    tracking = models.ForeignKey(Tracking, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=100, unique=True)  # Increased from 20 to 100
    date_time = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(
        max_length=50,  # Increased max_length for more flexibility
        choices=[
            ('Cash', 'Cash'),
            ('Store Pick-up', 'Store Pick-up'),
            ('Cash On Delivery', 'Cash On Delivery'),  # Added option if needed
            ('Card Payment', 'Card Payment'),  # Future option if you want
        ]
    )

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.total_price} PHP (Tracking ID: {self.tracking.id})"


class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="items")
    product_id = models.CharField(max_length=20)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Add this field
    image = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.product_name} (x{self.quantity}) in Transaction {self.transaction.transaction_id}"
    
class RemovedTransaction(models.Model):
    original_transaction_id = models.CharField(max_length=20)  # Order ID
    date_time = models.DateTimeField()  # Original transaction date/time
    product_id = models.CharField(max_length=20)  # Product ID
    product_name = models.CharField(max_length=255)  # Product Name
    product_price = models.DecimalField(max_digits=10, decimal_places=2)  # Product Price
    quantity = models.IntegerField()  # Quantity
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_mode = models.CharField(max_length=20)  # Payment Mode
    date_removed = models.DateTimeField(auto_now_add=True)  # Removal Timestamp

    def __str__(self):
        return f"Removed Order {self.original_transaction_id} - {self.product_name}"    
    
    from django.db import models

class StockInTransaction(models.Model):
    transaction_id = models.CharField(max_length=50, unique=True)
    date_time = models.DateTimeField(auto_now_add=True)
    admin_name = models.CharField(max_length=100)
    supplier_name = models.CharField(max_length=100)
    product_name = models.CharField(max_length=100)
    stocks_added = models.IntegerField()
    note = models.TextField()

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.product_name}"    

class PurchaseOrder(models.Model):
    po_id = models.CharField(max_length=255, unique=True, default=None, null=True, blank=True)
    purchase_datetime = models.DateTimeField(default=timezone.now)
    supplier = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    product_name = models.CharField(max_length=255)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_ordered = models.IntegerField()
    total_purchase_cost = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('Unpaid', 'Unpaid'),
            ('Paid', 'Paid'),
            ('Partial', 'Partial'),
        ],
        default='Unpaid'
    )
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('Credit', 'Credit'),
            ('Cash', 'Cash'),
            ('Gcash', 'Gcash'),
            ('Cash on Delivery', 'Cash on Delivery'),
        ],
        default='Cash'
    )
    order_status = models.CharField(
        max_length=50,
        choices=[
            ('Unclaimed', 'Unclaimed'),
            ('Delivered', 'Delivered'),
            ('Cancelled', 'Cancelled'),
            ('Return to Supplier', 'Return to Supplier'),
            ('Checking', 'Checking'),
            ('Completed', 'Completed'),
        ],
        default='Unclaimed'
    )

    def __str__(self):
        return f"PO: {self.po_id} - {self.product_name} ({self.quantity_ordered})"

    def save(self, *args, **kwargs):
        if not self.po_id:
            timestamp = int(timezone.now().timestamp() * 1000)
            # Generate a more consistently unique random number
            random_num = int.from_bytes(timezone.now().isoformat().encode(), byteorder='big') % 1000
            self.po_id = f"PO{timestamp}{random_num:03d}"
        super().save(*args, **kwargs)  
    

class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('In-Session', 'In-Session'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    customer_email = models.EmailField()

    booking_date = models.DateField()
    people_count = models.IntegerField()
    estimated_time = models.TimeField()
    booked_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Booking for {self.customer_email} on {self.booking_date} - {self.status}"
    
from django.db import models

class APLogs(models.Model):
    purchase_datetime = models.DateTimeField()
    po_id = models.CharField(max_length=100)
    supplier = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=50)
    product_name = models.CharField(max_length=255)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_ordered = models.IntegerField()
    total_purchase_cost = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=50)
    order_status = models.CharField(max_length=50)
    removed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.po_id} - {self.supplier} (Removed {self.removed_at.strftime('%Y-%m-%d %H:%M')})"

class ABlog(models.Model):
    # Fields similar to Booking model, for logging purposes
    booking_id = models.IntegerField()
    customer_email = models.EmailField()

    date = models.DateField()
    people = models.IntegerField()
    estimated_arrival_time = models.TimeField()
    status = models.CharField(max_length=20)
    booked_at = models.DateTimeField()
    removed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Removed Booking {self.booking_id} - {self.name}"
    
class UBlog(models.Model):
    # Fields similar to Booking model, for logging purposes
    booking_id = models.IntegerField()
    customer_email = models.EmailField()

    date = models.DateField()
    people = models.IntegerField()
    estimated_arrival_time = models.TimeField()
    status = models.CharField(max_length=20)
    booked_at = models.DateTimeField()
    removed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Removed Booking {self.booking_id} - {self.name}"
    
class DeletedTracking(models.Model):
    original_id = models.IntegerField()
    customer_email = models.EmailField()

    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Deleted Order #{self.original_id}"

class DeletedTrackingItem(models.Model):
    tracking = models.ForeignKey(DeletedTracking, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()


class UTlogs(models.Model):
    booking_id = models.CharField(max_length=100)
    customer_email = models.EmailField()

    phone_number = models.CharField(max_length=50)
    delivery_address = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mode_of_payment = models.CharField(max_length=50)
    removed_at = models.DateTimeField(default=timezone.now)

class UTlogItem(models.Model):
    tracking = models.ForeignKey(UTlogs, on_delete=models.CASCADE, related_name="items")
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

class Supplier(models.Model):
    name = models.CharField(max_length=100, unique=True)
    contact_person = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name    
