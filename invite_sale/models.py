from django.db import models
from escpos.printer import Usb
from django.db.models.signals import post_save
from django.dispatch import receiver

class InviteTicket(models.Model):
    id = models.AutoField(primary_key=True)
    dt_emissao = models.DateTimeField()
    total_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total', default=0)
    description = models.CharField(max_length=255, verbose_name='Observação', null=True, blank=True)

    class Meta:
        ordering = ['-dt_emissao']
        verbose_name = 'Convite Vendido'
        verbose_name_plural = 'Convites Vendidos'

    def __str__(self):
        return f'Convite comprado em: {self.dt_emissao.strftime("%d/%m/%Y %H:%M:%S")}'

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
        p.text('Comprovante Convite Cortesia')
        p.ln(2)
        p.set(align='left', height=2, width=2, bold=False)
        
        invites = InviteSale.objects.filter(invite_ticket=self)
        for invite in invites:
            p.text(f'Convidado: {invite.name_guest}\n')
            p.text(f'Doc Convidado: {invite.doc_guest}\n')
            p.text(f'Tipo do Convite: {invite.type_invite.name}\n')
            p.text(f'Valor Convite: R$ {invite.type_invite.price}\n')
            p.text(f'Forma de Pagamento: {invite.payment_method}\n')
            p.text('-------------------')
            p.ln(1)
        p.text(f'Data de Retirada: {self.dt_emissao.strftime("%d/%m/%Y %H:%M:%S")}\n')
        p.text(f'Valor Total: R$ {self.total_value}\n')
        if self.description:
            p.text(f'Observação: {self.description}\n')
        p.ln(2)
        p.set(height=4, width=4, bold=True)
        p.text('Obrigado por visitar o Clube Stiquifar!!')
        p.cut()

class TypeInvite(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='Nome')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço')

    class Meta:
        ordering = ['name']
        verbose_name = 'Tipo de Convite'
        verbose_name_plural = 'Tipos de Convites'

    def __str__(self):
        return self.name

class InviteSale(models.Model):
    PAYMENT_METHODS = [
        ('CARTAO DE CREDITO', 'CARTAO DE CREDITO'),
        ('CARTAO DE DEBITO', 'CARTAO DE DEBITO'),
        ('DINHEIRO', 'DINHEIRO'),
        ('PIX', 'PIX'),
    ]

    invite_ticket = models.ForeignKey(InviteTicket, on_delete=models.CASCADE, verbose_name='ID Ticket')
    name_guest = models.CharField(max_length=255, verbose_name='Nome do Convidado')
    doc_guest = models.CharField(max_length=15, verbose_name='Documento do Convidado')
    type_invite = models.ForeignKey(TypeInvite, on_delete=models.CASCADE, verbose_name='Tipo de Convite')
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS, verbose_name='Forma de Pagamento')


    class Meta:
        ordering = ['name_guest']
        verbose_name = 'Comprador'
        verbose_name_plural = 'Compradores'

    def __str__(self):
        return f'Convidado: {self.name_guest} portador do documento: {self.doc_guest}'
    

@receiver(post_save, sender=InviteSale)
def update_invite_ticket_total(sender, instance, **kwargs):
    invite_ticket = instance.invite_ticket
    total = sum(invite.type_invite.price for invite in InviteSale.objects.filter(invite_ticket=invite_ticket))
    invite_ticket.total_value = total
    invite_ticket.save(update_fields=['total_value'])
