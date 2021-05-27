from django.utils.translation import gettext_lazy as _


AED = "AED"
AFN = "AFN"
ALL = "ALL"
AMD = "AMD"
ANG = "ANG"
AOA = "AOA"
ARS = "ARS"
AUD = "AUD"
AWG = "AWG"
AZN = "AZN"
BAM = "BAM"
BBD = "BBD"
BDT = "BDT"
BGN = "BGN"
BHD = "BHD"
BIF = "BIF"
BMD = "BMD"
BND = "BND"
BOB = "BOB"
BOV = "BOV"
BRL = "BRL"
BSD = "BSD"
BTN = "BTN"
BWP = "BWP"
BYN = "BYN"
BZD = "BZD"
CAD = "CAD"
CDF = "CDF"
CHF = "CHF"
CLP = "CLP"
CNY = "CNY"
COP = "COP"
CRC = "CRC"
CUC = "CUC"
CUP = "CUP"
CVE = "CVE"
CZK = "CZK"
DJF = "DJF"
DKK = "DKK"
DOP = "DOP"
DZD = "DZD"
EGP = "EGP"
ERN = "ERN"
ETB = "ETB"
EUR = "EUR"
FJD = "FJD"
FKP = "FKP"
GBP = "GBP"
GEL = "GEL"
GHS = "GHS"
GIP = "GIP"
GMD = "GMD"
GNF = "GNF"
GTQ = "GTQ"
GYD = "GYD"
HKD = "HKD"
HNL = "HNL"
HRK = "HRK"
HTG = "HTG"
HUF = "HUF"
IDR = "IDR"
ILS = "ILS"
INR = "INR"
IQD = "IQD"
IRR = "IRR"
ISK = "ISK"
JMD = "JMD"
JOD = "JOD"
JPY = "JPY"
KES = "KES"
KGS = "KGS"
KHR = "KHR"
KMF = "KMF"
KPW = "KPW"
KRW = "KRW"
KWD = "KWD"
KYD = "KYD"
KZT = "KZT"
LAK = "LAK"
LBP = "LBP"
LKR = "LKR"
LRD = "LRD"
LSL = "LSL"
LYD = "LYD"
MAD = "MAD"
MDL = "MDL"
MGA = "MGA"
MKD = "MKD"
MMK = "MMK"
MNT = "MNT"
MOP = "MOP"
MRU = "MRU"
MUR = "MUR"
MVR = "MVR"
MWK = "MWK"
MXN = "MXN"
MYR = "MYR"
MZN = "MZN"
NAD = "NAD"
NGN = "NGN"
NIO = "NIO"
NOK = "NOK"
NPR = "NPR"
NZD = "NZD"
OMR = "OMR"
PAB = "PAB"
PEN = "PEN"
PGK = "PGK"
PHP = "PHP"
PKR = "PKR"
PLN = "PLN"
PYG = "PYG"
QAR = "QAR"
RON = "RON"
RSD = "RSD"
RUB = "RUB"
RWF = "RWF"
SAR = "SAR"
SBD = "SBD"
SCR = "SCR"
SDG = "SDG"
SEK = "SEK"
SGD = "SGD"
SHP = "SHP"
SLL = "SLL"
SOS = "SOS"
SRD = "SRD"
SSP = "SSP"
STN = "STN"
SVC = "SVC"
SYP = "SYP"
SZL = "SZL"
THB = "THB"
TJS = "TJS"
TMT = "TMT"
TND = "TND"
TOP = "TOP"
TRY = "TRY"
TTD = "TTD"
TWD = "TWD"
TZS = "TZS"
UAH = "UAH"
UGX = "UGX"
USD = "USD"
UYU = "UYU"
UYW = "UYW"
UZS = "UZS"
VES = "VES"
VND = "VND"
VUV = "VUV"
WST = "WST"
XAF = "XAF"
XAG = "XAG"
XAU = "XAU"
XCD = "XCD"
XOF = "XOF"
XPF = "XPF"
YER = "YER"
ZAR = "ZAR"
ZMW = "ZMW"
ZWL = "ZWL"

CURRENCY_CHOICES = (
    ("", _("None")),
    (AED, _("United Arab Emirates dirham")),
    (AFN, _("Afghan afghani")),
    (ALL, _("Albanian lek")),
    (AMD, _("Armenian dram")),
    (ANG, _("Netherlands Antillean guilder")),
    (AOA, _("Angolan kwanza")),
    (ARS, _("Argentine peso")),
    (AUD, _("Australian dollar")),
    (AWG, _("Aruban florin")),
    (AZN, _("Azerbaijani manat")),
    (BAM, _("Bosnia and Herzegovina convertible mark")),
    (BBD, _("Barbados dollar")),
    (BDT, _("Bangladeshi taka")),
    (BGN, _("Bulgarian lev")),
    (BHD, _("Bahraini dinar")),
    (BIF, _("Burundian franc")),
    (BMD, _("Bermudian dollar")),
    (BND, _("Brunei dollar")),
    (BOB, _("Boliviano")),
    (BOV, _("Bolivian Mvdol (funds code)")),
    (BRL, _("Brazilian real")),
    (BSD, _("Bahamian dollar")),
    (BTN, _("Bhutanese ngultrum")),
    (BWP, _("Botswana pula")),
    (BYN, _("Belarusian ruble")),
    (BZD, _("Belize dollar")),
    (CAD, _("Canadian dollar")),
    (CDF, _("Congolese franc")),
    (CHF, _("Swiss franc")),
    (CLP, _("Chilean peso")),
    (CNY, _("Chinese yuan")),
    (COP, _("Colombian peso")),
    (CRC, _("Costa Rican colon")),
    (CUC, _("Cuban convertible peso")),
    (CUP, _("Cuban peso")),
    (CVE, _("Cape Verdean escudo")),
    (CZK, _("Czech koruna")),
    (DJF, _("Djiboutian franc")),
    (DKK, _("Danish krone")),
    (DOP, _("Dominican peso")),
    (DZD, _("Algerian dinar")),
    (EGP, _("Egyptian pound")),
    (ERN, _("Eritrean nakfa")),
    (ETB, _("Ethiopian birr")),
    (EUR, _("Euro")),
    (FJD, _("Fiji dollar")),
    (FKP, _("Falkland Islands pound")),
    (GBP, _("Pound sterling")),
    (GEL, _("Georgian lari")),
    (GHS, _("Ghanaian cedi")),
    (GIP, _("Gibraltar pound")),
    (GMD, _("Gambian dalasi")),
    (GNF, _("Guinean franc")),
    (GTQ, _("Guatemalan quetzal")),
    (GYD, _("Guyanese dollar")),
    (HKD, _("Hong Kong dollar")),
    (HNL, _("Honduran lempira")),
    (HRK, _("Croatian kuna")),
    (HTG, _("Haitian gourde")),
    (HUF, _("Hungarian forint")),
    (IDR, _("Indonesian rupiah")),
    (ILS, _("Israeli new shekel")),
    (INR, _("Indian rupee")),
    (IQD, _("Iraqi dinar")),
    (IRR, _("Iranian rial")),
    (ISK, _("Icelandic króna")),
    (JMD, _("Jamaican dollar")),
    (JOD, _("Jordanian dinar")),
    (JPY, _("Japanese yen")),
    (KES, _("Kenyan shilling")),
    (KGS, _("Kyrgyzstani som")),
    (KHR, _("Cambodian riel")),
    (KMF, _("Comoro franc")),
    (KPW, _("North Korean won")),
    (KRW, _("South Korean won")),
    (KWD, _("Kuwaiti dinar")),
    (KYD, _("Cayman Islands dollar")),
    (KZT, _("Kazakhstani tenge")),
    (LAK, _("Lao kip")),
    (LBP, _("Lebanese pound")),
    (LKR, _("Sri Lankan rupee")),
    (LRD, _("Liberian dollar")),
    (LSL, _("Lesotho loti")),
    (LYD, _("Libyan dinar")),
    (MAD, _("Moroccan dirham")),
    (MDL, _("Moldovan leu")),
    (MGA, _("Malagasy ariary")),
    (MKD, _("Macedonian denar")),
    (MMK, _("Myanmar kyat")),
    (MNT, _("Mongolian tögrög")),
    (MOP, _("Macanese pataca")),
    (MRU, _("Mauritanian ouguiya")),
    (MUR, _("Mauritian rupee")),
    (MVR, _("Maldivian rufiyaa")),
    (MWK, _("Malawian kwacha")),
    (MXN, _("Mexican peso")),
    (MYR, _("Malaysian ringgit")),
    (MZN, _("Mozambican metical")),
    (NAD, _("Namibian dollar")),
    (NGN, _("Nigerian naira")),
    (NIO, _("Nicaraguan córdoba")),
    (NOK, _("Norwegian krone")),
    (NPR, _("Nepalese rupee")),
    (NZD, _("New Zealand dollar")),
    (OMR, _("Omani rial")),
    (PAB, _("Panamanian balboa")),
    (PEN, _("Peruvian sol")),
    (PGK, _("Papua New Guinean kina")),
    (PHP, _("Philippine peso")),
    (PKR, _("Pakistani rupee")),
    (PLN, _("Polish złoty")),
    (PYG, _("Paraguayan guaraní")),
    (QAR, _("Qatari riyal")),
    (RON, _("Romanian leu")),
    (RSD, _("Serbian dinar")),
    (RUB, _("Russian ruble")),
    (RWF, _("Rwandan franc")),
    (SAR, _("Saudi riyal")),
    (SBD, _("Solomon Islands dollar")),
    (SCR, _("Seychelles rupee")),
    (SDG, _("Sudanese pound")),
    (SEK, _("Swedish krona/kronor")),
    (SGD, _("Singapore dollar")),
    (SHP, _("Saint Helena pound")),
    (SLL, _("Sierra Leonean leone")),
    (SOS, _("Somali shilling")),
    (SRD, _("Surinamese dollar")),
    (SSP, _("South Sudanese pound")),
    (STN, _("São Tomé and Príncipe dobra")),
    (SVC, _("Salvadoran colón")),
    (SYP, _("Syrian pound")),
    (SZL, _("Swazi lilangeni")),
    (THB, _("Thai baht")),
    (TJS, _("Tajikistani somoni")),
    (TMT, _("Turkmenistan manat")),
    (TND, _("Tunisian dinar")),
    (TOP, _("Tongan paʻanga")),
    (TRY, _("Turkish lira")),
    (TTD, _("Trinidad and Tobago dollar")),
    (TWD, _("New Taiwan dollar")),
    (TZS, _("Tanzanian shilling")),
    (UAH, _("Ukrainian hryvnia")),
    (UGX, _("Ugandan shilling")),
    (USD, _("United States dollar")),
    (UYU, _("Uruguayan peso")),
    (UYW, _("Unidad previsional[14]")),
    (UZS, _("Uzbekistan som")),
    (VES, _("Venezuelan bolívar soberano")),
    (VND, _("Vietnamese đồng")),
    (VUV, _("Vanuatu vatu")),
    (WST, _("Samoan tala")),
    (XAF, _("CFA franc BEAC")),
    (XAG, _("Silver (one troy ounce)")),
    (XAU, _("Gold (one troy ounce)")),
    (XCD, _("East Caribbean dollar")),
    (XOF, _("CFA franc BCEAO")),
    (XPF, _("CFP franc (franc Pacifique)")),
    (YER, _("Yemeni rial")),
    (ZAR, _("South African rand")),
    (ZMW, _("Zambian kwacha")),
    (ZWL, _("Zimbabwean dollar")),
)
