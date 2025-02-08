from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

USER_TYPES = [
    ('company', 'Company'),
    ('transport', 'Transport'),
    ('admin', 'Admin'),
]

driver_status = [
    ('Free', 'Free'),
    ('Occupied', 'Occupied')
]

class Produit(models.Model):
    TYPE_CHOICES = [
        ('liquid', 'Liquid'),
        ('fragile', 'Fragile'),
        ('Box', 'Box'),
    ]
    amount = models.IntegerField()
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    height = models.FloatField()
    width = models.FloatField()
    weight = models.FloatField()
    company = models.ForeignKey("Auth.Company", verbose_name="Company", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.name} - {self.weight}kg"

class Company(models.Model):
    def __str__(self):
        return f"Company {self.id}"

class Drivers(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=50)
    license = models.ImageField(upload_to='images', null=True, blank=True)
    transport = models.ForeignKey("Auth.Transport", verbose_name="transports", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

class sharedtruckes(models.Model):
    status = models.CharField(choices=driver_status, max_length=50, default='Free')
    name = models.CharField(max_length=50)
    height = models.FloatField()
    width = models.FloatField()
    full = models.BooleanField(default=False)
    type = models.CharField(max_length=50)
    percentage = models.FloatField(default=0)
type_trucks=[
    ('Truck', 'Truck'),
    ('Van', 'Van'),
    ('Car', 'Car'),
]
class Truck(models.Model):
    status = models.CharField(choices=driver_status, max_length=50, default='Free')
    name = models.CharField(max_length=50)
    height = models.FloatField()
    width = models.FloatField()
    weight = models.FloatField()
    type = models.CharField(max_length=50,choices=type_trucks)
    full = models.BooleanField(default=False)
    percentage = models.FloatField(default=0)

    def __str__(self):
        return f"{self.name}"

class road(models.Model):
    name = models.CharField(max_length=50)
    begin = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    transport = models.ForeignKey("Auth.Transport", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

class Transport(models.Model):
    trucks = models.ManyToManyField(Truck, verbose_name="Trucks")
    shared_trucks = models.ManyToManyField(sharedtruckes, verbose_name="Shared Trucks")
    price_per_km = models.FloatField(null=True)
    price_per_day = models.FloatField(null=True)

    def __str__(self):
        return f"Transport with {self.trucks.count()} trucks"

class MyAccountManager(BaseUserManager):
    def create_user(self, email, name, user_type, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not name:
            raise ValueError("Users must have a username")
        if not user_type:
            raise ValueError("User must define a type")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            type=user_type
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(
            email=email,
            name=name,
            user_type='admin',
            password=password
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    number = models.IntegerField(null=True, blank=True)
    company = models.OneToOneField(Company, verbose_name="Company", null=True, blank=True, on_delete=models.SET_NULL, related_name="user")
    transport = models.OneToOneField(Transport, verbose_name="Transport", null=True, blank=True, on_delete=models.SET_NULL, related_name="user")
    type = models.CharField(choices=USER_TYPES, max_length=50)
    date_joined = models.DateField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    password = models.CharField(max_length=50)

    objects = MyAccountManager()

    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return self.is_superuser or super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        return True

class track(models.Model):
    destination = models.CharField(max_length=50)
    begin = models.CharField(max_length=50)
    date = models.CharField(max_length=50,null=True)
    truck= models.ForeignKey(Truck, on_delete=models.CASCADE, related_name='tracks',null=True)

class Feedback(models.Model):
    transporter = models.ForeignKey(Transport, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.CharField(max_length=255)
    rating = models.IntegerField()
    delivery_time = models.FloatField()
    success = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()

    def __str__(self):
        return f"Feedback for {self.transporter} by {self.user}"
