from django.utils.safestring import mark_safe


def _move_up_obj(obj):
    weight = obj.weight
    q = obj.__class__.objects.filter(weight__lt=weight).order_by('-weight')
    if q.count() == 0:
        return # Topmost

    prev_obj = q[0]
    obj.weight = prev_obj.weight
    prev_obj.weight = weight
    obj.save()
    prev_obj.save()

def move_up(modeladmin, request, queryset):
    for obj in queryset:
        _move_up_obj(obj)
move_up.short_description = "Move the object up in the order"


def _move_down_obj(obj):
    weight = obj.weight
    q = obj.__class__.objects.filter(weight__gt=weight).order_by('weight')
    if q.count() == 0:
        return # Bottommost

    next_obj = q[0]
    obj.weight = next_obj.weight
    next_obj.weight = weight
    obj.save()
    next_obj.save()

def move_down(modeladmin, request, queryset):
    for obj in queryset:
        _move_down_obj(obj)
move_down.short_description = "Move the object down in the order"


class MoveMethods:
    SCRIPT = """
        <a href="#" onclick="django.jQuery('select[name=action]').val('move_up'); django.jQuery('input[name=_selected_action][value=%(pk)d]').attr('checked', ''); django.jQuery('#changelist-form').submit(); return false;">&#9650;</a>
        <a href="#" onclick="django.jQuery('select[name=action]').val('move_down'); django.jQuery('input[name=_selected_action][value=%(pk)d]').attr('checked', ''); django.jQuery('#changelist-form').submit(); return false;">&#9660;</a>
        """
    def move(self, obj):
        return mark_safe(MoveMethods.SCRIPT % { 'pk': obj.pk })
