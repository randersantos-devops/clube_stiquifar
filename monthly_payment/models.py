from django.db import models
from escpos.printer import Usb
from django.db.models.signals import post_save
from django.dispatch import receiver

class Ticket(models.Model):

    REFERENCE_TYPES = [
        ('MENSALIDADE', 'MENSALIDADE'),
        ('JOIA', 'JOIA'),
        ('ALUGUEL BAR', 'ALUGUEL BAR'),
        ('OUTROS', 'OUTROS'),
        ('TAXA ARBITRAGEM', 'TAXA ARBITRAGEM'),
    ]

    MOVIMENT_TYPE = [
        ('ENTRADA', 'ENTRADA'),
        ('SAIDA', 'SAIDA'),
    ]

    PAYMENT_METHODS = [
        ('CARTAO DE CREDITO', 'CARTAO DE CREDITO'),
        ('CARTAO DE DEBITO', 'CARTAO DE DEBITO'),
        ('DINHEIRO', 'DINHEIRO'),
        ('PIX', 'PIX'),
    ]

    id = models.AutoField(primary_key=True)
    dt_emissao = models.DateTimeField(verbose_name='Data de Pagamento')
    name_payment = models.CharField(max_length=255, verbose_name='Nome do pagador')
    type_moviment = models.CharField(max_length=255, choices=MOVIMENT_TYPE, verbose_name='Tipo de Movimentação')
    reference_at = models.CharField(max_length=255, choices=REFERENCE_TYPES, verbose_name='Referente a')
    description = models.CharField(max_length=255, verbose_name='Descrição do pagamento')
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS, verbose_name='Forma de Pagamento')
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total', default=0)

    class Meta:
        ordering = ['-dt_emissao']
        verbose_name = 'Mensalidade'
        verbose_name_plural = 'Mensalidades'

    def __str__(self):
        return f'Pagamento realizado em: {self.dt_emissao.strftime("%d/%m/%Y %H:%M:%S")}'

    def generate_voucher(self):
        p = Usb(0x04B8, 0x0E27, 0, 0, 0)  # Substitua pelos IDs corretos da sua impressora
        cabecalho = '''CLUBE STIQUIFAR - CNPJ:20.052.817/0001-10\n\n
        TELEFONE: (34)3317-1646 - R. OUTONO 150, VILA ARQUELAU - UBERABA/MG
        '''
        logo = r'C:\Users\stiqu\PDV-CLUBE\django_admin\static\img\logo-stiquifar-site-recibo.png'

        p.set(align='center')
        p.image(img_source=logo)
        p.ln(1)
        p.set(bold=True, align='left')
        p.block_text(cabecalho)
        p.ln(2)
        p.set(align='center', height=4, width=4)
        p.text('Comprovante de Pagamento')
        p.ln(2)
        p.set(align='left', height=2, width=2, bold=False)
        p.text(f'Pagante: {self.name_payment}\n')
        p.text(f'Referente a: {self.reference_at}\n')
        p.text(f'Descriçao: {self.description}\n')
        p.text(f'Forma de Pagamento: {self.payment_method}\n')
        p.ln(1)
        p.text(f'Data de Retirada: {self.dt_emissao.strftime("%d/%m/%Y %H:%M:%S")}\n')
        p.text(f'Valor Total: R$ {self.value}')
        p.ln(2)
        p.set(height=4, width=4, bold=True)
        p.text('Obrigado escolher o Clube Stiquifar!!')
        p.cut()