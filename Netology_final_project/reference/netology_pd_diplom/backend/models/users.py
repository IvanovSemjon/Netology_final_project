"""Модели относящиеся к пользователям"""
from typing import Any, Optional
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Управление пользователями"""

    use_in_migrations = True

    def _create_user(self, email: str, password: Optional[str], **extra_fields: Any):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email.strip().lower())
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: Optional[str] = None, **extra_fields: Any):
        """Создать обычного пользователя"""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields: Any):
        """Создать супер-пользователя"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Модель пользователя системы.

    Расширяет стандартную модель Django для поддержки типов пользователей
    (покупатель/магазин) и функций восстановления пароля.
    """
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    email = models.EmailField(_("email address"), unique=True)
    company = models.CharField(_("company"), max_length=40, blank=True)
    position = models.CharField(_("position"), max_length=40, blank=True)

    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        validators=[username_validator],
        blank=True,
        null=True,
        help_text=_("150 characters or fewer."),
    )

    is_active = models.BooleanField(_("active"), default=False)
    USER_TYPE_CHOICES = (("shop", "Магазин"), ("buyer", "Покупатель"))
    type = models.CharField(_("type"), max_length=10, choices=USER_TYPE_CHOICES, default="buyer")

    password_reset_token = models.UUIDField(_("password reset token"), null=True, blank=True)
    password_reset_expires = models.DateTimeField(_("expires at"), null=True, blank=True)

    class Meta:
        """Метаданные модели User"""
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        ordering = ("email",)
        indexes = [
            models.Index(fields=["type"]),
            models.Index(fields=["is_active"])
            ]


    def __str__(self) -> str:
        """Строковое представление модели User"""
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or self.email

class Contact(models.Model):
    """
    Контактная информация пользователя: адрес, телефон.
    """
    CONTACT_TYPE_CHOICES = (
        ('phone', _('Телефон')),
        ('address', _('Адрес')),
    )

    user = models.ForeignKey(
        User,
        verbose_name=_("user"),
        related_name="contacts",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    type = models.CharField(_('type'), max_length=10, choices=CONTACT_TYPE_CHOICES, default='address')

    city = models.CharField(_("city"), max_length=50)
    street = models.CharField(_("street"), max_length=100)
    house = models.CharField(_("house"), max_length=15, blank=True)
    structure = models.CharField(_("structure"), max_length=15, blank=True)
    building = models.CharField(_("building"), max_length=15, blank=True)
    apartment = models.CharField(_("apartment"), max_length=15, blank=True)
    phone = models.CharField(_("phone"), max_length=20)

    class Meta:
        verbose_name = _("Контакт")
        verbose_name_plural = _("Контакты")

    def clean(self):
        """Валидация количества контактов"""
        from django.core.exceptions import ValidationError
        if self.type == 'phone':
            # Максимум 1 телефон
            existing_phones = Contact.objects.filter(user=self.user, type='phone')
            if self.pk:
                existing_phones = existing_phones.exclude(pk=self.pk)
            if existing_phones.exists():
                raise ValidationError(_('Можно добавить только один телефон'))
        elif self.type == 'address':
            # Максимум 5 адресов
            existing_addresses = Contact.objects.filter(user=self.user, type='address')
            if self.pk:
                existing_addresses = existing_addresses.exclude(pk=self.pk)
            if existing_addresses.count() >= 5:
                raise ValidationError(_('Можно добавить максимум 5 адресов'))

    def __str__(self):
        if self.type == 'phone':
            return f"Телефон: {self.phone}"
        base = f"{self.city}, {self.street}"
        if self.house:
            base += f" {self.house}"
        return base