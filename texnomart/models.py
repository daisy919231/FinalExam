from django.db import models
from uuslug import uuslug
from django.contrib.auth.models import User

# Create your models here.

class BaseModel(models.Model):
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True


class Category(BaseModel):
    title=models.CharField(max_length=100, null=True, blank=True)
    image=models.ImageField(upload_to='categories/', null=True, blank=True)
    slug=models.SlugField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural='Categories'

    def __str__(self):
        return self.title

    def __unicode__(self):
         return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = uuslug(self.title, instance=self)
        super(Category, self).save(*args, **kwargs)

class Group(BaseModel):
    title=models.CharField(max_length=100, null=True, blank=True)
    image=models.ImageField(upload_to='categories/', null=True, blank=True)
    slug=models.SlugField(max_length=255, null=True, blank=True)
# Homepagedagi lar category emas, group ekan.
    category=models.ForeignKey(Category, on_delete=models.CASCADE, related_name='groups')

    def __str__(self):
        return self.title

    def __unicode__(self):
         return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = uuslug(self.title, instance=self)
        super(Group, self).save(*args, **kwargs)

class Brand(BaseModel):
    title=models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.title

class Product(BaseModel):
    title=models.CharField(max_length=100, null=True)
    price = models.FloatField(default=0)
    twelve_month_plan=models.FloatField(default=0)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0, null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='product_brands')
    # lekin aynan user bo'lish shart emas ekan, biror productni sevimlilarga qo'shish uchun, o'rniga ip adressni eslab qolyapti shekilli.
    is_liked = models.ManyToManyField(User, related_name='likes', null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True)

    @property
    def discount(self):
        return self.twelve_month_plan - self.price

    def __unicode__(self):
         return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = uuslug(self.title, instance=self)
        super(Product,self).save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    

class Image(models.Model):
     image=models.ImageField(upload_to='images/', null=True, blank=True)
     product=models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name='images')
     is_primary = models.BooleanField(default=False)

     def __str__(self):
            return self.image.url
     
class Customer(BaseModel):
    name=models.CharField(max_length=100, null=True)
    surname=models.CharField(max_length=100, null=True)
    phone_number=models.CharField(max_length=13, null=True)


class Location(models.Model):
    home_location=models.CharField(max_length=200, null=True, blank=True)
    pickup_location=models.CharField(max_length=200, null=True, blank=True)

class Order(BaseModel):
    interest_rate=71

    class DurationChoices(models.IntegerChoices):
        zero_percentage = 0
        twenty_four=24
    
    class ReceiveMethod(models.TextChoices):
        choice1='home delivery'
        choice2= 'get from market'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name='orders')
    quantity = models.PositiveIntegerField(default=1, null=True, blank=True)
    installment_plan = models.PositiveSmallIntegerField(choices=DurationChoices.choices, default=DurationChoices.zero_percentage.value, null=True, blank=True)
    receive_method = models.CharField(max_length=40, choices=ReceiveMethod.choices, default=ReceiveMethod.choice1)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='orders')


    @property
    def home_delivery(self):
        if self.receive_method==self.ReceiveMethod.choice1.value:
            return self.location.home_location if self.location.home_location else None
        return self.location.pickup_location if self.location.pickup_location else None

                                        
    @property
    def monthly_payment(self):
        if self.installment_plan == self.DurationChoices.zero_percentage.value:
            return round(self.product.twelve_month_plan / 12, 2) if self.product else 0
        return round(((self.product.price * (self.interest_rate+100)/100))/24, 2) if self.product else 0
    
    @property
    def total_payment(self):
        if self.receive_method==self.DurationChoices.twenty_four.value:
            return 1,71 * self.product.price if self.product else 0
        return self.product.twelve_month_plan if self.product else 0

    def __str__(self):
        return f'{self.product.name} - {self.user.username} - {self.quantity}'


class Rating(models.Model):
    class RatingChoices(models.IntegerChoices):
        zero = 0
        one = 1
        two = 2
        three = 3
        four = 4
        five = 5

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveIntegerField(choices=RatingChoices.choices, default=RatingChoices.zero.value)
    message = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='comments/', null=True, blank=True)

class RatingLike(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    rating=models.ForeignKey(Rating, on_delete=models.CASCADE, related_name='likes')
    is_liked=models.BooleanField(default=False)


class CharacteristicsKey(models.Model):
    key_name=models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
          return self.key_name

class CharacteristicsValue(models.Model):
    value_name=models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
          return self.value_name


class ProductCharacteristics(models.Model):
    char_key=models.ForeignKey(CharacteristicsKey, on_delete=models.CASCADE, null=True, blank=True)
    char_value=models.ForeignKey(CharacteristicsValue, on_delete=models.CASCADE, null=True, blank=True)
    product=models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='characteristics')

    class Meta:
         verbose_name_plural='ProductCharacteristics'

    def __str__(self):
          return f' {self.char_value.value_name} - {self.product.title} '




                          

