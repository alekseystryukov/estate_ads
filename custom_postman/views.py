from postman.views import WriteView
# from django.contrib.auth import get_user_model
from ads.models import Ad


class MyWriteView(WriteView):
    # # by user id
    # def get_initial(self):
    #     initial = super(WriteView, self).get_initial()
    #     if self.request.method == 'GET':
    #         initial.update(self.request.GET.items())  # allow optional initializations by query string
    #         recipients = self.kwargs.get('recipients')
    #         if recipients:
    #             # order_by() is not mandatory, but: a) it doesn't hurt; b) it eases the test suite
    #             # and anyway the original ordering cannot be respected.
    #             user_model = get_user_model()
    #             usernames = list(user_model.objects.values_list('id', flat=True).filter(
    #                 **{'id__in': [r.strip() for r in recipients.split(':') if r and not r.isspace()]}
    #             ).order_by(user_model.USERNAME_FIELD))
    #             print(usernames)
    #             print([r.strip() for r in recipients.split(':') if r and not r.isspace()])
    #             if usernames:
    #                 initial['recipients'] = ', '.join(str(x) for x in usernames)
    #     return initial

    def get_initial(self):
        initial = super(WriteView, self).get_initial()
        if self.request.method == 'GET':
            initial.update(self.request.GET.items())
            recipients = self.kwargs.get('recipients')
            if recipients:
                try:
                    ad = Ad.objects.get(pk=recipients)
                    initial['subject'] = ad.title
                    if ad.user_id:
                        initial['recipients'] = str(ad.user_id)
                except Ad.DoesNotExist:
                    pass
        return initial