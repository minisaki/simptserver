from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.http import Http404
from rest_framework.response import Response
from django.db.models import Q
from .models import Category, SubCategory, Filter, NumberPhone, Customer, NewsPost, Infor, Posts, Order
from .serializers import CategorySerializer, SubCategorySerializer, SubCategoryDetailSerializer, \
    NumberPhoneSerializer, CustomerSerializer, InforSerializer, NewsPostSerializer, SubCategoryShortSerializer, \
    OrderSerializer, PostListSerializer, PostRetrieveSerializer, PostListShortSerializer, CustomerOderSerializer
# Create your views here.
import json


class CategoryList(viewsets.ViewSet):
    def list(self, request):
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)


class CustomPagination(PageNumberPagination):
    def __init__(self):
        self.page = 1
        self.display_page_controls = True
        self.request = ""
        self.page_current = ""

    def get_previous_page(self):
        if not self.page.has_previous():
            return None
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return 1
        return page_number

    def get_next_page(self):
        if not self.page.has_next():
            return None
        page_number = self.page.next_page_number()
        return page_number

    def paginate_queryset(self, queryset, request):
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            self.display_page_controls = True

        self.request = request
        self.page_current = page_number
        return list(self.page)

    def get_paginated_response(self, data, header):
        return Response({
            'header': header,
            'pageSize': f'{self.page_size}',
            'count': self.page.paginator.count,
            'num_pages': self.page.paginator.num_pages,
            'nextPage': self.get_next_page(),
            'prevPage': self.get_previous_page(),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'pageCurrent': self.page_current,
            'results': data,
        })


class SubCategoryList(viewsets.ViewSet):
    def list(self, request):
        try:
            queryset = SubCategory.objects.all()
            serializer = SubCategorySerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception:
            data = {
                'message': 'Lỗi yêu cầu tài nguyên'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        print(pk)
        try:
            params = request.GET.getlist('id')
            sub_cate = SubCategory.objects.get(slug=pk)
            serializer_subcate = SubCategoryShortSerializer(sub_cate)
            header = {
                'title': serializer_subcate.data['title'],
                'is_hide': serializer_subcate.data['is_hide'],
                'description': serializer_subcate.data['description']
            }
            queryset = sub_cate.sub_category.all().order_by('id')
            if params:
                # queryset = NumberPhone.objects.filter(category__id=pk)
                for param_id in params:
                    queryset = queryset.filter(category__id=param_id)
            # else:
                

            paginator = CustomPagination()
            page = paginator.paginate_queryset(queryset, request)
            if page is not None:
                serializer = NumberPhoneSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data, header)

            serializer = NumberPhoneSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception:
            data = {
                'message': 'Lỗi yêu cầu tài nguyên'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def get_list(self, request):
        try:
            query_filter = Filter.objects.get(slug="bo-loc-1")
            queryset = SubCategory.objects.filter(list_filter=query_filter)
            serializer = SubCategoryDetailSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            data = {
                'message': 'Lỗi yêu cầu tài nguyên'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class FilterList(viewsets.ViewSet):
    def list(self, request):
        try:
            queryset = Filter.objects.get(slug='bo-loc-2')
            sub_cate = SubCategory.objects.filter(list_filter=queryset)

            serializer = SubCategorySerializer(sub_cate, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            data = {
                'message': 'Lỗi yêu cầu tài nguyên'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class NumberPhoneList(viewsets.ViewSet):
    @action(detail=False, methods=['GET'])
    def filter_network(self, request):
        data = request.GET
        q_list = Q()
        for q in [Q(brand__iexact=n) for n in data.getlist('brand')]:
            q_list |= q
        try:
            queryset = NumberPhone.objects.filter(q_list)
            serializer = NumberPhoneSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            data = {
                'message': 'Lỗi yêu cầu tài nguyên'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        # return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def search(self, request):
        params = request.GET
        print(params)
        str_search = params['q'].replace('*', 'có đuôi ') if params["q"][0] == '*' else (
            f"đầu số {params['q'].replace('*', '')}")
        header = {}
        if params:
            arr = params['q'].split("*")
            list_ids = params.getlist('id')
            arr_len = len(arr)
            if arr_len == 1:
                try:
                    header['title'] = f"sim có chứa {params['q']}"
                    queryset = NumberPhone.objects.filter(number__contains=params['q'])
                    if list_ids:
                        for list_id in list_ids:
                            queryset = queryset.filter(category__id=list_id)
                    paginator = CustomPagination()
                    # paginator.page_size = 5
                    page = paginator.paginate_queryset(queryset, request)
                    if page is not None:
                        serializer = NumberPhoneSerializer(page, many=True)
                        return paginator.get_paginated_response(serializer.data, header)
                    else:
                        serializer = NumberPhoneSerializer(queryset, many=True)
                        data = {
                            'header': header,
                            'data': serializer.data
                        }
                        return Response(data, status=status.HTTP_200_OK)
                except Exception:
                    data = {
                        'message': 'Lỗi yêu cầu tài nguyên'
                    }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
            if arr_len == 2:
                header['title'] = f"sim {str_search}"
                try:
                    queryset = NumberPhone.objects.filter(number__startswith=arr[0], number__endswith=arr[1])
                    if list_ids:
                        for list_id in list_ids:
                            queryset = queryset.filter(category__id=list_id)
                    paginator = CustomPagination()
                    page = paginator.paginate_queryset(queryset, request)
                    if page is not None:
                        serializer = NumberPhoneSerializer(page, many=True)
                        return paginator.get_paginated_response(serializer.data, header)
                    else:
                        serializer = NumberPhoneSerializer(queryset, many=True)
                        data = {
                            'header': header,
                            'data': serializer.data
                        }
                        return Response(data, status=status.HTTP_200_OK)

                except Exception:
                    data = {
                        'message': 'Lỗi yêu cầu tài nguyên'
                    }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response({'data': params}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            queryset = NumberPhone.objects.get(pk=pk)
            serializer = NumberPhoneSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception:
            data = {
                'message': 'Lỗi yêu cầu tài nguyên'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class CustomerSerializerList(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        try:
            customer = Customer.objects.get(pk=pk)
            serializer = CustomerOderSerializer(customer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response({'message': 'Thông tin khách hàng không tồn tại'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'])
    def client(self, request, pk=None):
        try:
            customer = Customer.objects.get(pk=pk)
            serializer = CustomerSerializer(customer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'Thông tin khách hàng không tồn tại'}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        phone_id = request.data['id']
        number = NumberPhone.objects.get(pk=phone_id)
        name = request.data['fullName']
        contact = request.data['phone']
        address = request.data['address']
        note = request.data['note']
        try:
            customer = Customer.objects.get(contact=contact)
        except:
            customer = Customer.objects.create(full_name=name, contact=contact, address=address)
        try:
            price = number.price_discount()
            order = Order.objects.create(customer=customer, phone=number, price=price, note=note)
            number.is_stock = False
            number.save()
            serializer = OrderSerializer(order)
            response = {
                'message': f'Đặt hàng thành công số {number}',
                'result': serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        except:
            return Response({"message": "Đặt hàng thất bại"}, status=status.HTTP_400_BAD_REQUEST)


class NewSpostSerializerList(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        try:
            queryset = NewsPost.objects.get(pk=pk)
            serializer = NewsPostSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            data = {
                'message': 'Lỗi yêu cầu tài nguyên'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class GetInfor(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        try:
            queryset = Infor.objects.get(slug=pk)
            serializer = InforSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            data = {
                'message': 'Lỗi yêu cầu tài nguyên'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class PostList(viewsets.ViewSet):
    def list(self, request):
        try:
            queryset = Posts.objects.all()
            paginator = CustomPagination()
            paginator.page_size = 20
            page = paginator.paginate_queryset(queryset, request)
            if page is not None:
                # context={'request': request} them truong nay thi url img se co them domain
                # serializer = PostListSerializer(page, many=True, context={'request': request}) tra ve full url
                serializer = PostListSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data, header="")
            serializer = PostListSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            data = {
                'message': 'Lỗi yêu cầu tài nguyên'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            queryset = Posts.objects.get(slug=pk)
            serializer = PostRetrieveSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except:
            data = {
                'message': 'Lỗi yêu cầu tài nguyên'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def init_list(self, request):
        try:
            queryset = Posts.objects.all()[:10]
            serializer = PostListShortSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            data = {
                'message': 'Lỗi yêu cầu tài nguyên'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
