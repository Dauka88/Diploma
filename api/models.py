from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, validators=[RegexValidator(r'^\+?1?\d{9,15}$')])
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    social_id_card_number = models.CharField(max_length=20)
    is_social_id_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile of {self.user.username}"


class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Email verification for {self.user.username}"


class PhoneVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Phone verification for {self.user.username}"


class SocialIDVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    document = models.FileField(upload_to='social_id_documents/')
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Social ID verification for {self.user.username}"


class Apartment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    num_bedrooms = models.PositiveIntegerField()
    num_bathrooms = models.PositiveIntegerField()
    max_guests = models.PositiveIntegerField()
    size_sq_meters = models.DecimalField(max_digits=10, decimal_places=2)
    amenities = models.ManyToManyField('Amenity', related_name='apartments')
    main_image = models.ImageField(upload_to='apartment_images/')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='amenity_icons/')

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Calculate total price based on duration of stay and price per night
        self.total_price = (self.end_date - self.start_date).days * self.apartment.price_per_night
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.apartment.name} - {self.start_date} to {self.end_date}"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.apartment.name} - {self.user.username}"


class Photo(models.Model):
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='apartment_photos/')

    def __str__(self):
        return f"{self.apartment.name} - {self.image}"


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.booking.apartment.name} - {self.amount}"


class WishList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    apartments = models.ManyToManyField(Apartment, related_name='wishlist')

    def __str__(self):
        return f"Wishlist of {self.user.username}"