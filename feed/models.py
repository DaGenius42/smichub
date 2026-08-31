# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django.conf import settings

def validate(value):
    if not value:
        return
    
    if not value.endswith('@bjsmicschool.com'):
        raise ValidationError(
            f'Use your school email address ending with @bjsmicschool.com to sign up.'
        )

class CustomUser(AbstractUser):
    username = models.CharField(
        _("username"),
        max_length=20,
        unique=True,
        help_text=_("Required. 20 characters or fewer. Letters, digits and @/./+/-/_ only."),
        validators=[UnicodeUsernameValidator()],
        error_messages={"unique": _("A user with that username already exists.")},
    )
    identity = models.CharField(max_length=20, choices=[("student", "Student"), ("teacher", "Teacher")], default="student")
    bio = models.TextField(blank=True, default="")
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    email = models.EmailField(
        unique=True,
        null=True,
        validators=[validate],
        help_text="Must end with @bjsmicschool.com"
    )

class Post(models.Model):
    CATEGORY_CHOICES = [
        ("question", "Question"),
        ("resource", "Resource"),
        ("project", "Project"),
        ("discussion", "Discussion"),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
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
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="liked_posts"
    )

    file_attached = models.FileField(upload_to='uploads/', blank=True, null=True)

    verified = models.BooleanField(default=True, help_text="post verified by admin")

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()

    def is_image(self):
        """True if the attached file is an image (so templates can preview it)."""
        if not self.file_attached:
            return False
        return self.file_attached.name.lower().endswith(
            ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg', '.avif')
        )

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
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="liked_news"
    )

    file_attached = models.FileField(upload_to='uploads/', blank=True, null=True)

    def like_count(self):
        return self.likes.count()

    def is_image(self):
        """True if the attached file is an image"""
        if not self.file_attached:
            return False
        return self.file_attached.name.lower().endswith(
            ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg', '.avif')
        )

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
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

class Vote(models.Model):
    body = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    voters = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='voted_votes'
    )
    def voters_count(self):
        return self.voters.count()

class Price(models.Model):
    name = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    for_which = models.CharField(max_length=100)#maybe we can add prices for other stuff in the future
    thumbs = models.ManyToManyField(
            settings.AUTH_USER_MODEL,
            blank=True,
            related_name='price_votes'
        )
    def thumbs_count(self):
        return self.thumbs.count()

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