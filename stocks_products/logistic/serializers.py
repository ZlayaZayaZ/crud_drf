from rest_framework import serializers
from .models import Product, Stock, StockProduct


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockProduct
        fields = ['quantity', 'price', 'product']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    class Meta:
        model = Stock
        fields = ['id', 'address', 'positions']

    def create(self, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # создаем склад по его параметрам
        stock = super().create(validated_data)

        # заполняем таблицу StockProduct
        # с помощью списка positions
        for position in positions:
            StockProduct.objects.get_or_create(stock=stock, **position)

        return stock

    def update(self, instance, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # обновляем склад по его параметрам
        stock = super().update(instance, validated_data)

        # обновляем данные таблицы StockProduct
        # с помощью списка positions
        for position in positions:

            try:
                # ищем объект в базе данных StockProduct по id склада и продукта
                # меняем цену и количество, на заданные в запросе, если объект найден
                stock_product = StockProduct.objects.get(stock=stock, product=position.get('product'))
                stock_product.price = position.get('price', stock_product.price)
                stock_product.quantity = position.get('quantity', stock_product.quantity)
                stock_product.save()

            # если объект в базе не найден - ловим исключение и создаем объект
            except StockProduct.DoesNotExist:
                StockProduct.objects.create(stock=stock, **position)

        return stock
