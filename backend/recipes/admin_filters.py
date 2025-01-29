from django.db.models import Avg, Max, Min
from django.contrib import admin


class CookingTimeFilter(admin.SimpleListFilter):
    title = 'Время готовки'
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        queryset = model_admin.get_queryset(request)
        stats = queryset.aggregate(
            min_time=Min(self.parameter_name),
            avg_time=Avg(self.parameter_name),
            max_time=Max(self.parameter_name),
        )
        fast = int(stats['avg_time'] * 0.75)
        medium = int(stats['avg_time'] * 1.25)
        fast_count = queryset.filter(
            cooking_time__lte=fast).count()
        medium_count = queryset.filter(
            cooking_time__gt=fast, cooking_time__lte=medium).count()
        long_count = queryset.filter(
            cooking_time__gt=medium).count()
        return [
            ('fast', f'Быстрее {fast} мин ({fast_count})'),
            ('medium', f'До {medium} мин ({medium_count})'),
            ('long', f'Долго ({long_count})'),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if not value or not queryset:
            return queryset
        queryset = queryset.annotate(avg_time=Avg(self.parameter_name))
        fast = int(queryset.aggregate(
            Avg('cooking_time'))['cooking_time__avg'] * 0.75)
        medium = int(queryset.aggregate(
            Avg('cooking_time'))['cooking_time__avg'] * 1.25)
        if value == 'fast':
            return queryset.filter(
                cooking_time__lte=fast)
        elif value == 'medium':
            return queryset.filter(
                cooking_time__gt=fast, cooking_time__lte=medium)
        elif value == 'long':
            return queryset.filter(
                cooking_time__gt=medium)
        return queryset
