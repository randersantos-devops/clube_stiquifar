from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from django.http import HttpResponseRedirect, HttpResponse
from .models import InviteSale, InviteTicket, TypeInvite
from django.utils import timezone
import pandas as pd


class InviteSaleInline(admin.TabularInline):
    model = InviteSale
    extra = 1

class InviteTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_dt_emissao', 'get_name_guest', 'total_value', 'generate_voucher_button')
    list_filter = ['dt_emissao',]
    inlines = [InviteSaleInline]
    actions = ['export_csv']

    def get_name_guest(self, obj):
        invite_sale = InviteSale.objects.filter(invite_ticket=obj).first()
        if invite_sale:
            return invite_sale.name_guest
        return "-"
    get_name_guest.short_description = "Nome do Convidado"

 
    def get_type_invite(self, obj):
        invite_sale = InviteSale.objects.filter(invite_ticket=obj).first()
        if invite_sale:
            return invite_sale.type_invite.name
        return "-"
    get_type_invite.short_description = "Tipo de Convite"

    def get_dt_emissao(self, obj):
        return obj.dt_emissao.strftime('%d/%m/%Y %H:%M')
    get_dt_emissao.short_description = "Data de Emissão"

    def generate_voucher_button(self, obj):
        return format_html(
            '<a class="button" href="{}">Gerar Comprovante</a>',
            f'./{obj.id}/generate_voucher/'
        )
    generate_voucher_button.short_description = "Gerar Comprovante"

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
    
    def export_csv(self, request, queryset):
        # Obtém a data atual
        today = timezone.now().date()
        
        # Lista de dicionários para armazenar os dados
        data = []

        # Itera sobre os tickets no queryset selecionado
        for ticket in queryset:
            # Verifica se o ticket tem vendas associadas
            sales = InviteSale.objects.filter(invite_ticket=ticket)
            for sale in sales:
                data.append({
                    'ID Ticket': ticket.id,
                    'Data Emissao': ticket.dt_emissao.strftime('%d/%m/%Y %H:%M'),
                    'Nome Convidado': sale.name_guest,
                    'Documento Convidado': sale.doc_guest,
                    'Tipo de Convite': sale.type_invite.name,
                    'Valor Convite': f'{sale.type_invite.price:.2f}'.replace('.', ','),
                    'Forma de Pagamento': sale.payment_method,
                    'Valor Total do Ticket': f'{ticket.total_value:.2f}'.replace('.', ','),
                })

        if not data:
            self.message_user(request, "Nenhum dado encontrado para exportar.", level="error")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Converte a lista de dicionários em um DataFrame do pandas
        df = pd.DataFrame(data)

        # Cria uma resposta HTTP para o conteúdo CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="convites_{today}.csv"'

        # Exporta os dados para CSV e escreve na resposta HTTP
        df.to_csv(path_or_buf=response, sep=';', index=False, encoding='ISO-8859-1')

        return response

    
class InviteSaleAdmin(admin.ModelAdmin):
    list_display = ['name_guest', 'doc_guest', 'type_invite', 'payment_method']
    
admin.site.register(InviteTicket, InviteTicketAdmin)
admin.site.register(TypeInvite, admin.ModelAdmin)
admin.site.register(InviteSale, InviteSaleAdmin)
