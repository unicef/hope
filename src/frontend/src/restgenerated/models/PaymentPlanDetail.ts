/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApprovalProcess } from './ApprovalProcess';
import type { BackgroundActionStatusEnum } from './BackgroundActionStatusEnum';
import type { CurrencyEnum } from './CurrencyEnum';
import type { DeliveryMechanism } from './DeliveryMechanism';
import type { DeliveryMechanismPerPaymentPlan } from './DeliveryMechanismPerPaymentPlan';
import type { FinancialServiceProvider } from './FinancialServiceProvider';
import type { FollowUpPaymentPlan } from './FollowUpPaymentPlan';
import type { PaymentPlanStatusEnum } from './PaymentPlanStatusEnum';
import type { PaymentPlanSupportingDocument } from './PaymentPlanSupportingDocument';
import type { PaymentVerificationPlan } from './PaymentVerificationPlan';
import type { ProgramCycleSmall } from './ProgramCycleSmall';
import type { ProgramSmall } from './ProgramSmall';
import type { RuleCommit } from './RuleCommit';
export type PaymentPlanDetail = {
    readonly id: string;
    unicefId?: string | null;
    /**
     * Name
     */
    name?: string | null;
    /**
     * Status [sys]
     *
     * * `TP_OPEN` - Open
     * * `TP_LOCKED` - Locked
     * * `PROCESSING` - Processing
     * * `STEFICON_WAIT` - Steficon Wait
     * * `STEFICON_RUN` - Steficon Run
     * * `STEFICON_COMPLETED` - Steficon Completed
     * * `STEFICON_ERROR` - Steficon Error
     * * `DRAFT` - Draft
     * * `PREPARING` - Preparing
     * * `OPEN` - Open
     * * `LOCKED` - Locked
     * * `LOCKED_FSP` - Locked FSP
     * * `IN_APPROVAL` - In Approval
     * * `IN_AUTHORIZATION` - In Authorization
     * * `IN_REVIEW` - In Review
     * * `ACCEPTED` - Accepted
     * * `FINISHED` - Finished
     */
    status?: PaymentPlanStatusEnum;
    /**
     * Total Households Count [sys]
     */
    totalHouseholdsCount?: number;
    /**
     * Total Individuals Count [sys]
     */
    totalIndividualsCount?: number;
    /**
     * Currency
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
    currency?: CurrencyEnum | null;
    /**
     * Targeting level exclusion IDs
     */
    excludedIds?: string | null;
    /**
     * Total Entitled Quantity [sys]
     */
    totalEntitledQuantity?: string | null;
    /**
     * Total Delivered Quantity [sys]
     */
    totalDeliveredQuantity?: string | null;
    /**
     * Total Undelivered Quantity [sys]
     */
    totalUndeliveredQuantity?: string | null;
    /**
     * Dispersion Start Date
     */
    dispersionStartDate?: string | null;
    /**
     * Dispersion End Date
     */
    dispersionEndDate?: string | null;
    /**
     * Follow Up Payment Plan flag [sys]
     */
    isFollowUp?: boolean;
    readonly followUps: Array<FollowUpPaymentPlan>;
    readonly createdBy: string;
    readonly createdAt: string;
    readonly updatedAt: string;
    /**
     * record revision number
     */
    version?: number;
    /**
     * Background Action Status for celery task [sys]
     *
     * * `RULE_ENGINE_RUN` - Rule Engine Running
     * * `RULE_ENGINE_ERROR` - Rule Engine Errored
     * * `XLSX_EXPORTING` - Exporting XLSX file
     * * `XLSX_EXPORT_ERROR` - Export XLSX file Error
     * * `XLSX_IMPORT_ERROR` - Import XLSX file Error
     * * `XLSX_IMPORTING_ENTITLEMENTS` - Importing Entitlements XLSX file
     * * `XLSX_IMPORTING_RECONCILIATION` - Importing Reconciliation XLSX file
     * * `EXCLUDE_BENEFICIARIES` - Exclude Beneficiaries Running
     * * `EXCLUDE_BENEFICIARIES_ERROR` - Exclude Beneficiaries Error
     * * `SEND_TO_PAYMENT_GATEWAY` - Sending to Payment Gateway
     * * `SEND_TO_PAYMENT_GATEWAY_ERROR` - Send to Payment Gateway Error
     */
    backgroundActionStatus?: BackgroundActionStatusEnum | null;
    backgroundActionStatusDisplay: string;
    /**
     * Payment Plan start date
     */
    startDate?: string | null;
    /**
     * Payment Plan end date
     */
    endDate?: string | null;
    readonly program: ProgramSmall;
    programCycle: ProgramCycleSmall;
    hasPaymentListExportFile: boolean;
    readonly hasFspDeliveryMechanismXlsxTemplate: boolean;
    importedFileName: string;
    /**
     * Imported File Date [sys]
     */
    importedFileDate?: string | null;
    readonly paymentsConflictsCount: number;
    readonly deliveryMechanism: DeliveryMechanism;
    readonly deliveryMechanismPerPaymentPlan: DeliveryMechanismPerPaymentPlan;
    readonly volumeByDeliveryMechanism: Record<string, any>;
    readonly splitChoices: Array<Record<string, any>>;
    /**
     * Exclusion reason (Targeting level)
     */
    exclusionReason?: string | null;
    /**
     * Exclusion reason (Targeting level) [sys]
     */
    excludeHouseholdError?: string | null;
    bankReconciliationSuccess: number;
    bankReconciliationError: number;
    canCreatePaymentVerificationPlan: boolean;
    readonly availablePaymentRecordsCount: number;
    readonly reconciliationSummary: Record<string, number>;
    readonly excludedHouseholds: Record<string, any>;
    readonly excludedIndividuals: Record<string, any>;
    readonly canCreateFollowUp: boolean;
    readonly totalWithdrawnHouseholdsCount: number;
    readonly unsuccessfulPaymentsCount: number;
    canSendToPaymentGateway: boolean;
    readonly canSplit: boolean;
    readonly supportingDocuments: Array<PaymentPlanSupportingDocument>;
    readonly totalHouseholdsCountWithValidPhoneNo: number;
    canCreateXlsxWithFspAuthCode: boolean;
    fspCommunicationChannel: string;
    readonly financialServiceProvider: FinancialServiceProvider;
    readonly canExportXlsx: boolean;
    readonly canDownloadXlsx: boolean;
    readonly canSendXlsxPassword: boolean;
    readonly approvalProcess: Array<ApprovalProcess>;
    /**
     * Total Entitled Quantity USD [sys]
     */
    totalEntitledQuantityUsd?: string | null;
    /**
     * Total Entitled Quantity Revised USD [sys]
     */
    totalEntitledQuantityRevisedUsd?: string | null;
    /**
     * Total Delivered Quantity USD [sys]
     */
    totalDeliveredQuantityUsd?: string | null;
    /**
     * Total Undelivered Quantity USD [sys]
     */
    totalUndeliveredQuantityUsd?: string | null;
    /**
     * Male Children Count [sys]
     */
    maleChildrenCount?: number;
    /**
     * Female Children Count [sys]
     */
    femaleChildrenCount?: number;
    /**
     * Male Adults Count [sys]
     */
    maleAdultsCount?: number;
    /**
     * Female Adults Count [sys]
     */
    femaleAdultsCount?: number;
    readonly steficonRule: RuleCommit;
    readonly sourcePaymentPlan: FollowUpPaymentPlan;
    /**
     * Exchange Rate [sys]
     */
    exchangeRate?: string | null;
    readonly eligiblePaymentsCount: number;
    readonly fundsCommitments: Record<string, any> | null;
    readonly availableFundsCommitments: Array<Record<string, any>>;
    readonly paymentVerificationPlans: Array<PaymentVerificationPlan>;
    readonly adminUrl: string;
};

