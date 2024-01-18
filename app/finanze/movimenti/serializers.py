from rest_framework import serializers
from .models import Movement, Category, Subcategory, AssetBalance
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    category_set = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all())
    subcategory_set = serializers.PrimaryKeyRelatedField(many=True, queryset=Subcategory.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'category_set', 'subcategory_set']

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ["id", "subcategory"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "category", "direction"]

class AssetBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetBalance
        fields = '__all__'

class MovementSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    subcategory = SubcategorySerializer(read_only=True)
    
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Movement
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new `Movement` instance, given the validated data.
        """
        return Movement.objects.create(**validated_data)

    def update(self, instance: Movement, validated_data):
        """
        Update and return an existing `Movement` instance, given the validated data.
        """
        instance.date = validated_data.get("date", instance.date)
        instance.abs_amount = validated_data.get("abs_amount", instance.abs_amount)
        instance.description = validated_data.get("description", instance.description)
        instance.category = validated_data.get("category", instance.category)
        instance.subcategory = validated_data.get("subcategory", instance.subcategory)
        instance.save()
        return instance
