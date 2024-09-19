from django.db import models
from escpos.printer import Usb

class InviteTicket(models.Model):

    TYPE_ASSOCIATES = [
        ('AGREGADO(A)', 'AGREGADO(A)'),
        ('SINDICALIZADO(A)', 'SINDICALIZADO(A)'),
    ]

    STATUS_INVITE = [
        ('CANCELADO', 'CANCELADO'),
        ('RETIRADO', 'RETIRADO'),
        ('SOLICITADO', 'SOLICITADO')
    ]

    id = models.AutoField(primary_key=True)
    dt_emissao = models.DateTimeField(auto_now_add=True)
    name_associate = models.CharField(max_length=255, verbose_name='Nome do Associado')
    type_associate = models.CharField(max_length=30, choices=TYPE_ASSOCIATES, verbose_name='Tipo de Sócio')
    invite_status = models.CharField(max_length=30, choices=STATUS_INVITE, verbose_name='Status do Convite')

    class Meta:
        ordering = ['dt_emissao']
        verbose_name = 'Cortesia'
        verbose_name_plural = 'Cortesias'

    def __str__(self):
        return f'Convite retirado em: {self.dt_emissao.strftime("%d/%m/%Y %H:%M:%S")} por {self.name_associate}'
    
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
        p.text(f'Associado: {self.name_associate}\n')
        p.text(f'Tipo Sócio: {self.type_associate}\n')
        # Iterando sobre os convites relacionados
        invites = Invite.objects.filter(invite_ticket=self)
        for invite in invites:
            p.set(height=2, width=2, bold=False)
            p.text(f'Convidado: {invite.name_guest}\n')
            p.text(f'Doc Convidado: {invite.doc_guest}\n')
            
            p.text('-------------------')
            p.ln(1)

        p.text(f'Data de Retirada: {self.dt_emissao.strftime("%d/%m/%Y %H:%M:%S")}\n')
        p.ln(2)
        p.set(height=4, width=4, bold=True)
        p.text('Obrigado por visitar o Clube Stiquifar!!')
        p.cut()

class Invite(models.Model):
    invite_ticket = models.ForeignKey(InviteTicket, on_delete=models.CASCADE, verbose_name='ID Ticket')
    name_guest = models.CharField(max_length=255, verbose_name='Nome do Convidado')
    doc_guest = models.CharField(max_length=15, verbose_name='Documento do Convidado')

    class Meta:
        ordering = ['name_guest']
        verbose_name = 'Convidado'
        verbose_name = 'Convidado'

    def __str__(self):
        return f'Convidado: {self.name_guest} portador do documento: {self.doc_guest}'
