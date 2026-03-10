"""
Smart Agriculture Assistant - Django Models
Marketplace connecting farmers with buyers
"""

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ("farmer", "Farmer"),
        ("buyer", "Buyer"),
        ("agronomist", "Agronomist"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="farmer")
    location = models.CharField(max_length=200, blank=True)
    farm_size_hectares = models.FloatField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.TextField(blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Crop(models.Model):
    CROP_TYPES = [
        ("wheat", "Wheat"),
        ("rice", "Rice"),
        ("corn", "Corn"),
        ("soybean", "Soybean"),
        ("cotton", "Cotton"),
        ("sugarcane", "Sugarcane"),
        ("tomato", "Tomato"),
        ("potato", "Potato"),
        ("onion", "Onion"),
        ("other", "Other"),
    ]
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="crops")
    crop_type = models.CharField(max_length=50, choices=CROP_TYPES)
    variety = models.CharField(max_length=100, blank=True)
    field_name = models.CharField(max_length=100)
    area_hectares = models.FloatField()
    planting_date = models.DateField()
    expected_harvest = models.DateField(null=True, blank=True)
    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    soil_type = models.CharField(max_length=100, blank=True)
    irrigation_type = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.farmer.username} - {self.crop_type} ({self.field_name})"


class YieldPrediction(models.Model):
    """ML Pipeline result — TensorFlow + Pandas"""

    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name="predictions")
    predicted_yield_tons = models.FloatField()
    confidence_score = models.FloatField()  # 0.0 - 1.0
    model_version = models.CharField(max_length=20, default="v1.0")
    input_features = models.JSONField(default=dict)  # Stores Pandas-processed features
    feature_importance = models.JSONField(default=dict)  # What drove the prediction
    weather_data = models.JSONField(default=dict)
    recommendations = models.JSONField(default=list)
    predicted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-predicted_at"]

    def __str__(self):
        return f"{self.crop} → {self.predicted_yield_tons:.1f}t (conf: {self.confidence_score:.0%})"


class DiseaseDetection(models.Model):
    """Computer Vision — OpenCV real-time crop disease detection"""

    SEVERITY_CHOICES = [
        ("none", "None"),
        ("mild", "Mild"),
        ("moderate", "Moderate"),
        ("severe", "Severe"),
        ("critical", "Critical"),
    ]
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name="disease_scans")
    image = models.ImageField(upload_to="crop_scans/")
    detected_diseases = models.JSONField(default=list)  # List of {name, confidence, bbox}
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default="none")
    affected_area_percent = models.FloatField(default=0)
    treatment_recommendations = models.JSONField(default=list)
    opencv_metadata = models.JSONField(default=dict)  # Contour counts, color histograms, etc.
    scanned_at = models.DateTimeField(auto_now_add=True)
    reviewed_by_expert = models.BooleanField(default=False)

    class Meta:
        ordering = ["-scanned_at"]

    def __str__(self):
        diseases = ", ".join([d["name"] for d in self.detected_diseases]) or "None"
        return f"{self.crop} - {diseases} ({self.severity})"


class Listing(models.Model):
    """Marketplace listing by farmer"""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("sold", "Sold"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    crop = models.ForeignKey(Crop, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    crop_type = models.CharField(max_length=50)
    quantity_tons = models.FloatField()
    price_per_ton = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    harvest_date = models.DateField(null=True, blank=True)
    available_from = models.DateField(default=timezone.now)
    available_until = models.DateField(null=True, blank=True)
    quality_grade = models.CharField(max_length=10, blank=True)
    certifications = models.JSONField(default=list)  # ['organic', 'fair-trade', ...]
    description = models.TextField(blank=True)
    images = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    views_count = models.IntegerField(default=0)
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} — {self.quantity_tons}t @ {self.currency}{self.price_per_ton}/t"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("disputed", "Disputed"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT, related_name="orders")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchases")
    quantity_tons = models.FloatField()
    agreed_price_per_ton = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    delivery_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    placed_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} — {self.buyer.username} buys {self.quantity_tons}t"


class WeatherData(models.Model):
    """External weather API cache for ML features"""

    location_lat = models.FloatField()
    location_lng = models.FloatField()
    date = models.DateField()
    temperature_min = models.FloatField()
    temperature_max = models.FloatField()
    rainfall_mm = models.FloatField()
    humidity_percent = models.FloatField()
    wind_speed_kmh = models.FloatField()
    solar_radiation = models.FloatField(null=True, blank=True)
    raw_data = models.JSONField(default=dict)
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["location_lat", "location_lng", "date"]
