from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from django.http import HttpResponseRedirect, HttpResponse
from .models import Ticket
import pandas as pd
from fpdf import FPDF


class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'dt_emissao', 'name_payment', 'reference_at', 'value', 'description', 'payment_method',
                     'generate_voucher_button')
    list_filter = ['dt_emissao',]
    actions = ['export_csv', 'export_to_pdf']
    list_per_page = 30

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

    # Função para exportar dados selecionados para CSV
    def export_csv(self, request, queryset):
        # Cria uma lista de dicionários para gerar o CSV
        data = []
        for ticket in queryset:
            data.append({
                'Data Emissao': ticket.dt_emissao.strftime('%d/%m/%Y %H:%M'),
                'Nome Pagante': ticket.name_payment,
                'Tipo de Movimentacao': ticket.type_moviment,
                'Referente a': ticket.reference_at,
                'Descricao': ticket.description,
                'Forma de Pagamento': ticket.payment_method,
                'Valor Total': f'{ticket.value:.2f}'.replace('.', ','),
            })

        # Converte para DataFrame pandas
        df = pd.DataFrame(data)

        # Cria uma resposta HTTP com o conteúdo CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="pagamentos_selecionados.csv"'

        # Exporta para CSV e escreve na resposta HTTP
        df.to_csv(path_or_buf=response, sep=';', index=False, encoding='UTF-8', decimal=',')

        return response

    export_csv.short_description = "Exportar Pagamentos Selecionados para CSV"

    # Função para exportar dados selecionados para PDF
    def export_to_pdf(self, request, queryset):
        # Cria um objeto PDF
        pdf = CustomPDF()
        pdf.add_page('l')

        # Coleta os campos e valores dos objetos selecionados
        fields = [field.name for field in self.model._meta.fields]
        data = queryset.values_list()

        # Adiciona a tabela ao PDF
        pdf.add_table(data, fields)

        # Configura a resposta HTTP para download
        response = HttpResponse(pdf.output(dest='S').encode('latin1'), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="dados_exportados.pdf"'
        return response

    export_to_pdf.short_description = "Exportar para PDF"


# Classe customizada para geração de PDF
class CustomPDF(FPDF):
    def header(self):
        # Define um cabeçalho para o PDF
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Relatório de Dados Exportados', 0, 1, 'C')

    def footer(self):
        # Define um rodapé para o PDF
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_table(self, data, fields):
        # Define a largura das colunas com base no conteúdo
        col_widths = [self.get_string_width(field) + 10 for field in fields]  # 10 é a margem extra

        # Adiciona os cabeçalhos das colunas
        self.set_font('Arial', 'B', 8)
        for i, field in enumerate(fields):
            self.cell(col_widths[i], 10, field, 1)
        self.ln()

        # Adiciona os dados da tabela
        self.set_font('Arial', '', 5)
        for row in data:
            for i, value in enumerate(row):
                self.cell(col_widths[i], 10, str(value), 1)
            self.ln()

# Registra o model Ticket com o admin personalizado
admin.site.register(Ticket, TicketAdmin)
