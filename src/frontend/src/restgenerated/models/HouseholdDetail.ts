/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CurrencyEnum } from './CurrencyEnum';
import type { HeadOfHousehold } from './HeadOfHousehold';
import type { RegistrationDataImport } from './RegistrationDataImport';
import type { ResidenceStatusEnum } from './ResidenceStatusEnum';
export type HouseholdDetail = {
    readonly id: string;
    unicefId: string | null;
    headOfHousehold: HeadOfHousehold;
    admin1?: string;
    admin2?: string;
    admin3?: string;
    admin4?: string;
    program: string;
    country?: string;
    countryOrigin?: string;
    readonly status: string;
    totalCashReceived: string;
    totalCashReceivedUsd: string;
    readonly sanctionListPossibleMatch: boolean;
    readonly sanctionListConfirmedMatch: boolean;
    readonly hasDuplicates: boolean;
    registrationDataImport: RegistrationDataImport;
    readonly flexFields: Record<string, any>;
    readonly linkedGrievances: Record<string, any>;
    readonly adminAreaTitle: string;
    readonly activeIndividualsCount: number;
    geopoint: string;
    readonly importId: string;
    readonly adminUrl: string;
    /**
     * Household male children count
     */
    maleChildrenCount?: number | null;
    /**
     * Household female children count
     */
    femaleChildrenCount?: number | null;
    /**
     * Household children disabled count
     */
    childrenDisabledCount?: number | null;
    /**
     * Household currency
     *
     * * `` - None
     * * `AED` - United Arab Emirates dirham
     * * `AFN` - Afghan afghani
     * * `ALL` - Albanian lek
     * * `AMD` - Armenian dram
     * * `ANG` - Netherlands Antillean guilder
     * * `AOA` - Angolan kwanza
     * * `ARS` - Argentine peso
     * * `AUD` - Australian dollar
     * * `AWG` - Aruban florin
     * * `AZN` - Azerbaijani manat
     * * `BAM` - Bosnia and Herzegovina convertible mark
     * * `BBD` - Barbados dollar
     * * `BDT` - Bangladeshi taka
     * * `BGN` - Bulgarian lev
     * * `BHD` - Bahraini dinar
     * * `BIF` - Burundian franc
     * * `BMD` - Bermudian dollar
     * * `BND` - Brunei dollar
     * * `BOB` - Boliviano
     * * `BOV` - Bolivian Mvdol (funds code)
     * * `BRL` - Brazilian real
     * * `BSD` - Bahamian dollar
     * * `BTN` - Bhutanese ngultrum
     * * `BWP` - Botswana pula
     * * `BYN` - Belarusian ruble
     * * `BZD` - Belize dollar
     * * `CAD` - Canadian dollar
     * * `CDF` - Congolese franc
     * * `CHF` - Swiss franc
     * * `CLP` - Chilean peso
     * * `CNY` - Chinese yuan
     * * `COP` - Colombian peso
     * * `CRC` - Costa Rican colon
     * * `CUC` - Cuban convertible peso
     * * `CUP` - Cuban peso
     * * `CVE` - Cape Verdean escudo
     * * `CZK` - Czech koruna
     * * `DJF` - Djiboutian franc
     * * `DKK` - Danish krone
     * * `DOP` - Dominican peso
     * * `DZD` - Algerian dinar
     * * `EGP` - Egyptian pound
     * * `ERN` - Eritrean nakfa
     * * `ETB` - Ethiopian birr
     * * `EUR` - Euro
     * * `FJD` - Fiji dollar
     * * `FKP` - Falkland Islands pound
     * * `GBP` - Pound sterling
     * * `GEL` - Georgian lari
     * * `GHS` - Ghanaian cedi
     * * `GIP` - Gibraltar pound
     * * `GMD` - Gambian dalasi
     * * `GNF` - Guinean franc
     * * `GTQ` - Guatemalan quetzal
     * * `GYD` - Guyanese dollar
     * * `HKD` - Hong Kong dollar
     * * `HNL` - Honduran lempira
     * * `HRK` - Croatian kuna
     * * `HTG` - Haitian gourde
     * * `HUF` - Hungarian forint
     * * `IDR` - Indonesian rupiah
     * * `ILS` - Israeli new shekel
     * * `INR` - Indian rupee
     * * `IQD` - Iraqi dinar
     * * `IRR` - Iranian rial
     * * `ISK` - Icelandic króna
     * * `JMD` - Jamaican dollar
     * * `JOD` - Jordanian dinar
     * * `JPY` - Japanese yen
     * * `KES` - Kenyan shilling
     * * `KGS` - Kyrgyzstani som
     * * `KHR` - Cambodian riel
     * * `KMF` - Comoro franc
     * * `KPW` - North Korean won
     * * `KRW` - South Korean won
     * * `KWD` - Kuwaiti dinar
     * * `KYD` - Cayman Islands dollar
     * * `KZT` - Kazakhstani tenge
     * * `LAK` - Lao kip
     * * `LBP` - Lebanese pound
     * * `LKR` - Sri Lankan rupee
     * * `LRD` - Liberian dollar
     * * `LSL` - Lesotho loti
     * * `LYD` - Libyan dinar
     * * `MAD` - Moroccan dirham
     * * `MDL` - Moldovan leu
     * * `MGA` - Malagasy ariary
     * * `MKD` - Macedonian denar
     * * `MMK` - Myanmar kyat
     * * `MNT` - Mongolian tögrög
     * * `MOP` - Macanese pataca
     * * `MRU` - Mauritanian ouguiya
     * * `MUR` - Mauritian rupee
     * * `MVR` - Maldivian rufiyaa
     * * `MWK` - Malawian kwacha
     * * `MXN` - Mexican peso
     * * `MYR` - Malaysian ringgit
     * * `MZN` - Mozambican metical
     * * `NAD` - Namibian dollar
     * * `NGN` - Nigerian naira
     * * `NIO` - Nicaraguan córdoba
     * * `NOK` - Norwegian krone
     * * `NPR` - Nepalese rupee
     * * `NZD` - New Zealand dollar
     * * `OMR` - Omani rial
     * * `PAB` - Panamanian balboa
     * * `PEN` - Peruvian sol
     * * `PGK` - Papua New Guinean kina
     * * `PHP` - Philippine peso
     * * `PKR` - Pakistani rupee
     * * `PLN` - Polish złoty
     * * `PYG` - Paraguayan guaraní
     * * `QAR` - Qatari riyal
     * * `RON` - Romanian leu
     * * `RSD` - Serbian dinar
     * * `RUB` - Russian ruble
     * * `RWF` - Rwandan franc
     * * `SAR` - Saudi riyal
     * * `SBD` - Solomon Islands dollar
     * * `SCR` - Seychelles rupee
     * * `SDG` - Sudanese pound
     * * `SEK` - Swedish krona/kronor
     * * `SGD` - Singapore dollar
     * * `SHP` - Saint Helena pound
     * * `SLE` - Sierra Leonean leone
     * * `SOS` - Somali shilling
     * * `SRD` - Surinamese dollar
     * * `SSP` - South Sudanese pound
     * * `STN` - São Tomé and Príncipe dobra
     * * `SVC` - Salvadoran colón
     * * `SYP` - Syrian pound
     * * `SZL` - Swazi lilangeni
     * * `THB` - Thai baht
     * * `TJS` - Tajikistani somoni
     * * `TMT` - Turkmenistan manat
     * * `TND` - Tunisian dinar
     * * `TOP` - Tongan paʻanga
     * * `TRY` - Turkish lira
     * * `TTD` - Trinidad and Tobago dollar
     * * `TWD` - New Taiwan dollar
     * * `TZS` - Tanzanian shilling
     * * `UAH` - Ukrainian hryvnia
     * * `UGX` - Ugandan shilling
     * * `USD` - United States dollar
     * * `UYU` - Uruguayan peso
     * * `UYW` - Unidad previsional[14]
     * * `UZS` - Uzbekistan som
     * * `VES` - Venezuelan bolívar soberano
     * * `VND` - Vietnamese đồng
     * * `VUV` - Vanuatu vatu
     * * `WST` - Samoan tala
     * * `XAF` - CFA franc BEAC
     * * `XAG` - Silver (one troy ounce)
     * * `XAU` - Gold (one troy ounce)
     * * `XCD` - East Caribbean dollar
     * * `XOF` - CFA franc BCEAO
     * * `XPF` - CFP franc (franc Pacifique)
     * * `YER` - Yemeni rial
     * * `ZAR` - South African rand
     * * `ZMW` - Zambian kwacha
     * * `ZWL` - Zimbabwean dollar
     * * `USDC` - USD Coin
     */
    currency?: CurrencyEnum;
    /**
     * Household first registration date [sys]
     */
    firstRegistrationDate: string;
    /**
     * Household last registration date [sys]
     */
    lastRegistrationDate: string;
    /**
     * Household unhcr id
     */
    unhcrId?: string;
    /**
     * Household village
     */
    village?: string;
    /**
     * Household address
     */
    address?: string;
    /**
     * Household zip code
     */
    zipCode?: string | null;
    /**
     * Household female age group 0-5
     */
    femaleAgeGroup05Count?: number | null;
    /**
     * Household female age group 6-11
     */
    femaleAgeGroup611Count?: number | null;
    /**
     * Household female age group 12-17
     */
    femaleAgeGroup1217Count?: number | null;
    /**
     * Household female age group 18-59
     */
    femaleAgeGroup1859Count?: number | null;
    /**
     * Household female age group 60
     */
    femaleAgeGroup60Count?: number | null;
    /**
     * Household pregnant count
     */
    pregnantCount?: number | null;
    /**
     * Household male age group 0-5
     */
    maleAgeGroup05Count?: number | null;
    /**
     * Household male age group 6-11
     */
    maleAgeGroup611Count?: number | null;
    /**
     * Household male age group 12-17
     */
    maleAgeGroup1217Count?: number | null;
    /**
     * Household male age group 18-59
     */
    maleAgeGroup1859Count?: number | null;
    /**
     * Household male age group 60
     */
    maleAgeGroup60Count?: number | null;
    /**
     * Household female age group 0-5
     */
    femaleAgeGroup05DisabledCount?: number | null;
    /**
     * Household female age group 6-11
     */
    femaleAgeGroup611DisabledCount?: number | null;
    /**
     * Household female age group 12-17
     */
    femaleAgeGroup1217DisabledCount?: number | null;
    /**
     * Household female age group 18-59
     */
    femaleAgeGroup1859DisabledCount?: number | null;
    /**
     * Household female age group 60
     */
    femaleAgeGroup60DisabledCount?: number | null;
    /**
     * Household male age group 0-5
     */
    maleAgeGroup05DisabledCount?: number | null;
    /**
     * Household male age group 6-1
     */
    maleAgeGroup611DisabledCount?: number | null;
    /**
     * Household male age group 12-17
     */
    maleAgeGroup1217DisabledCount?: number | null;
    /**
     * Household male age group 18-59
     */
    maleAgeGroup1859DisabledCount?: number | null;
    /**
     * Household male age group 60
     */
    maleAgeGroup60DisabledCount?: number | null;
    /**
     * Data collection start date
     */
    start?: string | null;
    /**
     * Household deviceid [sys]
     */
    deviceid?: string;
    /**
     * Female child headed household flag
     */
    fchildHoh?: boolean | null;
    /**
     * Child headed household flag
     */
    childHoh?: boolean | null;
    /**
     * Household returnee status
     */
    returnee?: boolean | null;
    /**
     * Household size
     */
    size?: number | null;
    /**
     * Household residence status
     *
     * * `` - None
     * * `IDP` - Displaced  |  Internally Displaced People
     * * `REFUGEE` - Displaced  |  Refugee / Asylum Seeker
     * * `OTHERS_OF_CONCERN` - Displaced  |  Others of Concern
     * * `HOST` - Non-displaced  |   Host
     * * `NON_HOST` - Non-displaced  |   Non-host
     * * `RETURNEE` - Displaced  |   Returnee
     */
    residenceStatus?: ResidenceStatusEnum;
    /**
     * Beneficiary Program Registration id [sys]
     */
    programRegistrationId?: string | null;
};

