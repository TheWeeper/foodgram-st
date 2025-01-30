from django.db.models import Avg
from django.contrib import admin


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время готовки'
    parameter_name = 'cooking_time'
    fast = None
    medium = None
    

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        self.fast = int(queryset.aggregate(
            Avg('cooking_time'))['cooking_time__avg'] * 0.75)
        self.medium = int(queryset.aggregate(
            Avg('cooking_time'))['cooking_time__avg'] * 1.25)
        fast_count = queryset.filter(
            cooking_time__lte=self.fast).count()
        medium_count = queryset.filter(
            cooking_time__gt=self.fast, cooking_time__lte=self.medium).count()
        long_count = queryset.filter(
            cooking_time__gt=self.medium).count()
        return [
            ('fast', f'Быстрее {self.fast} мин ({fast_count})'),
            ('medium', f'До {self.medium} мин ({medium_count})'),
            ('long', f'Долго ({long_count})'),
        ]

    def queryset(self, request, queryset):
        print(queryset, request)
        value = self.value()
        if not value or not queryset:
            return queryset
        if value == 'fast':
            return queryset.filter(
                cooking_time__lte=self.fast)
        elif value == 'medium':
            return queryset.filter(
                cooking_time__gt=self.fast, cooking_time__lte=self.medium)
        elif value == 'long':
            return queryset.filter(
                cooking_time__gt=self.medium)
        return queryset
