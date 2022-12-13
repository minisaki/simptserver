from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Profile, Category, SubCategory, NumberPhone, Filter, Customer, NewsPost, Infor, Posts, Order, Discount, AgentPrice
import pandas as pd
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
import time

list_vina = ['91', '94', '81', '82', '83', '84', '85', '88']
list_mobi = ['90', '93', '70', '76', '77', '78', '79', '89']
list_vt = ['96', '97', '98', '32', '33', '34', '35', '36', '37', '38', '39', '86']
list_vnMobile = ['92', '56', '58']
list_gmobile = ['99', '59']
list_itel = ['87']

class FileForm(forms.Form):
  file_upload = forms.FileField()
  
class NumberPhoneAdmin(admin.ModelAdmin):
  list_display = ("number", "ower", "price", "agent_price")
  list_filter = ['create', 'category', 'ower']
  search_fields = ['number']
  ordering = ['-update']

  def save_related(self, request, form, formsets, change):
    super(NumberPhoneAdmin, self).save_related(request, form, formsets, change)    
    sub_priority = SubCategory.objects.get(slug="sim-gia-tot") 
    if form.instance.is_priority:               
      form.instance.category.add(sub_priority)
    else:
      form.instance.category.remove(sub_priority)

    sub_priority = SubCategory.objects.get(slug="sim-giam-gia")
    if form.instance.discount:      
      form.instance.category.add(sub_priority)
    else:
      form.instance.category.remove(sub_priority)

  def get_urls(self):
    urls = super().get_urls()
    new_urls = [
      path('upload-file/', self.upload_file),
    ]
    return new_urls + urls

  def get_ower(self, id, list_phone):
    try:
        ower = Profile.objects.get(pk=id)
        set_query = {data.number for data in ower.profile.all()}
        list_phone_result = []
        for phone in list_phone:
          has_dot = phone.find('.')
          if has_dot >= 0:
            phone = phone.replace('.', '')
          if phone[:1] == 'o':
            phone = phone.replace('o', '0')
          if len(phone) == 9:
            phone = f'0{phone}'
          if len(phone) == 10:
            list_phone_result.append(phone)
        set_phone = set(list_phone_result)
        diffirent = set_query.difference(set_phone)
        [ower.profile.get(number=number).delete() for number in diffirent]
        return ower
    except ower.DoesNotExist:
        raise Http404("Given query not found....")

  def read_file(self, request, file_name, sheet_name='Sheet2', sdt='sdt', price='price'):
    filePost = request.FILES[file_name]
    dfs = pd.read_excel(filePost, sheet_name=sheet_name)
    df = pd.DataFrame(dfs, columns= [sdt,price])
    listData = df.to_dict(orient='records')
    return listData

  def check_phone(self, phone, has_dot):    
    if not has_dot == -1:
      phone = phone.replace('.', '')
      if len(phone) == 10 and phone[:1] == 'o':
        phone = phone[1:]
        phone = f'0{phone}'
      elif len(phone) < 10:
        phone = f'0{phone}'
    else:
      if len(phone) == 9:
        phone = f'0{phone}'
    return phone

  def add_price(self, price):
    get_sub_cate = Category.objects.get(slug="sim-theo-gia").sub_menu.all()
    for sub_cate in get_sub_cate:
      [greater, less] = sub_cate.slug.split('-')
      if greater == 'tren' and price > int(less):
        return sub_cate
      elif greater != 'tren' and price > int(greater) and price <= int(less):
        return sub_cate

  def add_brand(self, dau_so):
    sub = ''
    if dau_so in list_vina:
      sub = SubCategory.objects.get(slug='vinaphone')
    elif dau_so in list_mobi:
      sub = SubCategory.objects.get(slug='mobifone')
    elif dau_so in list_vt:
      sub = SubCategory.objects.get(slug='viettel')
    elif dau_so in list_vnMobile:
      sub = SubCategory.objects.get(slug='vietnamobile')    
    elif dau_so in list_gmobile:
      sub = SubCategory.objects.get(slug='gmobile')
    elif dau_so in list_itel:
      sub = SubCategory.objects.get(slug='itelecom')
    return sub

  def add_format(self,phone):
    sub = ''
    display = ''
    sub_year = ''
    if phone[4:5]==phone[5:6]==phone[6:7]==phone[7:8]==phone[8:9]==phone[9:]:
      sub = SubCategory.objects.get(slug='sim-luc-quy')
      display = f'{phone[:4]}.{phone[4:]}'
    
    elif phone[5:6]==phone[6:7]==phone[7:8]==phone[8:9]==phone[9:]:
      sub = SubCategory.objects.get(slug='sim-ngu-quy')
      display = f'{phone[:3]}.{phone[3:5]}.{phone[5:]}'

    elif phone[6:7]==phone[7:8]==phone[8:9]==phone[9:]:
      sub = SubCategory.objects.get(slug='sim-tu-quy')
      display = f'{phone[:4]}.{phone[4:6]}.{phone[6:]}'

    elif phone[4:5]==phone[5:6]==phone[6:7] and phone[7:8]==phone[8:9]==phone[9:]:
      sub = SubCategory.objects.get(slug='tam-hoa-kep')
      display = f'{phone[:4]}.{phone[4:7]}.{phone[7:]}'

    elif phone[4:7] == phone[7:]:
      sub = SubCategory.objects.get(slug='sim-taxi')
      display = f'{phone[:4]}.{phone[4:7]}.{phone[7:]}'

    elif phone[2:6] == phone[6:]:
      sub = SubCategory.objects.get(slug='sim-taxi')
      display = f'{phone[:2]}.{phone[2:6]}.{phone[6:]}'

    elif phone[:5] == phone[5:]:
      sub = SubCategory.objects.get(slug='sim-taxi')
      display = f'{phone[:5]}.{phone[5:]}'

    elif phone[7:8]==phone[8:9]==phone[9:]:
      sub = SubCategory.objects.get(slug='sim-tam-hoa')
      display = f'{phone[:4]}.{phone[4:7]}.{phone[7:]}'

    elif phone[3:4]==phone[4:5]==phone[5:6]==phone[6:7]==phone[7:8]==phone[8:9]:
      sub = SubCategory.objects.get(slug='sim-luc-giua')
      display = f'{phone[:3]}.{phone[3:9]}.{phone[9:]}'
    
    elif phone[2:3]==phone[3:4]==phone[4:5]==phone[5:6]==phone[6:7]==phone[7:8]:
      sub = SubCategory.objects.get(slug='sim-luc-giua')
      display = f'{phone[:2]}.{phone[2:8]}.{phone[8:]}'
      
    elif phone[3:4]==phone[4:5]==phone[5:6]==phone[6:7]==phone[7:8]:
      sub = SubCategory.objects.get(slug='sim-ngu-giua')
      display = f'{phone[:3]}.{phone[3:8]}.{phone[8:]}'
    
    elif phone[4:5]==phone[5:6]==phone[6:7]==phone[7:8]==phone[8:9]:
      sub = SubCategory.objects.get(slug='sim-ngu-giua')
      display = f'{phone[:4]}.{phone[4:9]}.{phone[9:]}'

    elif phone[4:5]==phone[5:6]==phone[6:7]==phone[7:8]:
      sub = SubCategory.objects.get(slug='sim-tu-giua')
      display = f'{phone[:4]}.{phone[4:8]}.{phone[8:]}'

    elif phone[5:6]==phone[6:7]==phone[7:8]==phone[8:9]:
      sub = SubCategory.objects.get(slug='sim-tu-giua')
      display = f'{phone[:3]}.{phone[3:5]}.{phone[5:9]}.{phone[9:]}'

    elif phone[8:] == '79' or phone[8:] == '39':
      sub = SubCategory.objects.get(slug='sim-than-tai')
      display = f'{phone[:4]}.{phone[4:7]}.{phone[7:]}'

    elif phone[8:] == '68':
      sub = SubCategory.objects.get(slug='sim-loc-phat')
      display = f'{phone[:4]}.{phone[4:7]}.{phone[7:]}'

    elif phone[8:] == '78' or phone[8:] == '38':
      sub = SubCategory.objects.get(slug='sim-ong-dia')
      display = f'{phone[:4]}.{phone[4:7]}.{phone[7:]}'

    elif phone[4:5] == phone[9:] and phone[5:6] == phone[8:9] and phone[6:7]==phone[7:8]:
      sub = SubCategory.objects.get(slug='sim-ganh-dao')
      display = f'{phone[:4]}.{phone[4:7]}.{phone[7:]}'

    elif phone[4:5] == phone[5:6] and phone[6:7] == phone[7:8] and phone[8:9]==phone[9:]:
      sub = SubCategory.objects.get(slug='sim-lap-kep')
      display = f'{phone[:4]}.{phone[4:6]}.{phone[6:8]}.{phone[8:]}'

    elif int(phone[6:7]) == int(phone[7:8])-1 == int(phone[8:9])-2 == int(phone[9:])-3:
      sub = SubCategory.objects.get(slug='sim-sanh-tien')
      display = f'{phone[:4]}.{phone[4:6]}.{phone[6:]}'

    elif int(phone[7:8]) == int(phone[8:9])-1 == int(phone[9:])-2:
      sub = SubCategory.objects.get(slug='sim-sanh-tien')
      display = f'{phone[:4]}.{phone[4:7]}.{phone[7:]}'

    elif phone[6:8] == phone[8:]:
      sub = SubCategory.objects.get(slug='sim-cap-abab')
      display = f'{phone[:4]}.{phone[4:7]}.{phone[7:]}'

    elif int(phone[6:]) >= 1985 and int(phone[6:]) <= 2001:
      sub = SubCategory.objects.get(slug='sim-nam-sinh')
      display = f'{phone[:4]}.{phone[4:6]}.{phone[6:]}'

      if phone[6:] == '1985':
        sub_year = SubCategory.objects.get(slug='nam-sinh-1985')
      elif phone[6:] == '1986':            
        sub_year = SubCategory.objects.get(slug='nam-sinh-1986')     
      elif phone[6:] == '1987':            
        sub_year = SubCategory.objects.get(slug='nam-sinh-1987')
      elif phone[6:] == '1988':            
        sub_year = SubCategory.objects.get(slug='nam-sinh-1988')
      elif phone[6:] == '1989':            
        sub = SubCategory.objects.get(slug='nam-sinh-1989')
      elif phone[6:] == '1990':            
        sub_year = SubCategory.objects.get(slug='nam-sinh-1990')
      elif phone[6:] == '1991':            
        sub_year = SubCategory.objects.get(slug='nam-sinh-1991')
      elif phone[6:] == '1992':            
        sub_year = SubCategory.objects.get(slug='nam-sinh-1992')
      elif phone[6:] == '1993':            
        sub_year = SubCategory.objects.get(slug='nam-sinh-1993')
        display = f'{phone[:4]}.{phone[4:6]}.{phone[6:]}'
      elif phone[6:] == '1994':            
        sub_year = SubCategory.objects.get(slug='nam-sinh-1994')
      elif phone[6:] == '1995':            
        sub_year = SubCategory.objects.get(slug='nam-sinh-1995')
      elif phone[6:] == '1996':            
        sub_year = SubCategory.objects.get(slug='nam-sinh-1996')
      elif phone[6:] == '1997':            
        sub_year = SubCategory.objects.get(slug='nam-sinh-1997')
      elif phone[6:] == '1998':            
        sub_year = SubCategory.objects.get(slug='nam-sinh-1998')
      elif phone[6:] == '2001':            
        sub_year = SubCategory.objects.get(slug='nam-sinh-2001')   
    elif phone[8:] == '86':
      sub = SubCategory.objects.get(slug='sim-phat-loc')
      display = f'{phone[:4]}.{phone[4:6]}.{phone[6:]}'
    else:
      sub = SubCategory.objects.get(slug='sim-phong-thuy')
      display = f'{phone[:4]}.{phone[4:7]}.{phone[7:]}'
    
    return [sub, display, sub_year]
      
  
  def upload_file(self, request):
    if request.method == 'POST':
      id = request.POST['user']
      discount = request.POST['discount']
      try:
        priority = request.POST['priority']
      except:
        priority = "False"
      listData = self.read_file(request, file_name='file_upload')
      list_phone = [str(data['sdt']) for data in listData]
      ower = self.get_ower(id, list_phone)

      for x in listData:
        try:
          if x['price'] and x['sdt']:            
            price = int(str(x['price']).replace('.', ''))
            phone_origin = str(x['sdt']).strip()
            if phone_origin[:1] != '0' and len(phone_origin) < 10:
              phone_origin = f'0{phone_origin}'
            if phone_origin[:1] == 'o' or phone_origin[:1] == 'O':
              phone_origin = phone_origin.replace(phone_origin[:1], '0')

            has_dot = phone_origin.find('.')
            phone = self.check_phone(phone=phone_origin, has_dot=has_dot)
            dau_so = phone[1:3]
            if len(phone) == 10:
              try:
                number = NumberPhone.objects.get(number=phone)
                if not number.price == price:
                  sub = self.add_price(number.price)
                  number.category.remove(sub)
                  number.price = price
                  sub = self.add_price(price)
                  number.category.add(sub)
              except NumberPhone.DoesNotExist:
                number = NumberPhone(number=phone)
                number.ower = ower
                number.price = price
                if has_dot >= 0:
                  number.number_display = phone_origin
                number.save()

                if int(discount):
                  number.discount = discount
                  sub_cate = SubCategory.objects.get(slug="sim-gia-tot")
                  number.category.add(sub_cate)

                if priority == "True":
                  number.is_priority = True
                  sub_cate = SubCategory.objects.get(slug="sim-giam-gia")
                  number.category.add(sub_cate)                    

                sub_price = self.add_price(price)
                if sub_price:
                  number.category.add(sub_price)
                
                sub_brand = self.add_brand(dau_so)
                if sub_brand:
                  number.category.add(sub_brand)
                
                sub, display, sub_year = self.add_format(phone)
                if sub and display:
                  if not number.number_display:
                    number.number_display = display
                  number.category.add(sub)
                  if sub_year:
                    number.category.add(sub_year)
                
              number.save()
        except:
          print(f'co loi {x["sdt"]}')
          continue
      return redirect('/quan_tri/webApps/numberphone/')
        
    else:
      form = FileForm()
      profile = Profile.objects.all()
      data = {
        "form": form,
        "user": profile
      }
      return render(request, "admin/file-upload.html", data)

class SubCategoryForm(forms.ModelForm):
  description = forms.CharField(widget=CKEditorUploadingWidget)
  class Meta:
    model = SubCategory
    fields = '__all__'

class SubCategoryAdmin(admin.ModelAdmin):
  form = SubCategoryForm
  list_filter = ['menu']

class AgentPriceAdmin(admin.ModelAdmin):
  list_display = ("profile", "slug", "rate_discount")


admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(NumberPhone, NumberPhoneAdmin)
admin.site.register(Filter)
admin.site.register(Customer)
admin.site.register(NewsPost)
admin.site.register(Infor)
admin.site.register(Posts)
admin.site.register(Order)
admin.site.register(Discount)
admin.site.register(AgentPrice, AgentPriceAdmin)
