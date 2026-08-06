from django.contrib.auth.models import User
from django.db import models


#ORM

class Post(models.Model):
    CATEGORY_CHOICES = [
        ("question", "Question"),
        ("resource", "Resource"),
        ("project", "Project"),
        ("discussion", "Discussion"),
    ]

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    title = models.CharField(max_length=120)
    body = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="discussion",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    likes = models.ManyToManyField(
        User,
        blank=True,
        related_name="liked_posts"
    )

    verified = models.BooleanField(default=False, help_text="post verified by admin")

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class News(models.Model):
    CATEGORY_CHOICES = [
        ("announcement", "Announcement"),
        ("school activities", "School Activities"),
        ("changes", "Changes"),
        ("reminder", "Reminder"),
    ]

    title = models.CharField(max_length=120)
    body = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="announcement",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    likes = models.ManyToManyField(
        User,
        blank=True,
        related_name="liked_news"
    )

    def like_count(self):
        return self.likes.count()
    
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class House(models.Model):
    name = models.CharField(max_length=50)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name}: {self.points} points"

class Comments(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
"""
==============================
Django Model Field Reference
All field types + explanation
==============================

---- Text Fields ----
models.CharField(max_length=N)
Short bounded text. Requires max_length. For names, titles.
models.TextField()
Unbounded long text. Posts, article bodies.
models.EmailField(max_length=254)
CharField with built-in email format validation.
models.URLField()
CharField validating proper web URLs.
models.SlugField()
URL-safe short text (for clean website URLs).
models.UUIDField()
Store UUID identifiers.

---- Numeric Fields ----
models.IntegerField()
Standard whole number: -2147483648 to 2147483647
models.PositiveIntegerField()
Integers ≥ 0
models.SmallIntegerField()
Small range integer: -32768 to 32767
models.PositiveSmallIntegerField()
Small integers ≥ 0
models.BigIntegerField()
Very large integer
models.FloatField()
Approximate floating-point number
models.DecimalField(max_digits, decimal_places)
Precise decimal arithmetic (currency, measurements)

---- Date & Time Fields ----
models.DateField()
Stores date only (YYYY-MM-DD)
models.TimeField()
Stores time only (HH:MM:SS)
models.DateTimeField()
Date + timestamp
auto_now_add=True → set once on creation
auto_now=True → update every save
models.DurationField()
Time interval/delta

---- Boolean & Choice Fields ----
models.BooleanField(default=False)
True / False
Usage pattern for dropdowns:
models.CharField(max_length=50, choices=[("key", "Label"),])

---- File / Media ----
models.FileField(upload_to="folder/")
Accept any file; store file path in database
models.ImageField(upload_to="images/")
Inherits FileField; validates image files (requires Pillow)

---- Relationship Fields ----
models.ForeignKey(Model, on_delete=..., related_name="...")
Many-to-one relationship
models.OneToOneField(Model, on_delete=...)
Strict one-to-one link (User ↔ Profile)
models.ManyToManyField(Model, blank=True)
Many-to-many automatic join table

---- Special Fields ----
models.JSONField()
Store raw lists / dictionaries in database
models.GenericIPAddressField()
IPv4 / IPv6 address validation
models.BinaryField()
Raw binary blob data (rarely used)

---- Common Field Arguments (works on most fields)
null=True      → allow NULL in database
blank=True     → allow empty input in forms/admin
default=X      → default value
unique=True    → enforce unique values
verbose_name=""→ human readable label
help_text=""   → helper text in admin
"""