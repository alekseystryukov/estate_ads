from postman.fields import CommaSeparatedUserField
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class CommaSeparatedUserIdField(CommaSeparatedUserField):

    def clean(self, value):
        """Check names are valid and filter them."""
        names = super(CommaSeparatedUserField, self).clean(value)
        if not names:
            return []
        user_model = get_user_model()
        users = list(user_model.objects.filter(is_active=True, **{'id__in': names}))
        unknown_names = set(names) ^ set([str(u.id) for u in users])
        errors = []
        if unknown_names:
            errors.append(self.error_messages['unknown'].format(users=', '.join(unknown_names)))
        if self.user_filter:
            filtered_names = []
            for u in users[:]:
                try:
                    reason = self.user_filter(u)
                    if reason is not None:
                        users.remove(u)
                        filtered_names.append(
                            self.error_messages[
                                'filtered_user_with_reason' if reason else 'filtered_user'
                            ].format(username=u.get_full_name(), reason=reason)
                        )
                except ValidationError as e:
                    users.remove(u)
                    errors.extend(e.messages)
            if filtered_names:
                errors.append(self.error_messages['filtered'].format(users=', '.join(filtered_names)))
        if errors:
            raise ValidationError(errors)
        return users