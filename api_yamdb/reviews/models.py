from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.validators import EmailValidator
from django.db import models

from reviews.validators import validate_username, validate_year
from api_yamdb.settings import MAX_LENGTH, MAX_LENGTH_EMAIL


ADMIN = 'admin'
MODERATOR = 'moderator'
USER = 'user'


class NameSlugModel(models.Model):
    """Модель для Категории и Жанра."""

    name = models.CharField(
        max_length=256,
        verbose_name='Наименование'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Короткая метка'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name[:15]


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь'),
    ]
    username = models.CharField(
        max_length=MAX_LENGTH,
        unique=True,
        verbose_name='Логин пользователя',
        validators=[validate_username],
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH,
        null=True,
        blank=True,
        verbose_name='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH,
        null=True,
        blank=True,
        verbose_name='Фамилия пользователя'
    )
    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        validators=[EmailValidator]
    )
    confirmation_code = models.BigIntegerField(
        null=True,
    )
    role = models.CharField(
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль пользователя'
    )
    bio = models.TextField(
        null=True,
        blank=True,
        verbose_name='Биография пользователя'
    )
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='email_user_unique',
                fields=['email', 'username'],
            ),
        ]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username[:15]

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == MODERATOR


class Category(NameSlugModel):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(NameSlugModel):
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.TextField(
        verbose_name='Название'
    )
    year = models.IntegerField(
        validators=[validate_year],
        verbose_name='Дата выхода'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        through='GenreTitle'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='titles',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:15]


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр произведения'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'

    def __str__(self):
        return f'Жанр у произведения "{self.title}": {self.genre}'


class TextAuthorPubDateModel(models.Model):
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        abstract = True
        default_related_name = '%(class)ss'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Review(TextAuthorPubDateModel):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    score = models.IntegerField(
        default=1,
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        ),
        error_messages={'Ошибка': 'Пожалуйста, поставьте оценку от 1 to 10'},
        verbose_name='Оценка'
    )

    class Meta(TextAuthorPubDateModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            )
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Comment(TextAuthorPubDateModel):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )

    class Meta(TextAuthorPubDateModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
