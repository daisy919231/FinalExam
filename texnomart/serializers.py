from rest_framework import serializers
from texnomart.models import Category, Group, Product, ProductCharacteristics, CharacteristicsKey, CharacteristicsValue
from django.db.models import Avg
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
       model=Category
       fields='__all__' 

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model=Group
        fields='__all__'

class AllProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields='__all__'

class CategorySlugSerializer(serializers.ModelSerializer):
    is_primary = serializers.SerializerMethodField()
    all_products = serializers.SerializerMethodField()

    def get_all_products(self, instance):
        request = self.context.get('request')
        products = []
        
        # Loop through all groups and their products
        for group in instance.groups.all():
            for product in group.products.all():
                products.append(AllProductSerializer(product).data)  # Serialize each product

        return products

    def get_is_primary(self, instance):
        request = self.context.get('request')
        if not request:
            return None
        for group in instance.groups.all():
            for product in group.products.all():
                for image in product.images.all():
                    if image.is_primary:
                        return request.build_absolute_uri(image.image.url)

        return None  # Return None if no primary image is found

    class Meta:
        model = Category
        fields = '__all__'



class ProductCharSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductCharacteristics
        exclude=('id', 'product', 'char_key', 'char_value')

    def to_representation(self, instance):
        context=super(ProductCharSerializer, self).to_representation(instance)
        # context['key_id']=instance.char_key.id
        # context['key_name']=instance.char_key.key_name
        # context['value_id']=instance.char_value.id
        # context['value_name']=instance.char_value.value_name
        # return context

        # ID KERAK BO'LSA YUQORIDAGI ISHLATILADI
        return {instance.char_key.key_name:instance.char_value.value_name}


class ProductSerializer(serializers.ModelSerializer):
    characteristics=ProductCharSerializer(many=True, read_only=True)
    all_images = serializers.SerializerMethodField()
    all_comments = serializers.SerializerMethodField()
    comment_count=serializers.SerializerMethodField()
    average_rating=serializers.SerializerMethodField()
    is_liked=serializers.SerializerMethodField()

    def get_all_images(self, instance):
        request = self.context.get('request')
        images = [request.build_absolute_uri(image.image.url) for image in instance.images.all() if image.image]
        return images
    
    def get_all_comments(self, instance):
        request = self.context.get('request')
        comments = [comment.message for comment in instance.ratings.all()]
        return comments
    
    def get_comment_count(self, instance):
        request = self.context.get('request')
        count=instance.ratings.count()
        return count
    
    def get_average_rating(self, instance):
        request = self.context.get('request')
        avg_rating=instance.ratings.aggregate(Avg('rating'))['rating__avg'] or 0.0
        return avg_rating
    
    def get_is_liked(self, instance):
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
# Is_liked uchun alohida table ochiladi va shuning uchun userni idsi bilan kirish imkonimiz bo'ladi.
            return instance.is_liked.filter(id=user.id).exists()
        return False  
       

# # a little inaccurate, because two names for average_rating, but I should look for a better solution!

    
    class Meta:
        model=Product
        fields='__all__'


class KeySerializer(serializers.ModelSerializer):
    class Meta:
        model=CharacteristicsKey
        fields='__all__'

class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model=CharacteristicsValue
        fields='__all__'

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(
    required=True,
    validators=[UniqueValidator(queryset=User.objects.all())]
  )
  password = serializers.CharField(
    write_only=True, required=True, validators=[validate_password])
  password2 = serializers.CharField(write_only=True, required=True)
  class Meta:
    model = User
    fields = ('username', 'password', 'password2',
         'email', 'first_name', 'last_name')
    extra_kwargs = {
      'first_name': {'required': True},
      'last_name': {'required': True}
    }
  def validate(self, attrs):
    if attrs['password'] != attrs['password2']:
      raise serializers.ValidationError(
        {"password": "Password fields didn't match."})
    return attrs
  def create(self, validated_data):
    user = User.objects.create(
      username=validated_data['username'],
      email=validated_data['email'],
      first_name=validated_data['first_name'],
      last_name=validated_data['last_name']
    )
    user.set_password(validated_data['password'])
    user.save()
    return user
