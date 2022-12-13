import uuid
from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
# Create your models here.


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, default="", blank=True, null=True, allow_unicode=True)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class SubCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='sub_menu')
    slug = models.SlugField(unique=True, default="", blank=True, null=True)
    title = models.CharField(max_length=200)
    is_hide = models.BooleanField(default=True)
    description = RichTextField(blank=True, null=True, default="")
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(SubCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['create']

class Filter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, default="", blank=True, null=True)
    sub_cate = models.ManyToManyField(SubCategory, related_name='list_filter', default="", blank=True)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Filter, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    address = models.CharField(max_length=200)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AgentPrice(models.Model):
    profile = models.ForeignKey(Profile, blank=True, null=True, on_delete=models.CASCADE, default="")
    slug = models.SlugField(unique=False, default="", blank=True, null=True)
    rate_discount = models.FloatField(default=0)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f'{self.profile} - {self.slug} - {self.rate_discount}'

class Discount(models.Model):
    profile = models.ForeignKey(Profile, blank=True, null=True, on_delete=models.CASCADE)
    price_range = models.ForeignKey(SubCategory, blank=True, null=True, on_delete=models.CASCADE)
    rate = models.FloatField(default=0)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.profile} - {self.price_range} - {self.rate}'

class NumberPhone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number_display = models.CharField(max_length=20, default="", blank=True, null=True)
    number = models.CharField(max_length=10, unique=True)
    price = models.BigIntegerField(default=0)
    # discount = models.ForeignKey(Discount, on_delete=models.CASCADE, null=True, blank=True)
    # brand = models.CharField(max_length=50, default="")
    ower = models.ForeignKey(Profile, related_name='profile', on_delete=models.CASCADE)
    category = models.ManyToManyField(SubCategory, related_name="sub_category")
    discount = models.IntegerField(default=0)
    is_priority = models.BooleanField(default=False)
    is_stock = models.BooleanField(default=True)
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.number

    # def price_discount_ower(self):
    #     try:
    #         cate = self.category.get(menu__slug="sim-theo-gia")
    #         discount = Discount.objects.get(profile=self.ower, price_range=cate)
    #         price_discount = self.price * (100-discount.rate)
    #         return price_discount
    #     except:
    #         pass

    def agent_price(self):
        try:
            agents = AgentPrice.objects.filter(profile=self.ower)
            for rate in agents:
                [min_price, max_price] = rate.slug.split('-')
                if self.price >= int(min_price) and self.price < int(max_price):
                    return self.price * (1-rate.rate_discount)
        except Exception:
            pass
        

    def price_discount(self):
        price_discount = self.price * (1-(self.discount/100))
        return price_discount

    def get_format(self):
        try:
            cate = self.category.filter(menu__slug="kieu-so-dep").first()
            return cate.title
        except:
            pass

    def get_brand(self):
        try:
            cate = self.category.get(menu__slug="so-dien-thoai")
            return cate.title
        except:
            pass 

class Customer (models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # number_phone = models.ForeignKey(NumberPhone, related_name='customer', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    contact = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.full_name} - {self.contact}'

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='order')
    phone = models.OneToOneField(NumberPhone, on_delete=models.CASCADE)
    price = models.BigIntegerField(default=0)
    coupon = models.CharField(default='', blank=True, null=True, max_length=20)
    note = models.TextField(blank=True, null=True)
    is_finish = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.customer} - {self.phone}'
    
    class Meta:
        ordering = ['-update_at']

class NewsPost(models.Model):
    slug = models.SlugField(unique=True, default="", blank=True, null=True)
    title = models.CharField(max_length=200)
    description = RichTextField()
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Infor(models.Model):
    slug = models.SlugField(unique=True, default="", blank=True, null=True)
    title = models.CharField(max_length=200)
    description = RichTextField()
    create = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Posts(models.Model):
    slug = models.SlugField(unique=True, default="", blank=True, null=True, max_length=200)
    title = models.CharField(max_length=200)
    short_des = models.TextField()
    description = RichTextField()
    img = models.ImageField(upload_to='post/images/', blank=True)
    is_public = models.BooleanField(default=True)
    create = models.DateField(auto_now_add=True)
    update = models.DateField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug :
            self.slug = slugify(self.title)
        super(Posts, self).save(*args, **kwargs)
