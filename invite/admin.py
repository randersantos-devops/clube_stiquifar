from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from .models import Invite, InviteTicket

class InviteInline(admin.TabularInline):
    model = Invite
    extra = 1

class InviteTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'dt_emissao', 'name_associate', 'invite_status', 'generate_voucher_button')
    search_fields = ('name_associate', 'invite_status',)
    inlines = [InviteInline]

    def generate_voucher_button(self, obj):
        return format_html(
            '<a class="button" href="{}">Gerar Comprovante</a>',
            f'./{obj.id}/generate_voucher/'
        )
    generate_voucher_button.short_description = "Gerar Comprovante"
    generate_voucher_button.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:pk>/generate_voucher/',
                self.admin_site.admin_view(self.generate_voucher),
                name='generate_voucher',
            ),
        ]
        return custom_urls + urls

    def generate_voucher(self, request, pk):
        invite_ticket = self.get_object(request, pk)
        invite_ticket.generate_voucher()
        self.message_user(request, "Comprovante gerado com sucesso.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

admin.site.register(InviteTicket, InviteTicketAdmin)
admin.site.register(Invite, admin.ModelAdmin)
