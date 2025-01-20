from rest_framework import serializers
from movimenti.models import Movement, Category, Subcategory, AssetBalance
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    category_set = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all())
    subcategory_set = serializers.PrimaryKeyRelatedField(many=True, queryset=Subcategory.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'last_login', 'date_joined', 'category_set', 'subcategory_set']

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ["id", "subcategory"]

class CategorySerializer(serializers.ModelSerializer):
    direction = serializers.FloatField()

    class Meta:
        model = Category
        fields = ["id", "category", "direction"]
        
    def validate_direction(self, value):
        try:
            value = float(value)
            return value
        except Exception:
            raise serializers.ValidationError(f"Invalid 'direction' value: {value}")

class AssetBalanceSerializer(serializers.ModelSerializer):
    submission_id = serializers.CharField(read_only=True)
    class Meta:
        model = AssetBalance
        fields = '__all__'

class MovementSerializer(serializers.ModelSerializer):
    amount = serializers.FloatField(required=False)
    
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
