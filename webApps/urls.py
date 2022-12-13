from django.urls import path
from rest_framework import routers
from django.urls import path, include
from .views import CategoryList, SubCategoryList, FilterList, NumberPhoneList, CustomerSerializerList, NewSpostSerializerList, GetInfor, PostList

router = routers.DefaultRouter()
router.register('category', CategoryList, basename='category')
router.register('sub-cate', SubCategoryList, basename='sub-cate')
router.register('filter', FilterList, basename='filter')
router.register('number', NumberPhoneList, basename='number')
router.register('order', CustomerSerializerList, basename='order')
router.register('news', NewSpostSerializerList, basename='news')
router.register('infor', GetInfor, basename='infor')
router.register('posts', PostList, basename='post')


urlpatterns = [
    path('', include(router.urls)),
]