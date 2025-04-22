/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AcceptanceProcess } from '../models/AcceptanceProcess';
import type { ApplyEngineFormula } from '../models/ApplyEngineFormula';
import type { BusinessArea } from '../models/BusinessArea';
import type { CountResponse } from '../models/CountResponse';
import type { DelegatePeople } from '../models/DelegatePeople';
import type { HouseholdDetail } from '../models/HouseholdDetail';
import type { HouseholdList } from '../models/HouseholdList';
import type { HouseholdMember } from '../models/HouseholdMember';
import type { IndividualDetail } from '../models/IndividualDetail';
import type { PaginatedAreaList } from '../models/PaginatedAreaList';
import type { PaginatedAreaListList } from '../models/PaginatedAreaListList';
import type { PaginatedAreaTypeList } from '../models/PaginatedAreaTypeList';
import type { PaginatedBeneficiaryGroupList } from '../models/PaginatedBeneficiaryGroupList';
import type { PaginatedBusinessAreaList } from '../models/PaginatedBusinessAreaList';
import type { PaginatedCountryList } from '../models/PaginatedCountryList';
import type { PaginatedHouseholdListList } from '../models/PaginatedHouseholdListList';
import type { PaginatedIndividualListList } from '../models/PaginatedIndividualListList';
import type { PaginatedOrganizationList } from '../models/PaginatedOrganizationList';
import type { PaginatedPaymentListList } from '../models/PaginatedPaymentListList';
import type { PaginatedPaymentPlanList } from '../models/PaginatedPaymentPlanList';
import type { PaginatedPaymentPlanListList } from '../models/PaginatedPaymentPlanListList';
import type { PaginatedPaymentVerificationPlanListList } from '../models/PaginatedPaymentVerificationPlanListList';
import type { PaginatedPeriodicDataUpdateTemplateListList } from '../models/PaginatedPeriodicDataUpdateTemplateListList';
import type { PaginatedPeriodicDataUpdateUploadListList } from '../models/PaginatedPeriodicDataUpdateUploadListList';
import type { PaginatedPeriodicFieldList } from '../models/PaginatedPeriodicFieldList';
import type { PaginatedProgramCycleListList } from '../models/PaginatedProgramCycleListList';
import type { PaginatedProgramGlobalList } from '../models/PaginatedProgramGlobalList';
import type { PaginatedProgramListList } from '../models/PaginatedProgramListList';
import type { PaginatedProjectList } from '../models/PaginatedProjectList';
import type { PaginatedRegistrationDataImportListList } from '../models/PaginatedRegistrationDataImportListList';
import type { PaginatedRegistrationList } from '../models/PaginatedRegistrationList';
import type { PaginatedRuleList } from '../models/PaginatedRuleList';
import type { PaginatedTargetPopulationListList } from '../models/PaginatedTargetPopulationListList';
import type { PaginatedTPHouseholdListList } from '../models/PaginatedTPHouseholdListList';
import type { PaginatedUserList } from '../models/PaginatedUserList';
import type { PatchedPaymentPlanCreateUpdate } from '../models/PatchedPaymentPlanCreateUpdate';
import type { PatchedPaymentVerificationPlanCreate } from '../models/PatchedPaymentVerificationPlanCreate';
import type { PatchedPaymentVerificationUpdate } from '../models/PatchedPaymentVerificationUpdate';
import type { PatchedProgramCycleUpdate } from '../models/PatchedProgramCycleUpdate';
import type { PatchedRDI } from '../models/PatchedRDI';
import type { PatchedTargetPopulationCreate } from '../models/PatchedTargetPopulationCreate';
import type { PaymentDetail } from '../models/PaymentDetail';
import type { PaymentPlan } from '../models/PaymentPlan';
import type { PaymentPlanBulkAction } from '../models/PaymentPlanBulkAction';
import type { PaymentPlanCreateFollowUp } from '../models/PaymentPlanCreateFollowUp';
import type { PaymentPlanCreateUpdate } from '../models/PaymentPlanCreateUpdate';
import type { PaymentPlanDetail } from '../models/PaymentPlanDetail';
import type { PaymentPlanExcludeBeneficiaries } from '../models/PaymentPlanExcludeBeneficiaries';
import type { PaymentPlanExportAuthCode } from '../models/PaymentPlanExportAuthCode';
import type { PaymentPlanImportFile } from '../models/PaymentPlanImportFile';
import type { PaymentPlanSupportingDocument } from '../models/PaymentPlanSupportingDocument';
import type { PaymentVerificationPlanActivate } from '../models/PaymentVerificationPlanActivate';
import type { PaymentVerificationPlanCreate } from '../models/PaymentVerificationPlanCreate';
import type { PaymentVerificationPlanDetails } from '../models/PaymentVerificationPlanDetails';
import type { PaymentVerificationPlanImport } from '../models/PaymentVerificationPlanImport';
import type { PeriodicDataUpdateTemplateCreate } from '../models/PeriodicDataUpdateTemplateCreate';
import type { PeriodicDataUpdateTemplateDetail } from '../models/PeriodicDataUpdateTemplateDetail';
import type { PeriodicDataUpdateUpload } from '../models/PeriodicDataUpdateUpload';
import type { PeriodicDataUpdateUploadDetail } from '../models/PeriodicDataUpdateUploadDetail';
import type { Profile } from '../models/Profile';
import type { ProgramAPI } from '../models/ProgramAPI';
import type { ProgramCycleCreate } from '../models/ProgramCycleCreate';
import type { ProgramCycleList } from '../models/ProgramCycleList';
import type { ProgramCycleUpdate } from '../models/ProgramCycleUpdate';
import type { ProgramDetail } from '../models/ProgramDetail';
import type { PushPeople } from '../models/PushPeople';
import type { RDI } from '../models/RDI';
import type { RDINested } from '../models/RDINested';
import type { RefuseRdi } from '../models/RefuseRdi';
import type { RegistrationDataImportDetail } from '../models/RegistrationDataImportDetail';
import type { RevertMarkPaymentAsFailed } from '../models/RevertMarkPaymentAsFailed';
import type { SplitPaymentPlan } from '../models/SplitPaymentPlan';
import type { TargetPopulationCopy } from '../models/TargetPopulationCopy';
import type { TargetPopulationCreate } from '../models/TargetPopulationCreate';
import type { TargetPopulationDetail } from '../models/TargetPopulationDetail';
import type { TPHouseholdList } from '../models/TPHouseholdList';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class RestService {
    /**
     * OpenApi3 schema for this API. Format can be selected via content negotiation.
     *
     * - YAML: application/vnd.oai.openapi
     * - JSON: application/vnd.oai.openapi+json
     * @returns any
     * @throws ApiError
     */
    public static restRetrieve({
        format,
        lang,
    }: {
        format?: 'json' | 'yaml',
        lang?: 'af' | 'ar' | 'ar-dz' | 'ast' | 'az' | 'be' | 'bg' | 'bn' | 'br' | 'bs' | 'ca' | 'cs' | 'cy' | 'da' | 'de' | 'dsb' | 'el' | 'en' | 'en-au' | 'en-gb' | 'eo' | 'es' | 'es-ar' | 'es-co' | 'es-mx' | 'es-ni' | 'es-ve' | 'et' | 'eu' | 'fa' | 'fi' | 'fr' | 'fy' | 'ga' | 'gd' | 'gl' | 'he' | 'hi' | 'hr' | 'hsb' | 'hu' | 'hy' | 'ia' | 'id' | 'ig' | 'io' | 'is' | 'it' | 'ja' | 'ka' | 'kab' | 'kk' | 'km' | 'kn' | 'ko' | 'ky' | 'lb' | 'lt' | 'lv' | 'mk' | 'ml' | 'mn' | 'mr' | 'my' | 'nb' | 'ne' | 'nl' | 'nn' | 'os' | 'pa' | 'pl' | 'pt' | 'pt-br' | 'ro' | 'ru' | 'sk' | 'sl' | 'sq' | 'sr' | 'sr-latn' | 'sv' | 'sw' | 'ta' | 'te' | 'tg' | 'th' | 'tk' | 'tr' | 'tt' | 'udm' | 'uk' | 'ur' | 'uz' | 'vi' | 'zh-hans' | 'zh-hant',
    }): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/',
            query: {
                'format': format,
                'lang': lang,
            },
        });
    }
    /**
     * @returns ProgramAPI
     * @throws ApiError
     */
    public static restProgramList({
        businessArea,
        ordering,
        updatedAtAfter,
        updatedAtBefore,
    }: {
        businessArea: string,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        updatedAtAfter?: string,
        updatedAtBefore?: string,
    }): CancelablePromise<Array<ProgramAPI>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/{business_area}/program/',
            path: {
                'business_area': businessArea,
            },
            query: {
                'ordering': ordering,
                'updated_at_after': updatedAtAfter,
                'updated_at_before': updatedAtBefore,
            },
        });
    }
    /**
     * @returns ProgramAPI
     * @throws ApiError
     */
    public static restProgramCreateCreate({
        businessArea,
        requestBody,
    }: {
        businessArea: string,
        requestBody: ProgramAPI,
    }): CancelablePromise<ProgramAPI> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/{business_area}/program/create/',
            path: {
                'business_area': businessArea,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Api to Create RDI for selected business area
     * @returns RDI
     * @throws ApiError
     */
    public static restRdiCompletedCreate({
        businessArea,
        rdi,
        requestBody,
    }: {
        businessArea: string,
        rdi: string,
        requestBody: RDI,
    }): CancelablePromise<RDI> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/{business_area}/rdi/{rdi}/completed/',
            path: {
                'business_area': businessArea,
                'rdi': rdi,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Api to Create RDI for selected business area
     * @returns RDI
     * @throws ApiError
     */
    public static restRdiCompletedUpdate({
        businessArea,
        rdi,
        requestBody,
    }: {
        businessArea: string,
        rdi: string,
        requestBody: RDI,
    }): CancelablePromise<RDI> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/rest/{business_area}/rdi/{rdi}/completed/',
            path: {
                'business_area': businessArea,
                'rdi': rdi,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Api to Create RDI for selected business area
     * @returns RDI
     * @throws ApiError
     */
    public static restRdiCompletedPartialUpdate({
        businessArea,
        rdi,
        requestBody,
    }: {
        businessArea: string,
        rdi: string,
        requestBody?: PatchedRDI,
    }): CancelablePromise<RDI> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/rest/{business_area}/rdi/{rdi}/completed/',
            path: {
                'business_area': businessArea,
                'rdi': rdi,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static restRdiDelegatePeopleCreate({
        businessArea,
        rdi,
        requestBody,
    }: {
        businessArea: string,
        rdi: string,
        requestBody: DelegatePeople,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/{business_area}/rdi/{rdi}/delegate/people/',
            path: {
                'business_area': businessArea,
                'rdi': rdi,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Api to link Households with selected RDI
     * @returns any No response body
     * @throws ApiError
     */
    public static restRdiPushCreate({
        businessArea,
        rdi,
    }: {
        businessArea: string,
        rdi: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/{business_area}/rdi/{rdi}/push/',
            path: {
                'business_area': businessArea,
                'rdi': rdi,
            },
        });
    }
    /**
     * Api to link Households with selected RDI
     * @returns any No response body
     * @throws ApiError
     */
    public static restRdiPushLaxCreate({
        businessArea,
        rdi,
    }: {
        businessArea: string,
        rdi: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/{business_area}/rdi/{rdi}/push/lax/',
            path: {
                'business_area': businessArea,
                'rdi': rdi,
            },
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static restRdiPushPeopleCreate({
        businessArea,
        rdi,
        requestBody,
    }: {
        businessArea: string,
        rdi: string,
        requestBody: PushPeople,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/{business_area}/rdi/{rdi}/push/people/',
            path: {
                'business_area': businessArea,
                'rdi': rdi,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Api to Create RDI for selected business area
     * @returns RDI
     * @throws ApiError
     */
    public static restRdiCreateCreate({
        businessArea,
        requestBody,
    }: {
        businessArea: string,
        requestBody: RDI,
    }): CancelablePromise<RDI> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/{business_area}/rdi/create/',
            path: {
                'business_area': businessArea,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static restRdiUploadCreate({
        businessArea,
        requestBody,
    }: {
        businessArea: string,
        requestBody: RDINested,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/{business_area}/rdi/upload/',
            path: {
                'business_area': businessArea,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @returns PaginatedAreaList
     * @throws ApiError
     */
    public static restAreasList({
        areaTypeAreaLevel,
        countryIsoCode2,
        countryIsoCode3,
        limit,
        offset,
        ordering,
        parentId,
        parentPCode,
        search,
        updatedAtAfter,
        updatedAtBefore,
        validFromAfter,
        validFromBefore,
        validUntilAfter,
        validUntilBefore,
    }: {
        areaTypeAreaLevel?: number,
        countryIsoCode2?: string,
        countryIsoCode3?: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        parentId?: string,
        parentPCode?: string,
        /**
         * A search term.
         */
        search?: string,
        updatedAtAfter?: string,
        updatedAtBefore?: string,
        validFromAfter?: string,
        validFromBefore?: string,
        validUntilAfter?: string,
        validUntilBefore?: string,
    }): CancelablePromise<PaginatedAreaList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/areas/',
            query: {
                'area_type_area_level': areaTypeAreaLevel,
                'country_iso_code2': countryIsoCode2,
                'country_iso_code3': countryIsoCode3,
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
                'parent_id': parentId,
                'parent_p_code': parentPCode,
                'search': search,
                'updated_at_after': updatedAtAfter,
                'updated_at_before': updatedAtBefore,
                'valid_from_after': validFromAfter,
                'valid_from_before': validFromBefore,
                'valid_until_after': validUntilAfter,
                'valid_until_before': validUntilBefore,
            },
        });
    }
    /**
     * @returns PaginatedAreaTypeList
     * @throws ApiError
     */
    public static restAreatypesList({
        areaLevel,
        countryIsoCode2,
        countryIsoCode3,
        limit,
        offset,
        ordering,
        parentAreaLevel,
        search,
        updatedAtAfter,
        updatedAtBefore,
    }: {
        areaLevel?: number,
        countryIsoCode2?: string,
        countryIsoCode3?: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        parentAreaLevel?: number,
        /**
         * A search term.
         */
        search?: string,
        updatedAtAfter?: string,
        updatedAtBefore?: string,
    }): CancelablePromise<PaginatedAreaTypeList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/areatypes/',
            query: {
                'area_level': areaLevel,
                'country_iso_code2': countryIsoCode2,
                'country_iso_code3': countryIsoCode3,
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
                'parent_area_level': parentAreaLevel,
                'search': search,
                'updated_at_after': updatedAtAfter,
                'updated_at_before': updatedAtBefore,
            },
        });
    }
    /**
     * @returns PaginatedBeneficiaryGroupList
     * @throws ApiError
     */
    public static restBeneficiaryGroupsList({
        limit,
        offset,
    }: {
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
    }): CancelablePromise<PaginatedBeneficiaryGroupList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/beneficiary-groups/',
            query: {
                'limit': limit,
                'offset': offset,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaginatedBusinessAreaList
     * @throws ApiError
     */
    public static restBusinessAreasList({
        limit,
        offset,
        ordering,
    }: {
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
    }): CancelablePromise<PaginatedBusinessAreaList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/',
            query: {
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
            },
        });
    }
    /**
     * @returns PaginatedAreaListList
     * @throws ApiError
     */
    public static restBusinessAreasGeoAreasList({
        businessAreaSlug,
        level,
        limit,
        name,
        offset,
        ordering,
        updatedAtAfter,
        updatedAtBefore,
    }: {
        businessAreaSlug: string,
        level?: number,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        name?: string,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        updatedAtAfter?: string,
        updatedAtBefore?: string,
    }): CancelablePromise<PaginatedAreaListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/geo/areas/',
            path: {
                'business_area_slug': businessAreaSlug,
            },
            query: {
                'level': level,
                'limit': limit,
                'name': name,
                'offset': offset,
                'ordering': ordering,
                'updated_at_after': updatedAtAfter,
                'updated_at_before': updatedAtBefore,
            },
        });
    }
    /**
     * Applies BusinessAreaMixin and also filters the queryset based on the user's partner's area limits.
     * @returns PaginatedHouseholdListList
     * @throws ApiError
     */
    public static restBusinessAreasHouseholdsList({
        businessAreaSlug,
        address,
        admin1,
        admin2,
        adminArea,
        countryOrigin,
        documentNumber,
        documentType,
        firstRegistrationDate,
        headOfHouseholdFullName,
        headOfHouseholdPhoneNoValid,
        isActiveProgram,
        lastRegistrationDateAfter,
        lastRegistrationDateBefore,
        limit,
        offset,
        orderBy,
        ordering,
        program,
        rdiId,
        rdiMergeStatus,
        residenceStatus,
        search,
        sizeGte,
        sizeLte,
        sizeRange,
        sizeMax,
        sizeMin,
        withdrawn,
    }: {
        businessAreaSlug: string,
        address?: string,
        admin1?: string,
        admin2?: string,
        adminArea?: string,
        countryOrigin?: string,
        documentNumber?: string,
        documentType?: string,
        firstRegistrationDate?: string,
        headOfHouseholdFullName?: string,
        headOfHouseholdPhoneNoValid?: boolean,
        isActiveProgram?: boolean,
        lastRegistrationDateAfter?: string,
        lastRegistrationDateBefore?: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Ordering
         *
         * * `age` - Age
         * * `-age` - Age (descending)
         * * `sex` - Sex
         * * `-sex` - Sex (descending)
         * * `household__id` - Household  id
         * * `-household__id` - Household  id (descending)
         * * `id` - Id
         * * `-id` - Id (descending)
         * * `unicef_id` - Unicef id
         * * `-unicef_id` - Unicef id (descending)
         * * `size` - Size
         * * `-size` - Size (descending)
         * * `status_label` - Status label
         * * `-status_label` - Status label (descending)
         * * `head_of_household__full_name` - Head of household  full name
         * * `-head_of_household__full_name` - Head of household  full name (descending)
         * * `admin_area__name` - Admin area  name
         * * `-admin_area__name` - Admin area  name (descending)
         * * `residence_status` - Residence status
         * * `-residence_status` - Residence status (descending)
         * * `registration_data_import__name` - Registration data import  name
         * * `-registration_data_import__name` - Registration data import  name (descending)
         * * `total_cash_received` - Total cash received
         * * `-total_cash_received` - Total cash received (descending)
         * * `last_registration_date` - Last registration date
         * * `-last_registration_date` - Last registration date (descending)
         * * `first_registration_date` - First registration date
         * * `-first_registration_date` - First registration date (descending)
         */
        orderBy?: Array<'-admin_area__name' | '-age' | '-first_registration_date' | '-head_of_household__full_name' | '-household__id' | '-id' | '-last_registration_date' | '-registration_data_import__name' | '-residence_status' | '-sex' | '-size' | '-status_label' | '-total_cash_received' | '-unicef_id' | 'admin_area__name' | 'age' | 'first_registration_date' | 'head_of_household__full_name' | 'household__id' | 'id' | 'last_registration_date' | 'registration_data_import__name' | 'residence_status' | 'sex' | 'size' | 'status_label' | 'total_cash_received' | 'unicef_id'>,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        program?: string,
        rdiId?: string,
        /**
         * * `PENDING` - Pending
         * * `MERGED` - Merged
         */
        rdiMergeStatus?: 'MERGED' | 'PENDING',
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
        residenceStatus?: '' | 'HOST' | 'IDP' | 'NON_HOST' | 'OTHERS_OF_CONCERN' | 'REFUGEE' | 'RETURNEE',
        search?: any,
        sizeGte?: number,
        sizeLte?: number,
        /**
         * Multiple values may be separated by commas.
         */
        sizeRange?: Array<number>,
        /**
         * Household size
         */
        sizeMax?: number | null,
        /**
         * Household size
         */
        sizeMin?: number | null,
        withdrawn?: boolean,
    }): CancelablePromise<PaginatedHouseholdListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/households/',
            path: {
                'business_area_slug': businessAreaSlug,
            },
            query: {
                'address': address,
                'admin1': admin1,
                'admin2': admin2,
                'admin_area': adminArea,
                'country_origin': countryOrigin,
                'document_number': documentNumber,
                'document_type': documentType,
                'first_registration_date': firstRegistrationDate,
                'head_of_household__full_name': headOfHouseholdFullName,
                'head_of_household__phone_no_valid': headOfHouseholdPhoneNoValid,
                'is_active_program': isActiveProgram,
                'last_registration_date_after': lastRegistrationDateAfter,
                'last_registration_date_before': lastRegistrationDateBefore,
                'limit': limit,
                'offset': offset,
                'order_by': orderBy,
                'ordering': ordering,
                'program': program,
                'rdi_id': rdiId,
                'rdi_merge_status': rdiMergeStatus,
                'residence_status': residenceStatus,
                'search': search,
                'size__gte': sizeGte,
                'size__lte': sizeLte,
                'size__range': sizeRange,
                'size_max': sizeMax,
                'size_min': sizeMin,
                'withdrawn': withdrawn,
            },
        });
    }
    /**
     * Applies BusinessAreaMixin and also filters the queryset based on the user's partner's area limits.
     * @returns CountResponse
     * @throws ApiError
     */
    public static restBusinessAreasHouseholdsCountRetrieve({
        businessAreaSlug,
    }: {
        businessAreaSlug: string,
    }): CancelablePromise<CountResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/households/count/',
            path: {
                'business_area_slug': businessAreaSlug,
            },
        });
    }
    /**
     * Applies BusinessAreaMixin and also filters the queryset based on the user's partner's area limits.
     * @returns PaginatedIndividualListList
     * @throws ApiError
     */
    public static restBusinessAreasIndividualsList({
        businessAreaSlug,
        admin1,
        admin2,
        ageMax,
        ageMin,
        documentNumber,
        documentType,
        duplicatesOnly,
        excludedId,
        flags,
        fullName,
        householdAdminArea,
        householdId,
        isActiveProgram,
        lastRegistrationDateAfter,
        lastRegistrationDateBefore,
        limit,
        offset,
        orderBy,
        ordering,
        program,
        rdiId,
        rdiMergeStatus,
        search,
        sex,
        status,
        withdrawn,
    }: {
        businessAreaSlug: string,
        admin1?: string,
        admin2?: string,
        ageMax?: string,
        ageMin?: string,
        documentNumber?: string,
        documentType?: string,
        duplicatesOnly?: boolean,
        excludedId?: any,
        /**
         * * `DUPLICATE` - Duplicate
         * * `NEEDS_ADJUDICATION` - Needs adjudication
         * * `SANCTION_LIST_CONFIRMED_MATCH` - Sanction list match
         * * `SANCTION_LIST_POSSIBLE_MATCH` - Sanction list possible match
         */
        flags?: Array<'DUPLICATE' | 'NEEDS_ADJUDICATION' | 'SANCTION_LIST_CONFIRMED_MATCH' | 'SANCTION_LIST_POSSIBLE_MATCH'>,
        fullName?: string,
        householdAdminArea?: string,
        householdId?: string,
        isActiveProgram?: boolean,
        lastRegistrationDateAfter?: string,
        lastRegistrationDateBefore?: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Ordering
         *
         * * `id` - Id
         * * `-id` - Id (descending)
         * * `unicef_id` - Unicef id
         * * `-unicef_id` - Unicef id (descending)
         * * `full_name` - Full name
         * * `-full_name` - Full name (descending)
         * * `household__id` - Household  id
         * * `-household__id` - Household  id (descending)
         * * `household__unicef_id` - Household  unicef id
         * * `-household__unicef_id` - Household  unicef id (descending)
         * * `birth_date` - Birth date
         * * `-birth_date` - Birth date (descending)
         * * `sex` - Sex
         * * `-sex` - Sex (descending)
         * * `relationship` - Relationship
         * * `-relationship` - Relationship (descending)
         * * `household__admin_area__name` - Household  admin area  name
         * * `-household__admin_area__name` - Household  admin area  name (descending)
         * * `last_registration_date` - Last registration date
         * * `-last_registration_date` - Last registration date (descending)
         * * `first_registration_date` - First registration date
         * * `-first_registration_date` - First registration date (descending)
         */
        orderBy?: Array<'-birth_date' | '-first_registration_date' | '-full_name' | '-household__admin_area__name' | '-household__id' | '-household__unicef_id' | '-id' | '-last_registration_date' | '-relationship' | '-sex' | '-unicef_id' | 'birth_date' | 'first_registration_date' | 'full_name' | 'household__admin_area__name' | 'household__id' | 'household__unicef_id' | 'id' | 'last_registration_date' | 'relationship' | 'sex' | 'unicef_id'>,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        program?: string,
        rdiId?: string,
        /**
         * * `PENDING` - Pending
         * * `MERGED` - Merged
         */
        rdiMergeStatus?: 'MERGED' | 'PENDING',
        search?: any,
        /**
         * Beneficiary gender
         *
         * * `MALE` - Male
         * * `FEMALE` - Female
         * * `OTHER` - Other
         * * `NOT_COLLECTED` - Not collected
         * * `NOT_ANSWERED` - Not answered
         */
        sex?: Array<'FEMALE' | 'MALE' | 'NOT_ANSWERED' | 'NOT_COLLECTED' | 'OTHER'>,
        /**
         * * `ACTIVE` - Active
         * * `DUPLICATE` - Duplicate
         * * `WITHDRAWN` - Withdrawn
         */
        status?: Array<'ACTIVE' | 'DUPLICATE' | 'WITHDRAWN'>,
        withdrawn?: boolean,
    }): CancelablePromise<PaginatedIndividualListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/individuals/',
            path: {
                'business_area_slug': businessAreaSlug,
            },
            query: {
                'admin1': admin1,
                'admin2': admin2,
                'age_max': ageMax,
                'age_min': ageMin,
                'document_number': documentNumber,
                'document_type': documentType,
                'duplicates_only': duplicatesOnly,
                'excluded_id': excludedId,
                'flags': flags,
                'full_name': fullName,
                'household__admin_area': householdAdminArea,
                'household__id': householdId,
                'is_active_program': isActiveProgram,
                'last_registration_date_after': lastRegistrationDateAfter,
                'last_registration_date_before': lastRegistrationDateBefore,
                'limit': limit,
                'offset': offset,
                'order_by': orderBy,
                'ordering': ordering,
                'program': program,
                'rdi_id': rdiId,
                'rdi_merge_status': rdiMergeStatus,
                'search': search,
                'sex': sex,
                'status': status,
                'withdrawn': withdrawn,
            },
        });
    }
    /**
     * Applies BusinessAreaMixin and also filters the queryset based on the user's partner's area limits.
     * @returns CountResponse
     * @throws ApiError
     */
    public static restBusinessAreasIndividualsCountRetrieve({
        businessAreaSlug,
    }: {
        businessAreaSlug: string,
    }): CancelablePromise<CountResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/individuals/count/',
            path: {
                'business_area_slug': businessAreaSlug,
            },
        });
    }
    /**
     * Applies BusinessAreaMixin and also filters the queryset based on the user's partner's permissions across programs.
     * @returns PaginatedPaymentPlanList
     * @throws ApiError
     */
    public static restBusinessAreasPaymentsPaymentPlansManagerialList({
        businessAreaSlug,
        deliveryMechanism,
        dispersionEndDateLte,
        dispersionStartDateGte,
        fsp,
        isFollowUp,
        limit,
        name,
        offset,
        ordering,
        paymentVerificationSummaryStatus,
        program,
        programCycle,
        programCycleEndDate,
        programCycleStartDate,
        search,
        status,
        totalEntitledQuantityGte,
        totalEntitledQuantityLte,
        updatedAtGte,
        updatedAtLte,
    }: {
        businessAreaSlug: string,
        deliveryMechanism?: Array<string>,
        dispersionEndDateLte?: string,
        dispersionStartDateGte?: string,
        fsp?: string,
        isFollowUp?: boolean,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        name?: string,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        /**
         * * `ACTIVE` - Active
         * * `FINISHED` - Finished
         * * `PENDING` - Pending
         */
        paymentVerificationSummaryStatus?: 'ACTIVE' | 'FINISHED' | 'PENDING',
        program?: string,
        programCycle?: string,
        programCycleEndDate?: string,
        programCycleStartDate?: string,
        /**
         * A search term.
         */
        search?: string,
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
        status?: 'ACCEPTED' | 'DRAFT' | 'FINISHED' | 'IN_APPROVAL' | 'IN_AUTHORIZATION' | 'IN_REVIEW' | 'LOCKED' | 'LOCKED_FSP' | 'OPEN' | 'PREPARING' | 'PROCESSING' | 'STEFICON_COMPLETED' | 'STEFICON_ERROR' | 'STEFICON_RUN' | 'STEFICON_WAIT' | 'TP_LOCKED' | 'TP_OPEN',
        totalEntitledQuantityGte?: number,
        totalEntitledQuantityLte?: number,
        updatedAtGte?: string,
        updatedAtLte?: string,
    }): CancelablePromise<PaginatedPaymentPlanList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/payments/payment-plans-managerial/',
            path: {
                'business_area_slug': businessAreaSlug,
            },
            query: {
                'delivery_mechanism': deliveryMechanism,
                'dispersion_end_date__lte': dispersionEndDateLte,
                'dispersion_start_date__gte': dispersionStartDateGte,
                'fsp': fsp,
                'is_follow_up': isFollowUp,
                'limit': limit,
                'name': name,
                'offset': offset,
                'ordering': ordering,
                'payment_verification_summary_status': paymentVerificationSummaryStatus,
                'program': program,
                'program_cycle': programCycle,
                'program_cycle_end_date': programCycleEndDate,
                'program_cycle_start_date': programCycleStartDate,
                'search': search,
                'status': status,
                'total_entitled_quantity__gte': totalEntitledQuantityGte,
                'total_entitled_quantity__lte': totalEntitledQuantityLte,
                'updated_at__gte': updatedAtGte,
                'updated_at__lte': updatedAtLte,
            },
        });
    }
    /**
     * Applies BusinessAreaMixin and also filters the queryset based on the user's partner's permissions across programs.
     * @returns PaymentPlanBulkAction
     * @throws ApiError
     */
    public static restBusinessAreasPaymentsPaymentPlansManagerialBulkActionCreate({
        businessAreaSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        requestBody: PaymentPlanBulkAction,
    }): CancelablePromise<PaymentPlanBulkAction> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/payments/payment-plans-managerial/bulk-action/',
            path: {
                'business_area_slug': businessAreaSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Base validation class, inherit from this class to create custom validators.
     * Your custom validators have to implement validation methods that starts
     * with name "validate_" so validate can call all the validators from your
     * custom validator.
     *
     * Custom validate method have to takes *args, **kwargs parameters.
     *
     * validate method with parameters have to be called in mutate method.
     * If there are validation errors they will be all
     * returned as one error message.
     * @returns PaginatedProgramListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsList({
        businessAreaSlug,
        beneficiaryGroupMatch,
        budgetMax,
        budgetMin,
        compatibleDct,
        dataCollectingType,
        endDate,
        limit,
        name,
        numberOfHouseholdsMax,
        numberOfHouseholdsMin,
        numberOfHouseholdsWithTpInProgramMax,
        numberOfHouseholdsWithTpInProgramMin,
        offset,
        orderBy,
        ordering,
        search,
        sector,
        startDate,
        status,
        updatedAtAfter,
        updatedAtBefore,
    }: {
        businessAreaSlug: string,
        beneficiaryGroupMatch?: string,
        /**
         * Program budget
         */
        budgetMax?: string,
        /**
         * Program budget
         */
        budgetMin?: string,
        compatibleDct?: string,
        dataCollectingType?: string,
        endDate?: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        name?: string,
        numberOfHouseholdsMax?: string,
        numberOfHouseholdsMin?: string,
        numberOfHouseholdsWithTpInProgramMax?: string,
        numberOfHouseholdsWithTpInProgramMin?: string,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Ordering
         *
         * * `name` - Name
         * * `-name` - Name (descending)
         * * `status` - Status
         * * `-status` - Status (descending)
         * * `start_date` - Start date
         * * `-start_date` - Start date (descending)
         * * `end_date` - End date
         * * `-end_date` - End date (descending)
         * * `sector` - Sector
         * * `-sector` - Sector (descending)
         * * `number_of_households` - Number of households
         * * `-number_of_households` - Number of households (descending)
         * * `budget` - Budget
         * * `-budget` - Budget (descending)
         */
        orderBy?: Array<'-budget' | '-end_date' | '-name' | '-number_of_households' | '-sector' | '-start_date' | '-status' | 'budget' | 'end_date' | 'name' | 'number_of_households' | 'sector' | 'start_date' | 'status'>,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        search?: any,
        /**
         * Program sector
         *
         * * `CHILD_PROTECTION` - Child Protection
         * * `EDUCATION` - Education
         * * `HEALTH` - Health
         * * `MULTI_PURPOSE` - Multi Purpose
         * * `NUTRITION` - Nutrition
         * * `SOCIAL_POLICY` - Social Policy
         * * `WASH` - WASH
         */
        sector?: Array<'CHILD_PROTECTION' | 'EDUCATION' | 'HEALTH' | 'MULTI_PURPOSE' | 'NUTRITION' | 'SOCIAL_POLICY' | 'WASH'>,
        startDate?: string,
        /**
         * Program status
         *
         * * `ACTIVE` - Active
         * * `DRAFT` - Draft
         * * `FINISHED` - Finished
         */
        status?: Array<'ACTIVE' | 'DRAFT' | 'FINISHED'>,
        updatedAtAfter?: string,
        updatedAtBefore?: string,
    }): CancelablePromise<PaginatedProgramListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/',
            path: {
                'business_area_slug': businessAreaSlug,
            },
            query: {
                'beneficiary_group_match': beneficiaryGroupMatch,
                'budget_max': budgetMax,
                'budget_min': budgetMin,
                'compatible_dct': compatibleDct,
                'data_collecting_type': dataCollectingType,
                'end_date': endDate,
                'limit': limit,
                'name': name,
                'number_of_households_max': numberOfHouseholdsMax,
                'number_of_households_min': numberOfHouseholdsMin,
                'number_of_households_with_tp_in_program_max': numberOfHouseholdsWithTpInProgramMax,
                'number_of_households_with_tp_in_program_min': numberOfHouseholdsWithTpInProgramMin,
                'offset': offset,
                'order_by': orderBy,
                'ordering': ordering,
                'search': search,
                'sector': sector,
                'start_date': startDate,
                'status': status,
                'updated_at_after': updatedAtAfter,
                'updated_at_before': updatedAtBefore,
            },
        });
    }
    /**
     * @returns PaginatedProgramCycleListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsCyclesList({
        businessAreaSlug,
        programSlug,
        endDate,
        limit,
        offset,
        ordering,
        program,
        search,
        startDate,
        status,
        title,
        totalDeliveredQuantityUsdFrom,
        totalDeliveredQuantityUsdTo,
        updatedAtAfter,
        updatedAtBefore,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        endDate?: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        program?: string,
        search?: any,
        startDate?: string,
        /**
         * * `DRAFT` - Draft
         * * `ACTIVE` - Active
         * * `FINISHED` - Finished
         */
        status?: Array<'ACTIVE' | 'DRAFT' | 'FINISHED'>,
        title?: string,
        totalDeliveredQuantityUsdFrom?: any,
        totalDeliveredQuantityUsdTo?: any,
        updatedAtAfter?: string,
        updatedAtBefore?: string,
    }): CancelablePromise<PaginatedProgramCycleListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/cycles/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
            query: {
                'end_date': endDate,
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
                'program': program,
                'search': search,
                'start_date': startDate,
                'status': status,
                'title': title,
                'total_delivered_quantity_usd_from': totalDeliveredQuantityUsdFrom,
                'total_delivered_quantity_usd_to': totalDeliveredQuantityUsdTo,
                'updated_at_after': updatedAtAfter,
                'updated_at_before': updatedAtBefore,
            },
        });
    }
    /**
     * @returns ProgramCycleCreate
     * @throws ApiError
     */
    public static restBusinessAreasProgramsCyclesCreate({
        businessAreaSlug,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        requestBody: ProgramCycleCreate,
    }): CancelablePromise<ProgramCycleCreate> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/cycles/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @returns ProgramCycleList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsCyclesRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Programme Cycle.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<ProgramCycleList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/cycles/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * @returns ProgramCycleUpdate
     * @throws ApiError
     */
    public static restBusinessAreasProgramsCyclesUpdate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Programme Cycle.
         */
        id: string,
        programSlug: string,
        requestBody?: ProgramCycleUpdate,
    }): CancelablePromise<ProgramCycleUpdate> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/cycles/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @returns ProgramCycleUpdate
     * @throws ApiError
     */
    public static restBusinessAreasProgramsCyclesPartialUpdate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Programme Cycle.
         */
        id: string,
        programSlug: string,
        requestBody?: PatchedProgramCycleUpdate,
    }): CancelablePromise<ProgramCycleUpdate> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/cycles/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @returns void
     * @throws ApiError
     */
    public static restBusinessAreasProgramsCyclesDestroy({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Programme Cycle.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/cycles/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static restBusinessAreasProgramsCyclesFinishCreate({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Programme Cycle.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/cycles/{id}/finish/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static restBusinessAreasProgramsCyclesReactivateCreate({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Programme Cycle.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/cycles/{id}/reactivate/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Applies ProgramMixin and also filters the queryset based on the user's partner's area limits for the program.
     * @returns PaginatedHouseholdListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsHouseholdsList({
        businessAreaSlug,
        programSlug,
        address,
        admin1,
        admin2,
        adminArea,
        countryOrigin,
        documentNumber,
        documentType,
        firstRegistrationDate,
        headOfHouseholdFullName,
        headOfHouseholdPhoneNoValid,
        isActiveProgram,
        lastRegistrationDateAfter,
        lastRegistrationDateBefore,
        limit,
        offset,
        orderBy,
        ordering,
        program,
        rdiId,
        rdiMergeStatus,
        residenceStatus,
        search,
        sizeGte,
        sizeLte,
        sizeRange,
        sizeMax,
        sizeMin,
        withdrawn,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        address?: string,
        admin1?: string,
        admin2?: string,
        adminArea?: string,
        countryOrigin?: string,
        documentNumber?: string,
        documentType?: string,
        firstRegistrationDate?: string,
        headOfHouseholdFullName?: string,
        headOfHouseholdPhoneNoValid?: boolean,
        isActiveProgram?: boolean,
        lastRegistrationDateAfter?: string,
        lastRegistrationDateBefore?: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Ordering
         *
         * * `age` - Age
         * * `-age` - Age (descending)
         * * `sex` - Sex
         * * `-sex` - Sex (descending)
         * * `household__id` - Household  id
         * * `-household__id` - Household  id (descending)
         * * `id` - Id
         * * `-id` - Id (descending)
         * * `unicef_id` - Unicef id
         * * `-unicef_id` - Unicef id (descending)
         * * `size` - Size
         * * `-size` - Size (descending)
         * * `status_label` - Status label
         * * `-status_label` - Status label (descending)
         * * `head_of_household__full_name` - Head of household  full name
         * * `-head_of_household__full_name` - Head of household  full name (descending)
         * * `admin_area__name` - Admin area  name
         * * `-admin_area__name` - Admin area  name (descending)
         * * `residence_status` - Residence status
         * * `-residence_status` - Residence status (descending)
         * * `registration_data_import__name` - Registration data import  name
         * * `-registration_data_import__name` - Registration data import  name (descending)
         * * `total_cash_received` - Total cash received
         * * `-total_cash_received` - Total cash received (descending)
         * * `last_registration_date` - Last registration date
         * * `-last_registration_date` - Last registration date (descending)
         * * `first_registration_date` - First registration date
         * * `-first_registration_date` - First registration date (descending)
         */
        orderBy?: Array<'-admin_area__name' | '-age' | '-first_registration_date' | '-head_of_household__full_name' | '-household__id' | '-id' | '-last_registration_date' | '-registration_data_import__name' | '-residence_status' | '-sex' | '-size' | '-status_label' | '-total_cash_received' | '-unicef_id' | 'admin_area__name' | 'age' | 'first_registration_date' | 'head_of_household__full_name' | 'household__id' | 'id' | 'last_registration_date' | 'registration_data_import__name' | 'residence_status' | 'sex' | 'size' | 'status_label' | 'total_cash_received' | 'unicef_id'>,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        program?: string,
        rdiId?: string,
        /**
         * * `PENDING` - Pending
         * * `MERGED` - Merged
         */
        rdiMergeStatus?: 'MERGED' | 'PENDING',
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
        residenceStatus?: '' | 'HOST' | 'IDP' | 'NON_HOST' | 'OTHERS_OF_CONCERN' | 'REFUGEE' | 'RETURNEE',
        search?: any,
        sizeGte?: number,
        sizeLte?: number,
        /**
         * Multiple values may be separated by commas.
         */
        sizeRange?: Array<number>,
        /**
         * Household size
         */
        sizeMax?: number | null,
        /**
         * Household size
         */
        sizeMin?: number | null,
        withdrawn?: boolean,
    }): CancelablePromise<PaginatedHouseholdListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/households/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
            query: {
                'address': address,
                'admin1': admin1,
                'admin2': admin2,
                'admin_area': adminArea,
                'country_origin': countryOrigin,
                'document_number': documentNumber,
                'document_type': documentType,
                'first_registration_date': firstRegistrationDate,
                'head_of_household__full_name': headOfHouseholdFullName,
                'head_of_household__phone_no_valid': headOfHouseholdPhoneNoValid,
                'is_active_program': isActiveProgram,
                'last_registration_date_after': lastRegistrationDateAfter,
                'last_registration_date_before': lastRegistrationDateBefore,
                'limit': limit,
                'offset': offset,
                'order_by': orderBy,
                'ordering': ordering,
                'program': program,
                'rdi_id': rdiId,
                'rdi_merge_status': rdiMergeStatus,
                'residence_status': residenceStatus,
                'search': search,
                'size__gte': sizeGte,
                'size__lte': sizeLte,
                'size__range': sizeRange,
                'size_max': sizeMax,
                'size_min': sizeMin,
                'withdrawn': withdrawn,
            },
        });
    }
    /**
     * Applies ProgramMixin and also filters the queryset based on the user's partner's area limits for the program.
     * @returns HouseholdDetail
     * @throws ApiError
     */
    public static restBusinessAreasProgramsHouseholdsRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Household.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<HouseholdDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/households/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Applies ProgramMixin and also filters the queryset based on the user's partner's area limits for the program.
     * @returns HouseholdMember
     * @throws ApiError
     */
    public static restBusinessAreasProgramsHouseholdsMembersRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Household.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<HouseholdMember> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/households/{id}/members/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Applies ProgramMixin and also filters the queryset based on the user's partner's area limits for the program.
     * @returns PaginatedPaymentListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsHouseholdsPaymentsList({
        businessAreaSlug,
        id,
        programSlug,
        address,
        admin1,
        admin2,
        adminArea,
        countryOrigin,
        documentNumber,
        documentType,
        firstRegistrationDate,
        headOfHouseholdFullName,
        headOfHouseholdPhoneNoValid,
        isActiveProgram,
        lastRegistrationDateAfter,
        lastRegistrationDateBefore,
        limit,
        offset,
        orderBy,
        ordering,
        program,
        rdiId,
        rdiMergeStatus,
        residenceStatus,
        search,
        sizeGte,
        sizeLte,
        sizeRange,
        sizeMax,
        sizeMin,
        withdrawn,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Household.
         */
        id: string,
        programSlug: string,
        address?: string,
        admin1?: string,
        admin2?: string,
        adminArea?: string,
        countryOrigin?: string,
        documentNumber?: string,
        documentType?: string,
        firstRegistrationDate?: string,
        headOfHouseholdFullName?: string,
        headOfHouseholdPhoneNoValid?: boolean,
        isActiveProgram?: boolean,
        lastRegistrationDateAfter?: string,
        lastRegistrationDateBefore?: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Ordering
         *
         * * `age` - Age
         * * `-age` - Age (descending)
         * * `sex` - Sex
         * * `-sex` - Sex (descending)
         * * `household__id` - Household  id
         * * `-household__id` - Household  id (descending)
         * * `id` - Id
         * * `-id` - Id (descending)
         * * `unicef_id` - Unicef id
         * * `-unicef_id` - Unicef id (descending)
         * * `size` - Size
         * * `-size` - Size (descending)
         * * `status_label` - Status label
         * * `-status_label` - Status label (descending)
         * * `head_of_household__full_name` - Head of household  full name
         * * `-head_of_household__full_name` - Head of household  full name (descending)
         * * `admin_area__name` - Admin area  name
         * * `-admin_area__name` - Admin area  name (descending)
         * * `residence_status` - Residence status
         * * `-residence_status` - Residence status (descending)
         * * `registration_data_import__name` - Registration data import  name
         * * `-registration_data_import__name` - Registration data import  name (descending)
         * * `total_cash_received` - Total cash received
         * * `-total_cash_received` - Total cash received (descending)
         * * `last_registration_date` - Last registration date
         * * `-last_registration_date` - Last registration date (descending)
         * * `first_registration_date` - First registration date
         * * `-first_registration_date` - First registration date (descending)
         */
        orderBy?: Array<'-admin_area__name' | '-age' | '-first_registration_date' | '-head_of_household__full_name' | '-household__id' | '-id' | '-last_registration_date' | '-registration_data_import__name' | '-residence_status' | '-sex' | '-size' | '-status_label' | '-total_cash_received' | '-unicef_id' | 'admin_area__name' | 'age' | 'first_registration_date' | 'head_of_household__full_name' | 'household__id' | 'id' | 'last_registration_date' | 'registration_data_import__name' | 'residence_status' | 'sex' | 'size' | 'status_label' | 'total_cash_received' | 'unicef_id'>,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        program?: string,
        rdiId?: string,
        /**
         * * `PENDING` - Pending
         * * `MERGED` - Merged
         */
        rdiMergeStatus?: 'MERGED' | 'PENDING',
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
        residenceStatus?: '' | 'HOST' | 'IDP' | 'NON_HOST' | 'OTHERS_OF_CONCERN' | 'REFUGEE' | 'RETURNEE',
        search?: any,
        sizeGte?: number,
        sizeLte?: number,
        /**
         * Multiple values may be separated by commas.
         */
        sizeRange?: Array<number>,
        /**
         * Household size
         */
        sizeMax?: number | null,
        /**
         * Household size
         */
        sizeMin?: number | null,
        withdrawn?: boolean,
    }): CancelablePromise<PaginatedPaymentListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/households/{id}/payments/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            query: {
                'address': address,
                'admin1': admin1,
                'admin2': admin2,
                'admin_area': adminArea,
                'country_origin': countryOrigin,
                'document_number': documentNumber,
                'document_type': documentType,
                'first_registration_date': firstRegistrationDate,
                'head_of_household__full_name': headOfHouseholdFullName,
                'head_of_household__phone_no_valid': headOfHouseholdPhoneNoValid,
                'is_active_program': isActiveProgram,
                'last_registration_date_after': lastRegistrationDateAfter,
                'last_registration_date_before': lastRegistrationDateBefore,
                'limit': limit,
                'offset': offset,
                'order_by': orderBy,
                'ordering': ordering,
                'program': program,
                'rdi_id': rdiId,
                'rdi_merge_status': rdiMergeStatus,
                'residence_status': residenceStatus,
                'search': search,
                'size__gte': sizeGte,
                'size__lte': sizeLte,
                'size__range': sizeRange,
                'size_max': sizeMax,
                'size_min': sizeMin,
                'withdrawn': withdrawn,
            },
        });
    }
    /**
     * Applies ProgramMixin and also filters the queryset based on the user's partner's area limits for the program.
     * @returns HouseholdList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsHouseholdsWithdrawCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Household.
         */
        id: string,
        programSlug: string,
        requestBody: HouseholdList,
    }): CancelablePromise<HouseholdList> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/households/{id}/withdraw/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Applies ProgramMixin and also filters the queryset based on the user's partner's area limits for the program.
     * @returns CountResponse
     * @throws ApiError
     */
    public static restBusinessAreasProgramsHouseholdsCountRetrieve({
        businessAreaSlug,
        programSlug,
    }: {
        businessAreaSlug: string,
        programSlug: string,
    }): CancelablePromise<CountResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/households/count/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Applies ProgramMixin and also filters the queryset based on the user's partner's area limits for the program.
     * @returns PaginatedIndividualListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsIndividualsList({
        businessAreaSlug,
        programSlug,
        admin1,
        admin2,
        ageMax,
        ageMin,
        documentNumber,
        documentType,
        duplicatesOnly,
        excludedId,
        flags,
        fullName,
        householdAdminArea,
        householdId,
        isActiveProgram,
        lastRegistrationDateAfter,
        lastRegistrationDateBefore,
        limit,
        offset,
        orderBy,
        ordering,
        program,
        rdiId,
        rdiMergeStatus,
        search,
        sex,
        status,
        withdrawn,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        admin1?: string,
        admin2?: string,
        ageMax?: string,
        ageMin?: string,
        documentNumber?: string,
        documentType?: string,
        duplicatesOnly?: boolean,
        excludedId?: any,
        /**
         * * `DUPLICATE` - Duplicate
         * * `NEEDS_ADJUDICATION` - Needs adjudication
         * * `SANCTION_LIST_CONFIRMED_MATCH` - Sanction list match
         * * `SANCTION_LIST_POSSIBLE_MATCH` - Sanction list possible match
         */
        flags?: Array<'DUPLICATE' | 'NEEDS_ADJUDICATION' | 'SANCTION_LIST_CONFIRMED_MATCH' | 'SANCTION_LIST_POSSIBLE_MATCH'>,
        fullName?: string,
        householdAdminArea?: string,
        householdId?: string,
        isActiveProgram?: boolean,
        lastRegistrationDateAfter?: string,
        lastRegistrationDateBefore?: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Ordering
         *
         * * `id` - Id
         * * `-id` - Id (descending)
         * * `unicef_id` - Unicef id
         * * `-unicef_id` - Unicef id (descending)
         * * `full_name` - Full name
         * * `-full_name` - Full name (descending)
         * * `household__id` - Household  id
         * * `-household__id` - Household  id (descending)
         * * `household__unicef_id` - Household  unicef id
         * * `-household__unicef_id` - Household  unicef id (descending)
         * * `birth_date` - Birth date
         * * `-birth_date` - Birth date (descending)
         * * `sex` - Sex
         * * `-sex` - Sex (descending)
         * * `relationship` - Relationship
         * * `-relationship` - Relationship (descending)
         * * `household__admin_area__name` - Household  admin area  name
         * * `-household__admin_area__name` - Household  admin area  name (descending)
         * * `last_registration_date` - Last registration date
         * * `-last_registration_date` - Last registration date (descending)
         * * `first_registration_date` - First registration date
         * * `-first_registration_date` - First registration date (descending)
         */
        orderBy?: Array<'-birth_date' | '-first_registration_date' | '-full_name' | '-household__admin_area__name' | '-household__id' | '-household__unicef_id' | '-id' | '-last_registration_date' | '-relationship' | '-sex' | '-unicef_id' | 'birth_date' | 'first_registration_date' | 'full_name' | 'household__admin_area__name' | 'household__id' | 'household__unicef_id' | 'id' | 'last_registration_date' | 'relationship' | 'sex' | 'unicef_id'>,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        program?: string,
        rdiId?: string,
        /**
         * * `PENDING` - Pending
         * * `MERGED` - Merged
         */
        rdiMergeStatus?: 'MERGED' | 'PENDING',
        search?: any,
        /**
         * Beneficiary gender
         *
         * * `MALE` - Male
         * * `FEMALE` - Female
         * * `OTHER` - Other
         * * `NOT_COLLECTED` - Not collected
         * * `NOT_ANSWERED` - Not answered
         */
        sex?: Array<'FEMALE' | 'MALE' | 'NOT_ANSWERED' | 'NOT_COLLECTED' | 'OTHER'>,
        /**
         * * `ACTIVE` - Active
         * * `DUPLICATE` - Duplicate
         * * `WITHDRAWN` - Withdrawn
         */
        status?: Array<'ACTIVE' | 'DUPLICATE' | 'WITHDRAWN'>,
        withdrawn?: boolean,
    }): CancelablePromise<PaginatedIndividualListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/individuals/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
            query: {
                'admin1': admin1,
                'admin2': admin2,
                'age_max': ageMax,
                'age_min': ageMin,
                'document_number': documentNumber,
                'document_type': documentType,
                'duplicates_only': duplicatesOnly,
                'excluded_id': excludedId,
                'flags': flags,
                'full_name': fullName,
                'household__admin_area': householdAdminArea,
                'household__id': householdId,
                'is_active_program': isActiveProgram,
                'last_registration_date_after': lastRegistrationDateAfter,
                'last_registration_date_before': lastRegistrationDateBefore,
                'limit': limit,
                'offset': offset,
                'order_by': orderBy,
                'ordering': ordering,
                'program': program,
                'rdi_id': rdiId,
                'rdi_merge_status': rdiMergeStatus,
                'search': search,
                'sex': sex,
                'status': status,
                'withdrawn': withdrawn,
            },
        });
    }
    /**
     * Applies ProgramMixin and also filters the queryset based on the user's partner's area limits for the program.
     * @returns IndividualDetail
     * @throws ApiError
     */
    public static restBusinessAreasProgramsIndividualsRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Individual.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<IndividualDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/individuals/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Applies ProgramMixin and also filters the queryset based on the user's partner's area limits for the program.
     * @returns CountResponse
     * @throws ApiError
     */
    public static restBusinessAreasProgramsIndividualsCountRetrieve({
        businessAreaSlug,
        programSlug,
    }: {
        businessAreaSlug: string,
        programSlug: string,
    }): CancelablePromise<CountResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/individuals/count/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaginatedPaymentPlanListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansList({
        businessAreaSlug,
        programSlug,
        deliveryMechanism,
        dispersionEndDateLte,
        dispersionStartDateGte,
        fsp,
        isFollowUp,
        limit,
        name,
        offset,
        ordering,
        paymentVerificationSummaryStatus,
        program,
        programCycle,
        programCycleEndDate,
        programCycleStartDate,
        search,
        status,
        totalEntitledQuantityGte,
        totalEntitledQuantityLte,
        updatedAtGte,
        updatedAtLte,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        deliveryMechanism?: Array<string>,
        dispersionEndDateLte?: string,
        dispersionStartDateGte?: string,
        fsp?: string,
        isFollowUp?: boolean,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        name?: string,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        /**
         * * `ACTIVE` - Active
         * * `FINISHED` - Finished
         * * `PENDING` - Pending
         */
        paymentVerificationSummaryStatus?: 'ACTIVE' | 'FINISHED' | 'PENDING',
        program?: string,
        programCycle?: string,
        programCycleEndDate?: string,
        programCycleStartDate?: string,
        /**
         * A search term.
         */
        search?: string,
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
        status?: 'ACCEPTED' | 'DRAFT' | 'FINISHED' | 'IN_APPROVAL' | 'IN_AUTHORIZATION' | 'IN_REVIEW' | 'LOCKED' | 'LOCKED_FSP' | 'OPEN' | 'PREPARING' | 'PROCESSING' | 'STEFICON_COMPLETED' | 'STEFICON_ERROR' | 'STEFICON_RUN' | 'STEFICON_WAIT' | 'TP_LOCKED' | 'TP_OPEN',
        totalEntitledQuantityGte?: number,
        totalEntitledQuantityLte?: number,
        updatedAtGte?: string,
        updatedAtLte?: string,
    }): CancelablePromise<PaginatedPaymentPlanListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
            query: {
                'delivery_mechanism': deliveryMechanism,
                'dispersion_end_date__lte': dispersionEndDateLte,
                'dispersion_start_date__gte': dispersionStartDateGte,
                'fsp': fsp,
                'is_follow_up': isFollowUp,
                'limit': limit,
                'name': name,
                'offset': offset,
                'ordering': ordering,
                'payment_verification_summary_status': paymentVerificationSummaryStatus,
                'program': program,
                'program_cycle': programCycle,
                'program_cycle_end_date': programCycleEndDate,
                'program_cycle_start_date': programCycleStartDate,
                'search': search,
                'status': status,
                'total_entitled_quantity__gte': totalEntitledQuantityGte,
                'total_entitled_quantity__lte': totalEntitledQuantityLte,
                'updated_at__gte': updatedAtGte,
                'updated_at__lte': updatedAtLte,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlanCreateUpdate
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansCreate({
        businessAreaSlug,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        requestBody: PaymentPlanCreateUpdate,
    }): CancelablePromise<PaymentPlanCreateUpdate> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaginatedPaymentListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansPaymentsList({
        businessAreaSlug,
        paymentPlanId,
        programSlug,
        limit,
        offset,
    }: {
        businessAreaSlug: string,
        paymentPlanId: string,
        programSlug: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
    }): CancelablePromise<PaginatedPaymentListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{payment_plan_id}/payments/',
            path: {
                'business_area_slug': businessAreaSlug,
                'payment_plan_id': paymentPlanId,
                'program_slug': programSlug,
            },
            query: {
                'limit': limit,
                'offset': offset,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentDetail
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansPaymentsRetrieve({
        businessAreaSlug,
        paymentId,
        paymentPlanId,
        programSlug,
    }: {
        businessAreaSlug: string,
        paymentId: string,
        paymentPlanId: string,
        programSlug: string,
    }): CancelablePromise<PaymentDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{payment_plan_id}/payments/{payment_id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'payment_id': paymentId,
                'payment_plan_id': paymentPlanId,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns any No response body
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansPaymentsMarkAsFailedRetrieve({
        businessAreaSlug,
        paymentId,
        paymentPlanId,
        programSlug,
    }: {
        businessAreaSlug: string,
        paymentId: string,
        paymentPlanId: string,
        programSlug: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{payment_plan_id}/payments/{payment_id}/mark-as-failed/',
            path: {
                'business_area_slug': businessAreaSlug,
                'payment_id': paymentId,
                'payment_plan_id': paymentPlanId,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns RevertMarkPaymentAsFailed
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansPaymentsRevertMarkAsFailedCreate({
        businessAreaSlug,
        paymentId,
        paymentPlanId,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        paymentId: string,
        paymentPlanId: string,
        programSlug: string,
        requestBody: RevertMarkPaymentAsFailed,
    }): CancelablePromise<RevertMarkPaymentAsFailed> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{payment_plan_id}/payments/{payment_id}/revert-mark-as-failed/',
            path: {
                'business_area_slug': businessAreaSlug,
                'payment_id': paymentId,
                'payment_plan_id': paymentPlanId,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns CountResponse
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansPaymentsCountRetrieve({
        businessAreaSlug,
        paymentPlanId,
        programSlug,
    }: {
        businessAreaSlug: string,
        paymentPlanId: string,
        programSlug: string,
    }): CancelablePromise<CountResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{payment_plan_id}/payments/count/',
            path: {
                'business_area_slug': businessAreaSlug,
                'payment_plan_id': paymentPlanId,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * @returns PaymentPlanSupportingDocument
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansSupportingDocumentsCreate({
        businessAreaSlug,
        paymentPlanId,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        paymentPlanId: string,
        programSlug: string,
        requestBody: PaymentPlanSupportingDocument,
    }): CancelablePromise<PaymentPlanSupportingDocument> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{payment_plan_id}/supporting-documents/',
            path: {
                'business_area_slug': businessAreaSlug,
                'payment_plan_id': paymentPlanId,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @returns void
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansSupportingDocumentsDestroy({
        businessAreaSlug,
        fileId,
        paymentPlanId,
        programSlug,
    }: {
        businessAreaSlug: string,
        fileId: string,
        paymentPlanId: string,
        programSlug: string,
    }): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{payment_plan_id}/supporting-documents/{file_id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'file_id': fileId,
                'payment_plan_id': paymentPlanId,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * @returns PaymentPlanSupportingDocument
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansSupportingDocumentsDownloadRetrieve({
        businessAreaSlug,
        fileId,
        paymentPlanId,
        programSlug,
    }: {
        businessAreaSlug: string,
        fileId: string,
        paymentPlanId: string,
        programSlug: string,
    }): CancelablePromise<PaymentPlanSupportingDocument> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{payment_plan_id}/supporting-documents/{file_id}/download/',
            path: {
                'business_area_slug': businessAreaSlug,
                'file_id': fileId,
                'payment_plan_id': paymentPlanId,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlanDetail
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<PaymentPlanDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlanCreateUpdate
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansPartialUpdate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        requestBody?: PatchedPaymentPlanCreateUpdate,
    }): CancelablePromise<PaymentPlanCreateUpdate> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns void
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansDestroy({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlanDetail
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansApplyEngineFormulaCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        requestBody: ApplyEngineFormula,
    }): CancelablePromise<PaymentPlanDetail> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/apply-engine-formula/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns AcceptanceProcess
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansApproveCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        requestBody?: AcceptanceProcess,
    }): CancelablePromise<AcceptanceProcess> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/approve/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns AcceptanceProcess
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansAuthorizeCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        requestBody?: AcceptanceProcess,
    }): CancelablePromise<AcceptanceProcess> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/authorize/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlanDetail
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansCreateFollowUpCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        requestBody: PaymentPlanCreateFollowUp,
    }): CancelablePromise<PaymentPlanDetail> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/create-follow-up/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlan
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansEntitlementExportXlsxRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<PaymentPlan> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/entitlement-export-xlsx/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlanDetail
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansEntitlementImportXlsxCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        requestBody: PaymentPlanImportFile,
    }): CancelablePromise<PaymentPlanDetail> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/entitlement-import-xlsx/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlanDetail
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansExcludeBeneficiariesCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        requestBody: PaymentPlanExcludeBeneficiaries,
    }): CancelablePromise<PaymentPlanDetail> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/exclude-beneficiaries/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlan
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansExportPdfPaymentPlanSummaryRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<PaymentPlan> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/export-pdf-payment-plan-summary/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlanExportAuthCode
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansGenerateXlsxWithAuthCodeCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        requestBody: PaymentPlanExportAuthCode,
    }): CancelablePromise<PaymentPlanExportAuthCode> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/generate-xlsx-with-auth-code/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlan
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansLockRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<PaymentPlan> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/lock/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlan
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansLockFspRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<PaymentPlan> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/lock-fsp/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns AcceptanceProcess
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansMarkAsReleasedCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        requestBody?: AcceptanceProcess,
    }): CancelablePromise<AcceptanceProcess> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/mark-as-released/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlan
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansReconciliationExportXlsxRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<PaymentPlan> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/reconciliation-export-xlsx/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlanDetail
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansReconciliationImportXlsxCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        requestBody: PaymentPlanImportFile,
    }): CancelablePromise<PaymentPlanDetail> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/reconciliation-import-xlsx/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns AcceptanceProcess
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansRejectCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        requestBody?: AcceptanceProcess,
    }): CancelablePromise<AcceptanceProcess> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/reject/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlan
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansSendForApprovalRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<PaymentPlan> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/send-for-approval/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlan
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansSendToPaymentGatewayRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<PaymentPlan> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/send-to-payment-gateway/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlan
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansSendXlsxPasswordRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<PaymentPlan> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/send-xlsx-password/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns SplitPaymentPlan
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansSplitCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        requestBody: SplitPaymentPlan,
    }): CancelablePromise<SplitPaymentPlan> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/split/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlan
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansUnlockRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<PaymentPlan> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/unlock/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlan
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansUnlockFspRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<PaymentPlan> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/{id}/unlock-fsp/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns CountResponse
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentPlansCountRetrieve({
        businessAreaSlug,
        programSlug,
    }: {
        businessAreaSlug: string,
        programSlug: string,
    }): CancelablePromise<CountResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-plans/count/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaginatedPaymentVerificationPlanListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentVerificationsList({
        businessAreaSlug,
        programSlug,
        deliveryMechanism,
        dispersionEndDateLte,
        dispersionStartDateGte,
        fsp,
        isFollowUp,
        limit,
        name,
        offset,
        ordering,
        paymentVerificationSummaryStatus,
        program,
        programCycle,
        programCycleEndDate,
        programCycleStartDate,
        search,
        status,
        totalEntitledQuantityGte,
        totalEntitledQuantityLte,
        updatedAtGte,
        updatedAtLte,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        deliveryMechanism?: Array<string>,
        dispersionEndDateLte?: string,
        dispersionStartDateGte?: string,
        fsp?: string,
        isFollowUp?: boolean,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        name?: string,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        /**
         * * `ACTIVE` - Active
         * * `FINISHED` - Finished
         * * `PENDING` - Pending
         */
        paymentVerificationSummaryStatus?: 'ACTIVE' | 'FINISHED' | 'PENDING',
        program?: string,
        programCycle?: string,
        programCycleEndDate?: string,
        programCycleStartDate?: string,
        /**
         * A search term.
         */
        search?: string,
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
        status?: 'ACCEPTED' | 'DRAFT' | 'FINISHED' | 'IN_APPROVAL' | 'IN_AUTHORIZATION' | 'IN_REVIEW' | 'LOCKED' | 'LOCKED_FSP' | 'OPEN' | 'PREPARING' | 'PROCESSING' | 'STEFICON_COMPLETED' | 'STEFICON_ERROR' | 'STEFICON_RUN' | 'STEFICON_WAIT' | 'TP_LOCKED' | 'TP_OPEN',
        totalEntitledQuantityGte?: number,
        totalEntitledQuantityLte?: number,
        updatedAtGte?: string,
        updatedAtLte?: string,
    }): CancelablePromise<PaginatedPaymentVerificationPlanListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-verifications/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
            query: {
                'delivery_mechanism': deliveryMechanism,
                'dispersion_end_date__lte': dispersionEndDateLte,
                'dispersion_start_date__gte': dispersionStartDateGte,
                'fsp': fsp,
                'is_follow_up': isFollowUp,
                'limit': limit,
                'name': name,
                'offset': offset,
                'ordering': ordering,
                'payment_verification_summary_status': paymentVerificationSummaryStatus,
                'program': program,
                'program_cycle': programCycle,
                'program_cycle_end_date': programCycleEndDate,
                'program_cycle_start_date': programCycleStartDate,
                'search': search,
                'status': status,
                'total_entitled_quantity__gte': totalEntitledQuantityGte,
                'total_entitled_quantity__lte': totalEntitledQuantityLte,
                'updated_at__gte': updatedAtGte,
                'updated_at__lte': updatedAtLte,
            },
        });
    }
    /**
     * return list of verification records
     * @returns PaginatedPaymentListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentVerificationsVerificationsList({
        businessAreaSlug,
        paymentVerificationPk,
        programSlug,
        deliveryMechanism,
        dispersionEndDateLte,
        dispersionStartDateGte,
        fsp,
        isFollowUp,
        limit,
        name,
        offset,
        ordering,
        paymentVerificationSummaryStatus,
        program,
        programCycle,
        programCycleEndDate,
        programCycleStartDate,
        search,
        status,
        totalEntitledQuantityGte,
        totalEntitledQuantityLte,
        updatedAtGte,
        updatedAtLte,
    }: {
        businessAreaSlug: string,
        paymentVerificationPk: string,
        programSlug: string,
        deliveryMechanism?: Array<string>,
        dispersionEndDateLte?: string,
        dispersionStartDateGte?: string,
        fsp?: string,
        isFollowUp?: boolean,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        name?: string,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        /**
         * * `ACTIVE` - Active
         * * `FINISHED` - Finished
         * * `PENDING` - Pending
         */
        paymentVerificationSummaryStatus?: 'ACTIVE' | 'FINISHED' | 'PENDING',
        program?: string,
        programCycle?: string,
        programCycleEndDate?: string,
        programCycleStartDate?: string,
        /**
         * A search term.
         */
        search?: string,
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
        status?: 'ACCEPTED' | 'DRAFT' | 'FINISHED' | 'IN_APPROVAL' | 'IN_AUTHORIZATION' | 'IN_REVIEW' | 'LOCKED' | 'LOCKED_FSP' | 'OPEN' | 'PREPARING' | 'PROCESSING' | 'STEFICON_COMPLETED' | 'STEFICON_ERROR' | 'STEFICON_RUN' | 'STEFICON_WAIT' | 'TP_LOCKED' | 'TP_OPEN',
        totalEntitledQuantityGte?: number,
        totalEntitledQuantityLte?: number,
        updatedAtGte?: string,
        updatedAtLte?: string,
    }): CancelablePromise<PaginatedPaymentListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-verifications/{payment_verification_pk}/verifications/',
            path: {
                'business_area_slug': businessAreaSlug,
                'payment_verification_pk': paymentVerificationPk,
                'program_slug': programSlug,
            },
            query: {
                'delivery_mechanism': deliveryMechanism,
                'dispersion_end_date__lte': dispersionEndDateLte,
                'dispersion_start_date__gte': dispersionStartDateGte,
                'fsp': fsp,
                'is_follow_up': isFollowUp,
                'limit': limit,
                'name': name,
                'offset': offset,
                'ordering': ordering,
                'payment_verification_summary_status': paymentVerificationSummaryStatus,
                'program': program,
                'program_cycle': programCycle,
                'program_cycle_end_date': programCycleEndDate,
                'program_cycle_start_date': programCycleStartDate,
                'search': search,
                'status': status,
                'total_entitled_quantity__gte': totalEntitledQuantityGte,
                'total_entitled_quantity__lte': totalEntitledQuantityLte,
                'updated_at__gte': updatedAtGte,
                'updated_at__lte': updatedAtLte,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentDetail
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentVerificationsVerificationsRetrieve({
        businessAreaSlug,
        id,
        paymentVerificationPk,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        paymentVerificationPk: string,
        programSlug: string,
    }): CancelablePromise<PaymentDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-verifications/{payment_verification_pk}/verifications/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'payment_verification_pk': paymentVerificationPk,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * update verification amount
     * @returns PaymentDetail
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentVerificationsVerificationsPartialUpdate({
        businessAreaSlug,
        id,
        paymentVerificationPk,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        paymentVerificationPk: string,
        programSlug: string,
        requestBody?: PatchedPaymentVerificationUpdate,
    }): CancelablePromise<PaymentDetail> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-verifications/{payment_verification_pk}/verifications/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'payment_verification_pk': paymentVerificationPk,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns CountResponse
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentVerificationsVerificationsCountRetrieve({
        businessAreaSlug,
        paymentVerificationPk,
        programSlug,
    }: {
        businessAreaSlug: string,
        paymentVerificationPk: string,
        programSlug: string,
    }): CancelablePromise<CountResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-verifications/{payment_verification_pk}/verifications/count/',
            path: {
                'business_area_slug': businessAreaSlug,
                'payment_verification_pk': paymentVerificationPk,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentVerificationPlanDetails
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentVerificationsRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<PaymentVerificationPlanDetails> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-verifications/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentVerificationPlanDetails
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentVerificationsActivateVerificationPlanCreate({
        businessAreaSlug,
        id,
        programSlug,
        verificationPlanId,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        verificationPlanId: string,
        requestBody?: PaymentVerificationPlanActivate,
    }): CancelablePromise<PaymentVerificationPlanDetails> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-verifications/{id}/activate-verification-plan/{verification_plan_id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
                'verification_plan_id': verificationPlanId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Create Payment Verification Plan
     * @returns PaymentVerificationPlanDetails
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentVerificationsCreateVerificationPlanCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        requestBody: PaymentVerificationPlanCreate,
    }): CancelablePromise<PaymentVerificationPlanDetails> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-verifications/{id}/create-verification-plan/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentVerificationPlanDetails
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentVerificationsDeleteVerificationPlanCreate({
        businessAreaSlug,
        id,
        programSlug,
        verificationPlanId,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        verificationPlanId: string,
        requestBody?: PaymentVerificationPlanActivate,
    }): CancelablePromise<PaymentVerificationPlanDetails> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-verifications/{id}/delete-verification-plan/{verification_plan_id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
                'verification_plan_id': verificationPlanId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentVerificationPlanDetails
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentVerificationsDiscardVerificationPlanCreate({
        businessAreaSlug,
        id,
        programSlug,
        verificationPlanId,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        verificationPlanId: string,
        requestBody?: PaymentVerificationPlanActivate,
    }): CancelablePromise<PaymentVerificationPlanDetails> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-verifications/{id}/discard-verification-plan/{verification_plan_id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
                'verification_plan_id': verificationPlanId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentVerificationPlanDetails
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentVerificationsExportXlsxCreate({
        businessAreaSlug,
        id,
        programSlug,
        verificationPlanId,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        verificationPlanId: string,
        requestBody?: PaymentVerificationPlanActivate,
    }): CancelablePromise<PaymentVerificationPlanDetails> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-verifications/{id}/export-xlsx/{verification_plan_id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
                'verification_plan_id': verificationPlanId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentVerificationPlanDetails
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentVerificationsFinishVerificationPlanCreate({
        businessAreaSlug,
        id,
        programSlug,
        verificationPlanId,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        verificationPlanId: string,
        requestBody?: PaymentVerificationPlanActivate,
    }): CancelablePromise<PaymentVerificationPlanDetails> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-verifications/{id}/finish-verification-plan/{verification_plan_id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
                'verification_plan_id': verificationPlanId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentVerificationPlanDetails
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentVerificationsImportXlsxCreate({
        businessAreaSlug,
        id,
        programSlug,
        verificationPlanId,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        verificationPlanId: string,
        requestBody: PaymentVerificationPlanImport,
    }): CancelablePromise<PaymentVerificationPlanDetails> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-verifications/{id}/import-xlsx/{verification_plan_id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
                'verification_plan_id': verificationPlanId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentVerificationPlanDetails
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentVerificationsInvalidVerificationPlanCreate({
        businessAreaSlug,
        id,
        programSlug,
        verificationPlanId,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        verificationPlanId: string,
        requestBody?: PaymentVerificationPlanActivate,
    }): CancelablePromise<PaymentVerificationPlanDetails> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-verifications/{id}/invalid-verification-plan/{verification_plan_id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
                'verification_plan_id': verificationPlanId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentVerificationPlanDetails
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentVerificationsUpdateVerificationPlanPartialUpdate({
        businessAreaSlug,
        id,
        programSlug,
        verificationPlanId,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        verificationPlanId: string,
        requestBody?: PatchedPaymentVerificationPlanCreate,
    }): CancelablePromise<PaymentVerificationPlanDetails> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-verifications/{id}/update-verification-plan/{verification_plan_id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
                'verification_plan_id': verificationPlanId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns CountResponse
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentVerificationsCountRetrieve({
        businessAreaSlug,
        programSlug,
    }: {
        businessAreaSlug: string,
        programSlug: string,
    }): CancelablePromise<CountResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/payment-verifications/count/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * @returns PaginatedPeriodicDataUpdateTemplateListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPeriodicDataUpdateTemplatesList({
        businessAreaSlug,
        programSlug,
        limit,
        offset,
        ordering,
        updatedAtAfter,
        updatedAtBefore,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        updatedAtAfter?: string,
        updatedAtBefore?: string,
    }): CancelablePromise<PaginatedPeriodicDataUpdateTemplateListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/periodic-data-update-templates/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
            query: {
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
                'updated_at_after': updatedAtAfter,
                'updated_at_before': updatedAtBefore,
            },
        });
    }
    /**
     * @returns PeriodicDataUpdateTemplateCreate
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPeriodicDataUpdateTemplatesCreate({
        businessAreaSlug,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        requestBody: PeriodicDataUpdateTemplateCreate,
    }): CancelablePromise<PeriodicDataUpdateTemplateCreate> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/periodic-data-update-templates/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @returns PeriodicDataUpdateTemplateDetail
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPeriodicDataUpdateTemplatesRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A unique integer value identifying this periodic data update template.
         */
        id: number,
        programSlug: string,
    }): CancelablePromise<PeriodicDataUpdateTemplateDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/periodic-data-update-templates/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPeriodicDataUpdateTemplatesDownloadRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A unique integer value identifying this periodic data update template.
         */
        id: number,
        programSlug: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/periodic-data-update-templates/{id}/download/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPeriodicDataUpdateTemplatesExportCreate({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A unique integer value identifying this periodic data update template.
         */
        id: number,
        programSlug: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/periodic-data-update-templates/{id}/export/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * @returns PaginatedPeriodicDataUpdateUploadListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPeriodicDataUpdateUploadsList({
        businessAreaSlug,
        programSlug,
        limit,
        offset,
        ordering,
        updatedAtAfter,
        updatedAtBefore,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        updatedAtAfter?: string,
        updatedAtBefore?: string,
    }): CancelablePromise<PaginatedPeriodicDataUpdateUploadListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/periodic-data-update-uploads/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
            query: {
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
                'updated_at_after': updatedAtAfter,
                'updated_at_before': updatedAtBefore,
            },
        });
    }
    /**
     * @returns PeriodicDataUpdateUploadDetail
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPeriodicDataUpdateUploadsRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A unique integer value identifying this periodic data update upload.
         */
        id: number,
        programSlug: string,
    }): CancelablePromise<PeriodicDataUpdateUploadDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/periodic-data-update-uploads/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * @returns PeriodicDataUpdateUpload
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPeriodicDataUpdateUploadsUploadCreate({
        businessAreaSlug,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        requestBody: PeriodicDataUpdateUpload,
    }): CancelablePromise<PeriodicDataUpdateUpload> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/periodic-data-update-uploads/upload/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @returns PaginatedPeriodicFieldList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPeriodicFieldsList({
        businessAreaSlug,
        programSlug,
        limit,
        offset,
        ordering,
        updatedAtAfter,
        updatedAtBefore,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        updatedAtAfter?: string,
        updatedAtBefore?: string,
    }): CancelablePromise<PaginatedPeriodicFieldList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/periodic-fields/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
            query: {
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
                'updated_at_after': updatedAtAfter,
                'updated_at_before': updatedAtBefore,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaginatedRegistrationDataImportListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsRegistrationDataImportsList({
        businessAreaSlug,
        programSlug,
        importDate,
        importDateRange,
        importedById,
        limit,
        name,
        nameStartswith,
        offset,
        orderBy,
        ordering,
        search,
        size,
        status,
        totalHouseholdsCountWithValidPhoneNoMax,
        totalHouseholdsCountWithValidPhoneNoMin,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        importDate?: string,
        importDateRange?: string,
        importedById?: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        name?: string,
        nameStartswith?: string,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Ordering
         *
         * * `name` - Name
         * * `-name` - Name (descending)
         * * `status` - Status
         * * `-status` - Status (descending)
         * * `import_date` - Import date
         * * `-import_date` - Import date (descending)
         * * `number_of_individuals` - Number of individuals
         * * `-number_of_individuals` - Number of individuals (descending)
         * * `number_of_households` - Number of households
         * * `-number_of_households` - Number of households (descending)
         * * `data_source` - Data source
         * * `-data_source` - Data source (descending)
         * * `imported_by__first_name` - Imported by  first name
         * * `-imported_by__first_name` - Imported by  first name (descending)
         */
        orderBy?: Array<'-data_source' | '-import_date' | '-imported_by__first_name' | '-name' | '-number_of_households' | '-number_of_individuals' | '-status' | 'data_source' | 'import_date' | 'imported_by__first_name' | 'name' | 'number_of_households' | 'number_of_individuals' | 'status'>,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        search?: string,
        size?: number,
        /**
         * * `LOADING` - Loading
         * * `DEDUPLICATION` - Deduplication
         * * `DEDUPLICATION_FAILED` - Deduplication Failed
         * * `IMPORT_SCHEDULED` - Import Scheduled
         * * `IMPORTING` - Importing
         * * `IMPORT_ERROR` - Import Error
         * * `IN_REVIEW` - In Review
         * * `MERGE_SCHEDULED` - Merge Scheduled
         * * `MERGED` - Merged
         * * `MERGING` - Merging
         * * `MERGE_ERROR` - Merge Error
         * * `REFUSED` - Refused import
         */
        status?: 'DEDUPLICATION' | 'DEDUPLICATION_FAILED' | 'IMPORTING' | 'IMPORT_ERROR' | 'IMPORT_SCHEDULED' | 'IN_REVIEW' | 'LOADING' | 'MERGED' | 'MERGE_ERROR' | 'MERGE_SCHEDULED' | 'MERGING' | 'REFUSED',
        totalHouseholdsCountWithValidPhoneNoMax?: any,
        totalHouseholdsCountWithValidPhoneNoMin?: any,
    }): CancelablePromise<PaginatedRegistrationDataImportListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/registration-data-imports/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
            query: {
                'import_date': importDate,
                'import_date_range': importDateRange,
                'imported_by__id': importedById,
                'limit': limit,
                'name': name,
                'name__startswith': nameStartswith,
                'offset': offset,
                'order_by': orderBy,
                'ordering': ordering,
                'search': search,
                'size': size,
                'status': status,
                'total_households_count_with_valid_phone_no_max': totalHouseholdsCountWithValidPhoneNoMax,
                'total_households_count_with_valid_phone_no_min': totalHouseholdsCountWithValidPhoneNoMin,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns RegistrationDataImportDetail
     * @throws ApiError
     */
    public static restBusinessAreasProgramsRegistrationDataImportsRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Registration data import.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<RegistrationDataImportDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/registration-data-imports/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns any No response body
     * @throws ApiError
     */
    public static restBusinessAreasProgramsRegistrationDataImportsDeduplicateCreate({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Registration data import.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/registration-data-imports/{id}/deduplicate/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns any No response body
     * @throws ApiError
     */
    public static restBusinessAreasProgramsRegistrationDataImportsEraseCreate({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Registration data import.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/registration-data-imports/{id}/erase/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns any No response body
     * @throws ApiError
     */
    public static restBusinessAreasProgramsRegistrationDataImportsMergeCreate({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Registration data import.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/registration-data-imports/{id}/merge/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns RefuseRdi
     * @throws ApiError
     */
    public static restBusinessAreasProgramsRegistrationDataImportsRefuseCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Registration data import.
         */
        id: string,
        programSlug: string,
        requestBody: RefuseRdi,
    }): CancelablePromise<RefuseRdi> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/registration-data-imports/{id}/refuse/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns CountResponse
     * @throws ApiError
     */
    public static restBusinessAreasProgramsRegistrationDataImportsCountRetrieve({
        businessAreaSlug,
        programSlug,
    }: {
        businessAreaSlug: string,
        programSlug: string,
    }): CancelablePromise<CountResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/registration-data-imports/count/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns any No response body
     * @throws ApiError
     */
    public static restBusinessAreasProgramsRegistrationDataImportsRunDeduplicationCreate({
        businessAreaSlug,
        programSlug,
    }: {
        businessAreaSlug: string,
        programSlug: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/registration-data-imports/run-deduplication/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns any No response body
     * @throws ApiError
     */
    public static restBusinessAreasProgramsRegistrationDataImportsWebhookdeduplicationRetrieve({
        businessAreaSlug,
        programSlug,
    }: {
        businessAreaSlug: string,
        programSlug: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/registration-data-imports/webhookdeduplication/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaginatedTargetPopulationListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsTargetPopulationsList({
        businessAreaSlug,
        programSlug,
        createdAtGte,
        createdAtLte,
        deliveryMechanism,
        fsp,
        limit,
        name,
        offset,
        ordering,
        paymentVerificationSummaryStatus,
        program,
        programCycle,
        programCycleEndDate,
        programCycleStartDate,
        search,
        status,
        totalHouseholdsCountGte,
        totalHouseholdsCountLte,
        totalIndividualsCountGte,
        totalIndividualsCountLte,
        updatedAtGte,
        updatedAtLte,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        createdAtGte?: string,
        createdAtLte?: string,
        deliveryMechanism?: Array<string>,
        fsp?: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        name?: string,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        /**
         * * `ACTIVE` - Active
         * * `FINISHED` - Finished
         * * `PENDING` - Pending
         */
        paymentVerificationSummaryStatus?: 'ACTIVE' | 'FINISHED' | 'PENDING',
        program?: string,
        programCycle?: string,
        programCycleEndDate?: string,
        programCycleStartDate?: string,
        /**
         * A search term.
         */
        search?: string,
        /**
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
         * * `ASSIGNED` - Assigned
         */
        status?: 'ACCEPTED' | 'ASSIGNED' | 'DRAFT' | 'FINISHED' | 'IN_APPROVAL' | 'IN_AUTHORIZATION' | 'IN_REVIEW' | 'LOCKED' | 'LOCKED_FSP' | 'OPEN' | 'PREPARING' | 'PROCESSING' | 'STEFICON_COMPLETED' | 'STEFICON_ERROR' | 'STEFICON_RUN' | 'STEFICON_WAIT' | 'TP_LOCKED' | 'TP_OPEN',
        totalHouseholdsCountGte?: number,
        totalHouseholdsCountLte?: number,
        totalIndividualsCountGte?: number,
        totalIndividualsCountLte?: number,
        updatedAtGte?: string,
        updatedAtLte?: string,
    }): CancelablePromise<PaginatedTargetPopulationListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/target-populations/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
            query: {
                'created_at__gte': createdAtGte,
                'created_at__lte': createdAtLte,
                'delivery_mechanism': deliveryMechanism,
                'fsp': fsp,
                'limit': limit,
                'name': name,
                'offset': offset,
                'ordering': ordering,
                'payment_verification_summary_status': paymentVerificationSummaryStatus,
                'program': program,
                'program_cycle': programCycle,
                'program_cycle_end_date': programCycleEndDate,
                'program_cycle_start_date': programCycleStartDate,
                'search': search,
                'status': status,
                'total_households_count__gte': totalHouseholdsCountGte,
                'total_households_count__lte': totalHouseholdsCountLte,
                'total_individuals_count__gte': totalIndividualsCountGte,
                'total_individuals_count__lte': totalIndividualsCountLte,
                'updated_at__gte': updatedAtGte,
                'updated_at__lte': updatedAtLte,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns TargetPopulationCreate
     * @throws ApiError
     */
    public static restBusinessAreasProgramsTargetPopulationsCreate({
        businessAreaSlug,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        requestBody: TargetPopulationCreate,
    }): CancelablePromise<TargetPopulationCreate> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/target-populations/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns TargetPopulationDetail
     * @throws ApiError
     */
    public static restBusinessAreasProgramsTargetPopulationsRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<TargetPopulationDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/target-populations/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns TargetPopulationCreate
     * @throws ApiError
     */
    public static restBusinessAreasProgramsTargetPopulationsPartialUpdate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        requestBody?: PatchedTargetPopulationCreate,
    }): CancelablePromise<TargetPopulationCreate> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/target-populations/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns void
     * @throws ApiError
     */
    public static restBusinessAreasProgramsTargetPopulationsDestroy({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/target-populations/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns ApplyEngineFormula
     * @throws ApiError
     */
    public static restBusinessAreasProgramsTargetPopulationsApplyEngineFormulaCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        requestBody: ApplyEngineFormula,
    }): CancelablePromise<ApplyEngineFormula> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/target-populations/{id}/apply-engine-formula/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns TargetPopulationCopy
     * @throws ApiError
     */
    public static restBusinessAreasProgramsTargetPopulationsCopyCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
        requestBody: TargetPopulationCopy,
    }): CancelablePromise<TargetPopulationCopy> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/target-populations/{id}/copy/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlan
     * @throws ApiError
     */
    public static restBusinessAreasProgramsTargetPopulationsLockRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<PaymentPlan> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/target-populations/{id}/lock/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlan
     * @throws ApiError
     */
    public static restBusinessAreasProgramsTargetPopulationsMarkReadyRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<PaymentPlan> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/target-populations/{id}/mark-ready/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlan
     * @throws ApiError
     */
    public static restBusinessAreasProgramsTargetPopulationsRebuildRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<PaymentPlan> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/target-populations/{id}/rebuild/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaymentPlan
     * @throws ApiError
     */
    public static restBusinessAreasProgramsTargetPopulationsUnlockRetrieve({
        businessAreaSlug,
        id,
        programSlug,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this Payment Plan.
         */
        id: string,
        programSlug: string,
    }): CancelablePromise<PaymentPlan> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/target-populations/{id}/unlock/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaginatedTPHouseholdListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsTargetPopulationsHouseholdsList({
        businessAreaSlug,
        programSlug,
        targetPopulationId,
        limit,
        offset,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        targetPopulationId: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
    }): CancelablePromise<PaginatedTPHouseholdListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/target-populations/{target_population_id}/households/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
                'target_population_id': targetPopulationId,
            },
            query: {
                'limit': limit,
                'offset': offset,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns TPHouseholdList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsTargetPopulationsHouseholdsRetrieve({
        businessAreaSlug,
        id,
        programSlug,
        targetPopulationId,
    }: {
        businessAreaSlug: string,
        /**
         * A UUID string identifying this payment.
         */
        id: string,
        programSlug: string,
        targetPopulationId: string,
    }): CancelablePromise<TPHouseholdList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/target-populations/{target_population_id}/households/{id}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'id': id,
                'program_slug': programSlug,
                'target_population_id': targetPopulationId,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns CountResponse
     * @throws ApiError
     */
    public static restBusinessAreasProgramsTargetPopulationsHouseholdsCountRetrieve({
        businessAreaSlug,
        programSlug,
        targetPopulationId,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        targetPopulationId: string,
    }): CancelablePromise<CountResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/target-populations/{target_population_id}/households/count/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
                'target_population_id': targetPopulationId,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns CountResponse
     * @throws ApiError
     */
    public static restBusinessAreasProgramsTargetPopulationsCountRetrieve({
        businessAreaSlug,
        programSlug,
    }: {
        businessAreaSlug: string,
        programSlug: string,
    }): CancelablePromise<CountResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/target-populations/count/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
        });
    }
    /**
     * Base validation class, inherit from this class to create custom validators.
     * Your custom validators have to implement validation methods that starts
     * with name "validate_" so validate can call all the validators from your
     * custom validator.
     *
     * Custom validate method have to takes *args, **kwargs parameters.
     *
     * validate method with parameters have to be called in mutate method.
     * If there are validation errors they will be all
     * returned as one error message.
     * @returns ProgramDetail
     * @throws ApiError
     */
    public static restBusinessAreasProgramsRetrieve({
        businessAreaSlug,
        slug,
    }: {
        businessAreaSlug: string,
        slug: string,
    }): CancelablePromise<ProgramDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{slug}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'slug': slug,
            },
        });
    }
    /**
     * Base validation class, inherit from this class to create custom validators.
     * Your custom validators have to implement validation methods that starts
     * with name "validate_" so validate can call all the validators from your
     * custom validator.
     *
     * Custom validate method have to takes *args, **kwargs parameters.
     *
     * validate method with parameters have to be called in mutate method.
     * If there are validation errors they will be all
     * returned as one error message.
     * @returns void
     * @throws ApiError
     */
    public static restBusinessAreasProgramsDestroy({
        businessAreaSlug,
        slug,
    }: {
        businessAreaSlug: string,
        slug: string,
    }): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{slug}/',
            path: {
                'business_area_slug': businessAreaSlug,
                'slug': slug,
            },
        });
    }
    /**
     * Base validation class, inherit from this class to create custom validators.
     * Your custom validators have to implement validation methods that starts
     * with name "validate_" so validate can call all the validators from your
     * custom validator.
     *
     * Custom validate method have to takes *args, **kwargs parameters.
     *
     * validate method with parameters have to be called in mutate method.
     * If there are validation errors they will be all
     * returned as one error message.
     * @returns PaginatedPaymentListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsPaymentsList({
        businessAreaSlug,
        slug,
        beneficiaryGroupMatch,
        budgetMax,
        budgetMin,
        compatibleDct,
        dataCollectingType,
        endDate,
        limit,
        name,
        numberOfHouseholdsMax,
        numberOfHouseholdsMin,
        numberOfHouseholdsWithTpInProgramMax,
        numberOfHouseholdsWithTpInProgramMin,
        offset,
        orderBy,
        ordering,
        search,
        sector,
        startDate,
        status,
        updatedAtAfter,
        updatedAtBefore,
    }: {
        businessAreaSlug: string,
        slug: string,
        beneficiaryGroupMatch?: string,
        /**
         * Program budget
         */
        budgetMax?: string,
        /**
         * Program budget
         */
        budgetMin?: string,
        compatibleDct?: string,
        dataCollectingType?: string,
        endDate?: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        name?: string,
        numberOfHouseholdsMax?: string,
        numberOfHouseholdsMin?: string,
        numberOfHouseholdsWithTpInProgramMax?: string,
        numberOfHouseholdsWithTpInProgramMin?: string,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Ordering
         *
         * * `name` - Name
         * * `-name` - Name (descending)
         * * `status` - Status
         * * `-status` - Status (descending)
         * * `start_date` - Start date
         * * `-start_date` - Start date (descending)
         * * `end_date` - End date
         * * `-end_date` - End date (descending)
         * * `sector` - Sector
         * * `-sector` - Sector (descending)
         * * `number_of_households` - Number of households
         * * `-number_of_households` - Number of households (descending)
         * * `budget` - Budget
         * * `-budget` - Budget (descending)
         */
        orderBy?: Array<'-budget' | '-end_date' | '-name' | '-number_of_households' | '-sector' | '-start_date' | '-status' | 'budget' | 'end_date' | 'name' | 'number_of_households' | 'sector' | 'start_date' | 'status'>,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        search?: any,
        /**
         * Program sector
         *
         * * `CHILD_PROTECTION` - Child Protection
         * * `EDUCATION` - Education
         * * `HEALTH` - Health
         * * `MULTI_PURPOSE` - Multi Purpose
         * * `NUTRITION` - Nutrition
         * * `SOCIAL_POLICY` - Social Policy
         * * `WASH` - WASH
         */
        sector?: Array<'CHILD_PROTECTION' | 'EDUCATION' | 'HEALTH' | 'MULTI_PURPOSE' | 'NUTRITION' | 'SOCIAL_POLICY' | 'WASH'>,
        startDate?: string,
        /**
         * Program status
         *
         * * `ACTIVE` - Active
         * * `DRAFT` - Draft
         * * `FINISHED` - Finished
         */
        status?: Array<'ACTIVE' | 'DRAFT' | 'FINISHED'>,
        updatedAtAfter?: string,
        updatedAtBefore?: string,
    }): CancelablePromise<PaginatedPaymentListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{slug}/payments/',
            path: {
                'business_area_slug': businessAreaSlug,
                'slug': slug,
            },
            query: {
                'beneficiary_group_match': beneficiaryGroupMatch,
                'budget_max': budgetMax,
                'budget_min': budgetMin,
                'compatible_dct': compatibleDct,
                'data_collecting_type': dataCollectingType,
                'end_date': endDate,
                'limit': limit,
                'name': name,
                'number_of_households_max': numberOfHouseholdsMax,
                'number_of_households_min': numberOfHouseholdsMin,
                'number_of_households_with_tp_in_program_max': numberOfHouseholdsWithTpInProgramMax,
                'number_of_households_with_tp_in_program_min': numberOfHouseholdsWithTpInProgramMin,
                'offset': offset,
                'order_by': orderBy,
                'ordering': ordering,
                'search': search,
                'sector': sector,
                'start_date': startDate,
                'status': status,
                'updated_at_after': updatedAtAfter,
                'updated_at_before': updatedAtBefore,
            },
        });
    }
    /**
     * Base validation class, inherit from this class to create custom validators.
     * Your custom validators have to implement validation methods that starts
     * with name "validate_" so validate can call all the validators from your
     * custom validator.
     *
     * Custom validate method have to takes *args, **kwargs parameters.
     *
     * validate method with parameters have to be called in mutate method.
     * If there are validation errors they will be all
     * returned as one error message.
     * @returns CountResponse
     * @throws ApiError
     */
    public static restBusinessAreasProgramsCountRetrieve({
        businessAreaSlug,
    }: {
        businessAreaSlug: string,
    }): CancelablePromise<CountResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/count/',
            path: {
                'business_area_slug': businessAreaSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns PaginatedUserList
     * @throws ApiError
     */
    public static restBusinessAreasUsersList({
        businessAreaSlug,
        isFeedbackCreator,
        isMessageCreator,
        isSurveyCreator,
        isTicketCreator,
        limit,
        offset,
        orderBy,
        ordering,
        partner,
        program,
        roles,
        search,
        status,
    }: {
        businessAreaSlug: string,
        isFeedbackCreator?: boolean,
        isMessageCreator?: boolean,
        isSurveyCreator?: boolean,
        isTicketCreator?: boolean,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Ordering
         *
         * * `first_name` - First name
         * * `-first_name` - First name (descending)
         * * `last_name` - Last name
         * * `-last_name` - Last name (descending)
         * * `last_login` - Last login
         * * `-last_login` - Last login (descending)
         * * `status` - Status
         * * `-status` - Status (descending)
         * * `partner` - Partner
         * * `-partner` - Partner (descending)
         * * `email` - Email
         * * `-email` - Email (descending)
         */
        orderBy?: Array<'-email' | '-first_name' | '-last_login' | '-last_name' | '-partner' | '-status' | 'email' | 'first_name' | 'last_login' | 'last_name' | 'partner' | 'status'>,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        partner?: Array<number>,
        program?: string,
        roles?: Array<string>,
        search?: string,
        /**
         * * `ACTIVE` - Active
         * * `INACTIVE` - Inactive
         * * `INVITED` - Invited
         */
        status?: Array<'ACTIVE' | 'INACTIVE' | 'INVITED'>,
    }): CancelablePromise<PaginatedUserList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/users/',
            path: {
                'business_area_slug': businessAreaSlug,
            },
            query: {
                'is_feedback_creator': isFeedbackCreator,
                'is_message_creator': isMessageCreator,
                'is_survey_creator': isSurveyCreator,
                'is_ticket_creator': isTicketCreator,
                'limit': limit,
                'offset': offset,
                'order_by': orderBy,
                'ordering': ordering,
                'partner': partner,
                'program': program,
                'roles': roles,
                'search': search,
                'status': status,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns CountResponse
     * @throws ApiError
     */
    public static restBusinessAreasUsersCountRetrieve({
        businessAreaSlug,
    }: {
        businessAreaSlug: string,
    }): CancelablePromise<CountResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/users/count/',
            path: {
                'business_area_slug': businessAreaSlug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns Profile
     * @throws ApiError
     */
    public static restBusinessAreasUsersProfileRetrieve({
        businessAreaSlug,
        program,
    }: {
        businessAreaSlug: string,
        program?: string,
    }): CancelablePromise<Profile> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/users/profile/',
            path: {
                'business_area_slug': businessAreaSlug,
            },
            query: {
                'program': program,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns BusinessArea
     * @throws ApiError
     */
    public static restBusinessAreasRetrieve({
        slug,
    }: {
        slug: string,
    }): CancelablePromise<BusinessArea> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{slug}/',
            path: {
                'slug': slug,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * @returns CountResponse
     * @throws ApiError
     */
    public static restBusinessAreasCountRetrieve(): CancelablePromise<CountResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/count/',
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static restConstanceRetrieve(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/constance/',
        });
    }
    /**
     * Returns the list of currency choices.
     * @returns any No response body
     * @throws ApiError
     */
    public static restCurrencyRetrieve(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/currency/',
        });
    }
    /**
     * Retrieve dashboard data for a given business area from Redis cache.
     * If data is not cached or needs updating, refresh it.
     * @returns any No response body
     * @throws ApiError
     */
    public static restDashboardDataRetrieve({
        businessAreaSlug,
    }: {
        businessAreaSlug: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/dashboard/{business_area_slug}/data/',
            path: {
                'business_area_slug': businessAreaSlug,
            },
        });
    }
    /**
     * API to trigger the creation or update of a DashReport for a given business area.
     * Restricted to superusers and users with the required permissions.
     * @returns any No response body
     * @throws ApiError
     */
    public static restDashboardGenerateCreate({
        businessAreaSlug,
    }: {
        businessAreaSlug: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/dashboard/generate/{business_area_slug}/',
            path: {
                'business_area_slug': businessAreaSlug,
            },
        });
    }
    /**
     * @returns PaginatedRuleList
     * @throws ApiError
     */
    public static restEngineRulesList({
        type,
        deprecated,
        enabled,
        limit,
        offset,
        ordering,
    }: {
        /**
         * Use Rule for Targeting or Payment Plan
         *
         * * `PAYMENT_PLAN` - Payment Plan
         * * `TARGETING` - Targeting
         */
        type: 'PAYMENT_PLAN' | 'TARGETING',
        deprecated?: boolean,
        enabled?: boolean,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
    }): CancelablePromise<PaginatedRuleList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/engine-rules/',
            query: {
                'deprecated': deprecated,
                'enabled': enabled,
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
                'type': type,
            },
        });
    }
    /**
     * @returns PaginatedCountryList
     * @throws ApiError
     */
    public static restLookupsCountryList({
        limit,
        offset,
        ordering,
        search,
        updatedAtAfter,
        updatedAtBefore,
        validFromAfter,
        validFromBefore,
        validUntilAfter,
        validUntilBefore,
    }: {
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        /**
         * A search term.
         */
        search?: string,
        updatedAtAfter?: string,
        updatedAtBefore?: string,
        validFromAfter?: string,
        validFromBefore?: string,
        validUntilAfter?: string,
        validUntilBefore?: string,
    }): CancelablePromise<PaginatedCountryList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/lookups/country/',
            query: {
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
                'search': search,
                'updated_at_after': updatedAtAfter,
                'updated_at_before': updatedAtBefore,
                'valid_from_after': validFromAfter,
                'valid_from_before': validFromBefore,
                'valid_until_after': validUntilAfter,
                'valid_until_before': validUntilBefore,
            },
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static restLookupsDocumentRetrieve(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/lookups/document/',
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static restLookupsMaritalstatusRetrieve(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/lookups/maritalstatus/',
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static restLookupsObserveddisabilityRetrieve(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/lookups/observeddisability/',
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static restLookupsProgramStatusesRetrieve(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/lookups/program-statuses/',
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static restLookupsRelationshipRetrieve(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/lookups/relationship/',
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static restLookupsResidencestatusRetrieve(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/lookups/residencestatus/',
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static restLookupsRoleRetrieve(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/lookups/role/',
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static restLookupsSexRetrieve(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/lookups/sex/',
        });
    }
    /**
     * @returns PaginatedProgramGlobalList
     * @throws ApiError
     */
    public static restProgramsList({
        active,
        businessArea,
        limit,
        offset,
        ordering,
        status,
        updatedAtAfter,
        updatedAtBefore,
    }: {
        active?: boolean,
        businessArea?: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        /**
         * Which field to use when ordering the results.
         */
        ordering?: string,
        /**
         * Program status
         *
         * * `ACTIVE` - Active
         * * `DRAFT` - Draft
         * * `FINISHED` - Finished
         */
        status?: 'ACTIVE' | 'DRAFT' | 'FINISHED',
        updatedAtAfter?: string,
        updatedAtBefore?: string,
    }): CancelablePromise<PaginatedProgramGlobalList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/programs/',
            query: {
                'active': active,
                'business_area': businessArea,
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
                'status': status,
                'updated_at_after': updatedAtAfter,
                'updated_at_before': updatedAtBefore,
            },
        });
    }
    /**
     * @returns PaginatedOrganizationList
     * @throws ApiError
     */
    public static restSystemsAuroraOfficesList({
        limit,
        offset,
    }: {
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
    }): CancelablePromise<PaginatedOrganizationList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/systems/aurora/offices/',
            query: {
                'limit': limit,
                'offset': offset,
            },
        });
    }
    /**
     * @returns PaginatedProjectList
     * @throws ApiError
     */
    public static restSystemsAuroraProjectsList({
        limit,
        offset,
        orgPk,
        orgSlug,
    }: {
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        orgPk?: string,
        orgSlug?: string,
    }): CancelablePromise<PaginatedProjectList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/systems/aurora/projects/',
            query: {
                'limit': limit,
                'offset': offset,
                'org_pk': orgPk,
                'org_slug': orgSlug,
            },
        });
    }
    /**
     * @returns PaginatedRegistrationList
     * @throws ApiError
     */
    public static restSystemsAuroraRegistrationsList({
        limit,
        offset,
        orgPk,
        orgSlug,
        programmePk,
    }: {
        /**
         * Number of results to return per page.
         */
        limit?: number,
        /**
         * The initial index from which to return the results.
         */
        offset?: number,
        orgPk?: string,
        orgSlug?: string,
        programmePk?: string,
    }): CancelablePromise<PaginatedRegistrationList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/systems/aurora/registrations/',
            query: {
                'limit': limit,
                'offset': offset,
                'org_pk': orgPk,
                'org_slug': orgSlug,
                'programme_pk': programmePk,
            },
        });
    }
}
