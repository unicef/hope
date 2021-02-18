# Register your models here.
from django import forms
from django.contrib import admin
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils import timezone

from adminfilters.filters import TextFieldFilter

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.erp_datahub.models import DownPayment, FundsCommitment
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase

currencies = (
    ("AED", "UAE Dirham"),
    ("AFN", "Afghani"),
    ("ALL", "Lek"),
    ("AMD", "Armenisk Dram"),
    ("ANG", "Gulden från Nederländska Antillerna"),
    ("AOA", "Kwanza"),
    ("ARS", "Argentinsk Peso"),
    ("AUD", "Australisk Dollar"),
    ("AWG", "Arubisk Florin"),
    ("AZN", "Azerbajdzjansk Manat"),
    ("BAM", "Konvertibel Mark"),
    ("BBD", "Barbadosdollar"),
    ("BDT", "Taka"),
    ("BGN", "Bulgarisk Lev"),
    ("BHD", "Bahraini Dinar"),
    ("BIF", "Burundi-franc"),
    ("BMD", "Bermuda-dollar"),
    ("BND", "Brunei-dollar"),
    ("BOB", "Boliviano"),
    ("BOV", "Mvdol"),
    ("BRL", "Brasilisk Real"),
    ("BSD", "Bahamasdollar"),
    ("BTN", "Ngultrum"),
    ("BWP", "Pula"),
    ("BYR", "Vitrysk Rubel"),
    ("BZD", "Belize-dollar"),
    ("CAD", "Kanadensisk Dollar"),
    ("CDF", "Kongolesisk Franc"),
    ("CHE", "WIR Euro"),
    ("CHF", "Schweizerfranc"),
    ("CHW", "WIR Franc"),
    ("CLF", "Unidad de Fomento"),
    ("CLP", "Chilensk Peso"),
    ("CNY", "Yuan Renminbi"),
    ("COP", "Colombiansk Peso"),
    ("COU", "Unidad de Valor Real"),
    ("CRC", "Costa Ricansk Colon"),
    ("CUC", "Peso Convertible"),
    ("CUP", "Kubansk Peso"),
    ("CVE", "Kap Verde Escudo"),
    ("CZK", "Tjeckisk Koruna"),
    ("DJF", "Djibouti-franc"),
    ("DKK", "Dansk Krone"),
    ("DOP", "Dominicansk Peso"),
    ("DZD", "Algerisk Dinar"),
    ("EGP", "Egyptiskt pund"),
    ("ERN", "Nakfa"),
    ("ETB", "Etiopisk Birr"),
    ("EUR", "Euro"),
    ("FJD", "Fiji Dollar"),
    ("FKP", "Pund från Falklandöarna"),
    ("GBP", "Pund Sterling"),
    ("GEL", "Lari"),
    ("GHS", "Ghana Cedi"),
    ("GIP", "Gibraltar-pund"),
    ("GMD", "Dalasi"),
    ("GNF", "Guinea-franc"),
    ("GTQ", "Quetzal"),
    ("GYD", "Guyana-dollar"),
    ("HKD", "Hong Kong-dollar"),
    ("HNL", "Lempira"),
    ("HRK", "Kuna"),
    ("HTG", "Gourde"),
    ("HUF", "Forint"),
    ("IDR", "Rupiah"),
    ("ILS", "Ny Israelisk Shekel"),
    ("INR", "Indisk Rupie"),
    ("IQD", "Irakisk Dinar"),
    ("IRR", "Iransk Rial"),
    ("ISK", "Isländsk Krona"),
    ("JMD", "Jamaica-dollar"),
    ("JOD", "Jordanisk Dinar"),
    ("JPY", "Yen"),
    ("KES", "Kenyansk Shilling"),
    ("KGS", "Som"),
    ("KHR", "Riel"),
    ("KMF", "Comoros-franc"),
    ("KPW", "Nordkoreansk Won"),
    ("KRW", "Won"),
    ("KWD", "Kuwaiti Dinar"),
    ("KYD", "Caymanöar-dollar"),
    ("KZT", "Tenge"),
    ("LAK", "Kip"),
    ("LBP", "Libanesiskt pund"),
    ("LKR", "Sri Lanka Rupie"),
    ("LRD", "Liberiansk Dollar"),
    ("LSL", "Loti"),
    ("LYD", "Libysk Dinar"),
    ("MAD", "Marockansk Dirham"),
    ("MDL", "Moldavisk Leu"),
    ("MGA", "Malagasy Ariary"),
    ("MKD", "Denar"),
    ("MMK", "Kyat"),
    ("MNT", "Tugrik"),
    ("MOP", "Pataca"),
    ("MRO", "Ouguiya"),
    ("MUR", "Mauritius Rupie"),
    ("MVR", "Rufiyaa"),
    ("MWK", "Kwacha"),
    ("MXN", "Mexikansk Peso"),
    ("MXV", "Mexikansk Unidad de Inversion (UDI)"),
    ("MYR", "Malaysisk Ringgit"),
    ("MZN", "Mozambique Metical"),
    ("NAD", "Namibia Dollar"),
    ("NGN", "Naira"),
    ("NIO", "Cordoba Oro"),
    ("NOK", "Norsk Krone"),
    ("NOK", "Norwegian Krone"),
    ("NPR", "Nepalesisk Rupie"),
    ("NZD", "Nya Zealand-dollar"),
    ("OMR", "Rial Omani"),
    ("PAB", "Balboa"),
    ("PEN", "Nuevo Sol"),
    ("PGK", "Kina"),
    ("PHP", "Filippinsk Peso"),
    ("PKR", "Pakistansk Rupie"),
    ("PLN", "Zloty"),
    ("PYG", "Guarani"),
    ("QAR", "Qatari Rial"),
    ("RON", "Rumänsk Leu"),
    ("RSD", "Serbisk Dinar"),
    ("RUB", "Rysk Rubel"),
    ("RWF", "Rwanda Franc"),
    ("SAR", "Saudi Riyal"),
    ("SBD", "Dollar från Salomonöarna"),
    ("SCR", "Seychell-rupie"),
    ("SDG", "Sudanesiskt pund"),
    ("SEK", "Svensk Krona"),
    ("SGD", "Singapore Dollar"),
    ("SHP", "Saint Helena pund"),
    ("SLL", "Leone"),
    ("SOS", "Somalisk Shilling"),
    ("SRD", "Surinam Dollar"),
    ("SSP", "Sydsudanesiskt pund"),
    ("STD", "Dobra"),
    ("SVC", "El Salvador Colon"),
    ("SYP", "Syriskt pund"),
    ("SZL", "Lilangeni"),
    ("THB", "Baht"),
    ("TJS", "Somoni"),
    ("TMT", "Turkmenistansk Ny Manat"),
    ("TND", "Tunisisk Dinar"),
    ("TOP", "Pa’anga"),
    ("TRY", "Turkisk Lira"),
    ("TTD", "Trinidad och Tobago Dollar"),
    ("TWD", "Ny Taiwanesisk Dollar"),
    ("TZS", "Tanzanisk Shilling"),
    ("UAH", "Hryvnia"),
    ("UGX", "Uganda Shilling"),
    ("USD", "US Dollar"),
    ("USN", "US Dollar (Nästa dag)"),
    ("UYI", "Uruguay Peso en Unidades Indexadas (URUIURUI)"),
    ("UYU", "Peso Uruguayo"),
    ("UZS", "Uzbekistansk Sum"),
    ("VEF", "Bolivar"),
    ("VND", "Dong"),
    ("VUV", "Vatu"),
    ("WST", "Tala"),
    ("XAF", "CFA Franc BEAC"),
    ("XCD", "East Caribbean Dollar"),
    ("XDR", "SDR (Särskild dragningsrätt)"),
    ("XOF", "CFA Franc BCEAO"),
    ("XPF", "CFP Franc"),
    ("XSU", "Sucre"),
    ("XUA", "ADB Beräkningsenhet"),
    ("YER", "Yemeni Rial"),
    ("ZAR", "Rand"),
    ("ZMW", "Zambian Kwacha"),
    ("ZWL", "Zimbabwe Dollar"),
)


class NumberValidator(RegexValidator):
    regex = r'[0-9]{10,}'


class FundsCommitmentAddForm(forms.ModelForm):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects,
                                           to_field_name='code')
    currency_code = forms.ChoiceField(choices=sorted(currencies, key=lambda tup: tup[1]))
    funds_commitment_number = forms.CharField(required=True)
    vendor_id = forms.CharField(validators=[NumberValidator,
                                            MinLengthValidator(10)])
    gl_account = forms.CharField(validators=[NumberValidator,
                                             MinLengthValidator(10)])

    class Meta:
        model = FundsCommitment
        exclude = ('update_date', 'updated_by', 'mis_sync_flag',
                   'mis_sync_date', 'ca_sync_date', 'ca_sync_flag')

    def clean_business_area(self):
        return self.cleaned_data['business_area'].code


@admin.register(FundsCommitment)
class FundsCommitmentAdmin(HOPEModelAdminBase):
    # list_display = ()
    list_filter = ("mis_sync_date", "ca_sync_date",
                   TextFieldFilter.factory('business_area'),
                   )
    date_hierarchy = "create_date"
    add_form = FundsCommitmentAddForm

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial['created_by'] = request.user.email
        initial['updated_by'] = request.user.email
        initial['posting_date'] = timezone.now()
        initial['status_date'] = timezone.now()
        return initial

    def get_form(self, request, obj=None, change=False, **kwargs):
        if not change:
            return FundsCommitmentAddForm
        return super().get_form(request, obj, change, **kwargs)


@admin.register(DownPayment)
class DownPaymentAdmin(HOPEModelAdminBase):
    list_filter = ("mis_sync_date", "ca_sync_date",
                   TextFieldFilter.factory('business_area'),
                   )
    date_hierarchy = "create_date"
