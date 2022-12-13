from rest_framework import serializers
from .models import Category, SubCategory, Filter, NumberPhone, Customer, NewsPost, Infor, Posts, Order, Discount


class CategorySmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']


class SubCategorySerializer(serializers.ModelSerializer):
    menu = CategorySmallSerializer()
    class Meta:
        model = SubCategory
        fields = ['id', 'title', 'slug', 'menu']


class CategorySerializer(serializers.ModelSerializer):
    sub_menu = SubCategorySerializer(many=True)

    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'sub_menu']


class NumberPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumberPhone
        fields = ['id', 'number', 'number_display', 'price', 'discount', 'price_discount', 'get_format', 'get_brand', 'is_stock']


class SubCategoryDetailSerializer(serializers.ModelSerializer):
    menu = CategorySmallSerializer()
    phones = serializers.SerializerMethodField()

    def get_phones(self, obj):
        print(obj.id)
        query = NumberPhone.objects.filter(category=obj.id)[:20]
        serializer = NumberPhoneSerializer(query, many=True)
        return serializer.data
    
    class Meta:
        model = SubCategory
        fields = ['id', 'title', 'slug', 'menu', 'phones']


class SubCategoryShortSerializer(serializers.ModelSerializer):    
    class Meta:
        model = SubCategory
        fields = ['id', 'title', 'slug', 'description', 'is_hide']


# class SubCategoryFullSerializer(serializers.ModelSerializer):
#     sub_category = NumberPhoneSerializer(many=True)
#     menu = CategorySmallSerializer()

#     class Meta:
#         model = SubCategory
#         fields = ['id', 'title', 'slug', 'menu', 'sub_category', 'description', 'discount', 'price_discount']

class OrderSerializer(serializers.ModelSerializer):
    phone = NumberPhoneSerializer()

    class Meta:
        model = Order
        fields = '__all__'


class CustomerOderSerializer(serializers.ModelSerializer):
    order = OrderSerializer(many=True)

    class Meta:
        model = Customer
        fields = ['full_name', 'contact', 'order']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['full_name', 'contact', 'address']


class PostListShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ['slug', 'title']


class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ['id', 'slug', 'title', 'short_des', 'img', 'update']


class PostRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = ['title', 'description', 'update']


class InforSerializer(serializers.ModelSerializer):
    class Meta:
        model = Infor
        fields = '__all__'


class NewsPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPost
        fields = '__all__'


