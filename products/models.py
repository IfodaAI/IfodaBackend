from django.db import models
from utils.models import BaseModel
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

class DiseaseCategory(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title


class Disease(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    product = models.ManyToManyField("ProductSKU")
    category = models.ForeignKey(
        DiseaseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="diseases",
    )

    def __str__(self):
        return self.name


class ProductCategory(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title


    # Prevents model from being displayed as "Product categorys" in admin panel
    class Meta:
        verbose_name_plural = "Product categories"


class ProductSubcategory(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product_subcategories",
    )

    def __str__(self):
        return self.title
    
    # Prevents model from being displayed as "Product subcategorys" in admin panel
    class Meta:
        verbose_name_plural = "Product subcategories"


class Product(BaseModel):
    product_id = models.BigIntegerField(
        unique=True
    )  # This field is used to integrate with LOGIX system.
    name = models.CharField(max_length=50)
    description = models.TextField()
    spic = models.CharField(max_length=50)
    package_code = models.CharField(max_length=50)
    category = models.ForeignKey(
        ProductSubcategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    image_thumbnail = ProcessedImageField(upload_to='avatars',
                                        # processors=[ResizeToFill(100, 50)],
                                        format='JPEG',
                                        options={'quality': 60},
                                        blank=True,
                                        null=True
                                        )

    def __str__(self):
        return self.name

class ProductSKU(BaseModel):
    UNIT_CHOICES = [
        ("ml", "Milliliter"),
        ("l", "Liter"),
        ("g", "Gram"),
        ("kg", "Kilogram"),
    ]

    quantity = models.IntegerField()
    price = models.FloatField()
    unit = models.CharField(choices=UNIT_CHOICES)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product_skus",
    )

    def __str__(self):
        return f"{self.id} - {self.product}"
    
    @property
    def product_name(self):
        return f"{self.product.name} {self.quantity} {self.unit}"
    
    class Meta:
        verbose_name_plural = "Product SKUs"


class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="product_images",
    )
    image = models.ImageField(upload_to="product_images/")

    def __str__(self):
        return f"{self.product}'s image"
