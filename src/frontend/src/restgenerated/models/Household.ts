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
    first_registration_date?: string;
    last_registration_date?: string;
    members: Array<Individual>;
    country: CountryEnum;
    country_origin?: CountryOriginEnum;
    size?: number | null;
    rdi_merge_status?: RdiMergeStatusEnum;
    is_removed?: boolean;
    removed_date?: string | null;
    readonly created_at: string;
    readonly updated_at: string;
    last_sync_at?: string | null;
    internal_data?: any;
    /**
     * Household consent sign image
     */
    consent_sign?: string;
    /**
     * Household consent
     */
    consent?: boolean | null;
    /**
     * Household consent sharing
     *
     * * `` - None
     * * `GOVERNMENT_PARTNER` - Government partners
     * * `HUMANITARIAN_PARTNER` - Humanitarian partners
     * * `PRIVATE_PARTNER` - Private partners
     * * `UNICEF` - UNICEF
     */
    consent_sharing?: ConsentSharingEnum;
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
    residence_status?: ResidenceStatusEnum;
    /**
     * Household address
     */
    address?: string;
    /**
     * Household zip code
     */
    zip_code?: string | null;
    /**
     * Household female age group 0-5
     */
    female_age_group_0_5_count?: number | null;
    /**
     * Household female age group 6-11
     */
    female_age_group_6_11_count?: number | null;
    /**
     * Household female age group 12-17
     */
    female_age_group_12_17_count?: number | null;
    /**
     * Household female age group 18-59
     */
    female_age_group_18_59_count?: number | null;
    /**
     * Household female age group 60
     */
    female_age_group_60_count?: number | null;
    /**
     * Household pregnant count
     */
    pregnant_count?: number | null;
    /**
     * Household male age group 0-5
     */
    male_age_group_0_5_count?: number | null;
    /**
     * Household male age group 6-11
     */
    male_age_group_6_11_count?: number | null;
    /**
     * Household male age group 12-17
     */
    male_age_group_12_17_count?: number | null;
    /**
     * Household male age group 18-59
     */
    male_age_group_18_59_count?: number | null;
    /**
     * Household male age group 60
     */
    male_age_group_60_count?: number | null;
    /**
     * Household female age group 0-5
     */
    female_age_group_0_5_disabled_count?: number | null;
    /**
     * Household female age group 6-11
     */
    female_age_group_6_11_disabled_count?: number | null;
    /**
     * Household female age group 12-17
     */
    female_age_group_12_17_disabled_count?: number | null;
    /**
     * Household female age group 18-59
     */
    female_age_group_18_59_disabled_count?: number | null;
    /**
     * Household female age group 60
     */
    female_age_group_60_disabled_count?: number | null;
    /**
     * Household male age group 0-5
     */
    male_age_group_0_5_disabled_count?: number | null;
    /**
     * Household male age group 6-1
     */
    male_age_group_6_11_disabled_count?: number | null;
    /**
     * Household male age group 12-17
     */
    male_age_group_12_17_disabled_count?: number | null;
    /**
     * Household male age group 18-59
     */
    male_age_group_18_59_disabled_count?: number | null;
    /**
     * Household male age group 60
     */
    male_age_group_60_disabled_count?: number | null;
    /**
     * Household children count
     */
    children_count?: number | null;
    /**
     * Household male children count
     */
    male_children_count?: number | null;
    /**
     * Household female children count
     */
    female_children_count?: number | null;
    /**
     * Household children disabled count
     */
    children_disabled_count?: number | null;
    /**
     * Household male children disabled count
     */
    male_children_disabled_count?: number | null;
    /**
     * Household female children disabled count
     */
    female_children_disabled_count?: number | null;
    /**
     * Household other sex group count
     */
    other_sex_group_count?: number | null;
    /**
     * Household unknown sex group count
     */
    unknown_sex_group_count?: number | null;
    /**
     * Household returnee status
     */
    returnee?: boolean | null;
    /**
     * Female child headed household flag
     */
    fchild_hoh?: boolean | null;
    /**
     * Child headed household flag
     */
    child_hoh?: boolean | null;
    /**
     * Household village
     */
    village?: string;
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
    unhcr_id?: string;
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
    registration_method?: RegistrationMethodEnum;
    /**
     * Family ID eDopomoga household id [sys]
     */
    family_id?: string | null;
    /**
     * Household origin unicef id [sys]
     */
    origin_unicef_id?: string | null;
    /**
     * Household migration status [sys]
     */
    is_migration_handled?: boolean;
    /**
     * Household migrated at [sys]
     */
    migrated_at?: string | null;
    /**
     * Household collect type [sys]
     *
     * * `STANDARD` - Standard
     * * `SINGLE` - Single
     */
    collect_type?: CollectTypeEnum;
    /**
     * Beneficiary Program Registration id [sys]
     */
    program_registration_id?: string | null;
    /**
     * Household cash received usd [sys]
     */
    total_cash_received_usd?: string | null;
    /**
     * Household cash received [sys]
     */
    total_cash_received?: string | null;
    /**
     * Household flex fields [sys]
     */
    flex_fields?: any;
    /**
     * Household withdrawn [sys]
     */
    withdrawn?: boolean;
    /**
     * Household withdrawn date [sys]
     */
    withdrawn_date?: string | null;
    /**
     * Household deviceid [sys]
     */
    deviceid?: string;
    /**
     * Household name enumerator [sys]
     */
    name_enumerator?: string;
    /**
     * Household org enumerator [sys]
     *
     * * `` - None
     * * `PARTNER` - Partner
     * * `UNICEF` - UNICEF
     */
    org_enumerator?: OrgEnumeratorEnum;
    /**
     * Household org name enumerator [sys]
     */
    org_name_enumerator?: string;
    /**
     * Household enumerator record [sys]
     */
    enumerator_rec_id?: number | null;
    /**
     * Household flex registrations record [sys]
     */
    flex_registrations_record_id?: number | null;
    /**
     * Collection of household representations
     */
    household_collection?: number | null;
    /**
     * Household storage object
     */
    storage_obj?: number | null;
    /**
     * If this household was copied from another household, this field will contain the household it was copied from.
     */
    copied_from?: string | null;
    /**
     * Household lowest administrative area
     */
    admin_area?: string | null;
    /**
     * Household administrative area level 1
     */
    admin1?: string | null;
    /**
     * Household administrative area level 2
     */
    admin2?: string | null;
    /**
     * Household administrative area level 3
     */
    admin3?: string | null;
    /**
     * Household administrative area level 4
     */
    admin4?: string | null;
    /**
     * This is only used to track collector (primary or secondary) of a household.
     * They may still be a HOH of this household or any other household.
     * Through model will contain the role (ROLE_CHOICE) they are connected with on.
     */
    readonly representatives: Array<string>;
};

