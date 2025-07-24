/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CollectTypeEnum } from './CollectTypeEnum';
import type { ConsentSharingEnum } from './ConsentSharingEnum';
import type { CountryEnum } from './CountryEnum';
import type { CountryOriginEnum } from './CountryOriginEnum';
import type { CurrencyEnum } from './CurrencyEnum';
import type { Individual } from './Individual';
import type { OrgEnumeratorEnum } from './OrgEnumeratorEnum';
import type { RdiMergeStatusEnum } from './RdiMergeStatusEnum';
import type { RegistrationMethodEnum } from './RegistrationMethodEnum';
import type { ResidenceStatusEnum } from './ResidenceStatusEnum';
export type Household = {
    firstRegistrationDate?: string;
    lastRegistrationDate?: string;
    members: Array<Individual>;
    country: CountryEnum;
    countryOrigin?: CountryOriginEnum;
    size?: number | null;
    consentSharing?: Array<ConsentSharingEnum>;
    village?: string | null;
    admin1?: string | null;
    admin2?: string | null;
    admin3?: string | null;
    admin4?: string | null;
    rdiMergeStatus?: RdiMergeStatusEnum;
    isRemoved?: boolean;
    removedDate?: string | null;
    readonly createdAt: string;
    readonly updatedAt: string;
    lastSyncAt?: string | null;
    internalData?: any;
    /**
     * Household consent sign image
     */
    consentSign?: string;
    /**
     * Household consent
     */
    consent?: boolean | null;
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
     * Household children count
     */
    childrenCount?: number | null;
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
     * Household male children disabled count
     */
    maleChildrenDisabledCount?: number | null;
    /**
     * Household female children disabled count
     */
    femaleChildrenDisabledCount?: number | null;
    /**
     * Household other sex group count
     */
    otherSexGroupCount?: number | null;
    /**
     * Household unknown sex group count
     */
    unknownSexGroupCount?: number | null;
    /**
     * Household returnee status
     */
    returnee?: boolean | null;
    /**
     * Female child headed household flag
     */
    fchildHoh?: boolean | null;
    /**
     * Child headed household flag
     */
    childHoh?: boolean | null;
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
     * Household unhcr id
     */
    unhcrId?: string;
    /**
     * Data collection start date
     */
    start?: string | null;
    /**
     * Household registration method [sys]
     *
     * * `` - None
     * * `COMMUNITY` - Community-level Registration
     * * `HH_REGISTRATION` - Household Registration
     */
    registrationMethod?: RegistrationMethodEnum;
    /**
     * Family ID eDopomoga household id [sys]
     */
    familyId?: string | null;
    /**
     * Household origin unicef id [sys]
     */
    originUnicefId?: string | null;
    /**
     * Household migration status [sys]
     */
    isMigrationHandled?: boolean;
    /**
     * Household migrated at [sys]
     */
    migratedAt?: string | null;
    /**
     * Household collect type [sys]
     *
     * * `STANDARD` - Standard
     * * `SINGLE` - Single
     */
    collectType?: CollectTypeEnum;
    /**
     * Beneficiary Program Registration id [sys]
     */
    programRegistrationId?: string | null;
    /**
     * Household cash received usd [sys]
     */
    totalCashReceivedUsd?: string | null;
    /**
     * Household cash received [sys]
     */
    totalCashReceived?: string | null;
    /**
     * Household flex fields [sys]
     */
    flexFields?: any;
    /**
     * Household withdrawn [sys]
     */
    withdrawn?: boolean;
    /**
     * Household withdrawn date [sys]
     */
    withdrawnDate?: string | null;
    /**
     * Household deviceid [sys]
     */
    deviceid?: string;
    /**
     * Household name enumerator [sys]
     */
    nameEnumerator?: string;
    /**
     * Household org enumerator [sys]
     *
     * * `` - None
     * * `PARTNER` - Partner
     * * `UNICEF` - UNICEF
     */
    orgEnumerator?: OrgEnumeratorEnum;
    /**
     * Household org name enumerator [sys]
     */
    orgNameEnumerator?: string;
    /**
     * Household enumerator record [sys]
     */
    enumeratorRecId?: number | null;
    /**
     * Household flex registrations record [sys]
     */
    flexRegistrationsRecordId?: number | null;
    /**
     * Key used to identify Collisions in the system
     */
    identificationKey?: string | null;
    /**
     * Flag used to identify if the household is in collision state
     */
    collisionFlag?: boolean;
    /**
     * Collection of household representations
     */
    householdCollection?: number | null;
    /**
     * Household storage object
     */
    storageObj?: number | null;
    /**
     * If this household was copied from another household, this field will contain the household it was copied from.
     */
    copiedFrom?: string | null;
    /**
     * This is only used to track collector (primary or secondary) of a household.
     * They may still be a HOH of this household or any other household.
     * Through model will contain the role (ROLE_CHOICE) they are connected with on.
     */
    readonly representatives: Array<string>;
    /**
     * This relation is filed when collision of Household happens.
     */
    extraRdis?: Array<string>;
};

