/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BusinessArea } from '../models/BusinessArea';
import type { DelegatePeople } from '../models/DelegatePeople';
import type { HouseholdDetail } from '../models/HouseholdDetail';
import type { HouseholdList } from '../models/HouseholdList';
import type { PaginatedAreaList } from '../models/PaginatedAreaList';
import type { PaginatedAreaListList } from '../models/PaginatedAreaListList';
import type { PaginatedAreaTypeList } from '../models/PaginatedAreaTypeList';
import type { PaginatedBeneficiaryGroupList } from '../models/PaginatedBeneficiaryGroupList';
import type { PaginatedBusinessAreaList } from '../models/PaginatedBusinessAreaList';
import type { PaginatedCountryList } from '../models/PaginatedCountryList';
import type { PaginatedHouseholdListList } from '../models/PaginatedHouseholdListList';
import type { PaginatedOrganizationList } from '../models/PaginatedOrganizationList';
import type { PaginatedPaymentPlanList } from '../models/PaginatedPaymentPlanList';
import type { PaginatedPeriodicDataUpdateTemplateListList } from '../models/PaginatedPeriodicDataUpdateTemplateListList';
import type { PaginatedPeriodicDataUpdateUploadListList } from '../models/PaginatedPeriodicDataUpdateUploadListList';
import type { PaginatedPeriodicFieldList } from '../models/PaginatedPeriodicFieldList';
import type { PaginatedProgramCycleListList } from '../models/PaginatedProgramCycleListList';
import type { PaginatedProgramGlobalList } from '../models/PaginatedProgramGlobalList';
import type { PaginatedProgramListList } from '../models/PaginatedProgramListList';
import type { PaginatedProjectList } from '../models/PaginatedProjectList';
import type { PaginatedRegistrationDataImportListList } from '../models/PaginatedRegistrationDataImportListList';
import type { PaginatedRegistrationList } from '../models/PaginatedRegistrationList';
import type { PaginatedTargetPopulationListList } from '../models/PaginatedTargetPopulationListList';
import type { PatchedProgramCycleUpdate } from '../models/PatchedProgramCycleUpdate';
import type { PatchedRDI } from '../models/PatchedRDI';
import type { PaymentPlanBulkAction } from '../models/PaymentPlanBulkAction';
import type { PaymentPlanSupportingDocument } from '../models/PaymentPlanSupportingDocument';
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
import type { RegistrationDataImportList } from '../models/RegistrationDataImportList';
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
     * @returns PaginatedBusinessAreaList
     * @throws ApiError
     */
    public static restBusinessAreasList({
        active,
        limit,
        offset,
        ordering,
        updatedAtAfter,
        updatedAtBefore,
    }: {
        active?: boolean,
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
    }): CancelablePromise<PaginatedBusinessAreaList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/',
            query: {
                'active': active,
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
                'updated_at_after': updatedAtAfter,
                'updated_at_before': updatedAtBefore,
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
        addressStartswith,
        admin1,
        admin2,
        adminArea,
        businessArea,
        countryOrigin,
        documentNumber,
        documentType,
        firstRegistrationDate,
        headOfHouseholdFullName,
        headOfHouseholdFullNameStartswith,
        headOfHouseholdPhoneNoValid,
        isActiveProgram,
        lastRegistrationDate,
        limit,
        offset,
        orderBy,
        ordering,
        program,
        rdiId,
        rdiMergeStatus,
        residenceStatus,
        search,
        size,
        sizeGte,
        sizeLte,
        sizeRange,
        withdrawn,
    }: {
        businessAreaSlug: string,
        address?: string,
        addressStartswith?: string,
        admin1?: string,
        admin2?: string,
        adminArea?: string,
        businessArea?: string,
        countryOrigin?: string,
        documentNumber?: string,
        documentType?: string,
        firstRegistrationDate?: string,
        headOfHouseholdFullName?: string,
        headOfHouseholdFullNameStartswith?: string,
        headOfHouseholdPhoneNoValid?: boolean,
        isActiveProgram?: boolean,
        lastRegistrationDate?: string,
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
        size?: number | null,
        sizeGte?: number,
        sizeLte?: number,
        /**
         * Multiple values may be separated by commas.
         */
        sizeRange?: Array<number>,
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
                'address__startswith': addressStartswith,
                'admin1': admin1,
                'admin2': admin2,
                'admin_area': adminArea,
                'business_area': businessArea,
                'country_origin': countryOrigin,
                'document_number': documentNumber,
                'document_type': documentType,
                'first_registration_date': firstRegistrationDate,
                'head_of_household__full_name': headOfHouseholdFullName,
                'head_of_household__full_name__startswith': headOfHouseholdFullNameStartswith,
                'head_of_household__phone_no_valid': headOfHouseholdPhoneNoValid,
                'is_active_program': isActiveProgram,
                'last_registration_date': lastRegistrationDate,
                'limit': limit,
                'offset': offset,
                'order_by': orderBy,
                'ordering': ordering,
                'program': program,
                'rdi_id': rdiId,
                'rdi_merge_status': rdiMergeStatus,
                'residence_status': residenceStatus,
                'search': search,
                'size': size,
                'size__gte': sizeGte,
                'size__lte': sizeLte,
                'size__range': sizeRange,
                'withdrawn': withdrawn,
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
        dispersionEndDateLte,
        dispersionStartDateGte,
        isFollowUp,
        limit,
        name,
        offset,
        ordering,
        program,
        search,
        status,
        totalEntitledQuantityGte,
        totalEntitledQuantityLte,
    }: {
        businessAreaSlug: string,
        dispersionEndDateLte?: string,
        dispersionStartDateGte?: string,
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
        program?: string,
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
         */
        status?: 'ACCEPTED' | 'DRAFT' | 'FINISHED' | 'IN_APPROVAL' | 'IN_AUTHORIZATION' | 'IN_REVIEW' | 'LOCKED' | 'LOCKED_FSP' | 'OPEN' | 'PREPARING' | 'PROCESSING' | 'STEFICON_COMPLETED' | 'STEFICON_ERROR' | 'STEFICON_RUN' | 'STEFICON_WAIT' | 'TP_LOCKED' | 'TP_OPEN',
        totalEntitledQuantityGte?: number,
        totalEntitledQuantityLte?: number,
    }): CancelablePromise<PaginatedPaymentPlanList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/payments/payment-plans-managerial/',
            path: {
                'business_area_slug': businessAreaSlug,
            },
            query: {
                'dispersion_end_date__lte': dispersionEndDateLte,
                'dispersion_start_date__gte': dispersionStartDateGte,
                'is_follow_up': isFollowUp,
                'limit': limit,
                'name': name,
                'offset': offset,
                'ordering': ordering,
                'program': program,
                'search': search,
                'status': status,
                'total_entitled_quantity__gte': totalEntitledQuantityGte,
                'total_entitled_quantity__lte': totalEntitledQuantityLte,
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
     * @returns PaginatedProgramListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsList({
        beneficiaryGroupMatch,
        businessArea,
        businessAreaSlug,
        budget,
        compatibleDct,
        dataCollectingType,
        endDate,
        limit,
        name,
        numberOfHouseholds,
        numberOfHouseholdsWithTpInProgram,
        offset,
        orderBy,
        ordering,
        search,
        sector,
        startDate,
        status,
    }: {
        beneficiaryGroupMatch: any,
        businessArea: string,
        businessAreaSlug: string,
        budget?: string,
        compatibleDct?: any,
        dataCollectingType?: string,
        endDate?: string,
        /**
         * Number of results to return per page.
         */
        limit?: number,
        name?: string,
        numberOfHouseholds?: string,
        numberOfHouseholdsWithTpInProgram?: string,
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
         * * `ACTIVE` - Active
         * * `DRAFT` - Draft
         * * `FINISHED` - Finished
         */
        status?: Array<'ACTIVE' | 'DRAFT' | 'FINISHED'>,
    }): CancelablePromise<PaginatedProgramListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/',
            path: {
                'business_area_slug': businessAreaSlug,
            },
            query: {
                'beneficiary_group_match': beneficiaryGroupMatch,
                'budget': budget,
                'business_area': businessArea,
                'compatible_dct': compatibleDct,
                'data_collecting_type': dataCollectingType,
                'end_date': endDate,
                'limit': limit,
                'name': name,
                'number_of_households': numberOfHouseholds,
                'number_of_households_with_tp_in_program': numberOfHouseholdsWithTpInProgram,
                'offset': offset,
                'order_by': orderBy,
                'ordering': ordering,
                'search': search,
                'sector': sector,
                'start_date': startDate,
                'status': status,
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
     * Adds a count action to the viewset that returns the count of the queryset.
     * NOTE: This mixin should be added as the first mixin in the inheritance chain.
     * @returns PaginatedHouseholdListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsHouseholdsList({
        businessAreaSlug,
        programSlug,
        address,
        addressStartswith,
        admin1,
        admin2,
        adminArea,
        businessArea,
        countryOrigin,
        documentNumber,
        documentType,
        firstRegistrationDate,
        headOfHouseholdFullName,
        headOfHouseholdFullNameStartswith,
        headOfHouseholdPhoneNoValid,
        isActiveProgram,
        lastRegistrationDate,
        limit,
        offset,
        orderBy,
        ordering,
        program,
        rdiId,
        rdiMergeStatus,
        residenceStatus,
        search,
        size,
        sizeGte,
        sizeLte,
        sizeRange,
        withdrawn,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        address?: string,
        addressStartswith?: string,
        admin1?: string,
        admin2?: string,
        adminArea?: string,
        businessArea?: string,
        countryOrigin?: string,
        documentNumber?: string,
        documentType?: string,
        firstRegistrationDate?: string,
        headOfHouseholdFullName?: string,
        headOfHouseholdFullNameStartswith?: string,
        headOfHouseholdPhoneNoValid?: boolean,
        isActiveProgram?: boolean,
        lastRegistrationDate?: string,
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
        size?: number | null,
        sizeGte?: number,
        sizeLte?: number,
        /**
         * Multiple values may be separated by commas.
         */
        sizeRange?: Array<number>,
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
                'address__startswith': addressStartswith,
                'admin1': admin1,
                'admin2': admin2,
                'admin_area': adminArea,
                'business_area': businessArea,
                'country_origin': countryOrigin,
                'document_number': documentNumber,
                'document_type': documentType,
                'first_registration_date': firstRegistrationDate,
                'head_of_household__full_name': headOfHouseholdFullName,
                'head_of_household__full_name__startswith': headOfHouseholdFullNameStartswith,
                'head_of_household__phone_no_valid': headOfHouseholdPhoneNoValid,
                'is_active_program': isActiveProgram,
                'last_registration_date': lastRegistrationDate,
                'limit': limit,
                'offset': offset,
                'order_by': orderBy,
                'ordering': ordering,
                'program': program,
                'rdi_id': rdiId,
                'rdi_merge_status': rdiMergeStatus,
                'residence_status': residenceStatus,
                'search': search,
                'size': size,
                'size__gte': sizeGte,
                'size__lte': sizeLte,
                'size__range': sizeRange,
                'withdrawn': withdrawn,
            },
        });
    }
    /**
     * Adds a count action to the viewset that returns the count of the queryset.
     * NOTE: This mixin should be added as the first mixin in the inheritance chain.
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
     * Adds a count action to the viewset that returns the count of the queryset.
     * NOTE: This mixin should be added as the first mixin in the inheritance chain.
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
     * Adds a count action to the viewset that returns the count of the queryset.
     * NOTE: This mixin should be added as the first mixin in the inheritance chain.
     * @returns HouseholdList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsHouseholdsCountRetrieve({
        businessAreaSlug,
        programSlug,
    }: {
        businessAreaSlug: string,
        programSlug: string,
    }): CancelablePromise<HouseholdList> {
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
     * @returns PaginatedRegistrationDataImportListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsRegistrationDataImportsList({
        businessAreaSlug,
        programSlug,
        limit,
        name,
        offset,
        ordering,
        status,
        updatedAtAfter,
        updatedAtBefore,
    }: {
        businessAreaSlug: string,
        programSlug: string,
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
        updatedAtAfter?: string,
        updatedAtBefore?: string,
    }): CancelablePromise<PaginatedRegistrationDataImportListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/registration-data-imports/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
            query: {
                'limit': limit,
                'name': name,
                'offset': offset,
                'ordering': ordering,
                'status': status,
                'updated_at_after': updatedAtAfter,
                'updated_at_before': updatedAtBefore,
            },
        });
    }
    /**
     * @returns RegistrationDataImportList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsRegistrationDataImportsRunDeduplicationCreate({
        businessAreaSlug,
        programSlug,
        requestBody,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        requestBody: RegistrationDataImportList,
    }): CancelablePromise<RegistrationDataImportList> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/registration-data-imports/run-deduplication/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @returns RegistrationDataImportList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsRegistrationDataImportsWebhookdeduplicationRetrieve({
        businessAreaSlug,
        programSlug,
    }: {
        businessAreaSlug: string,
        programSlug: string,
    }): CancelablePromise<RegistrationDataImportList> {
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
     * @returns PaginatedTargetPopulationListList
     * @throws ApiError
     */
    public static restBusinessAreasProgramsTargetPopulationsList({
        businessAreaSlug,
        programSlug,
        dispersionEndDateLte,
        dispersionStartDateGte,
        isFollowUp,
        limit,
        name,
        offset,
        ordering,
        program,
        status,
        totalEntitledQuantityGte,
        totalEntitledQuantityLte,
    }: {
        businessAreaSlug: string,
        programSlug: string,
        dispersionEndDateLte?: string,
        dispersionStartDateGte?: string,
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
        program?: string,
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
         */
        status?: 'ACCEPTED' | 'DRAFT' | 'FINISHED' | 'IN_APPROVAL' | 'IN_AUTHORIZATION' | 'IN_REVIEW' | 'LOCKED' | 'LOCKED_FSP' | 'OPEN' | 'PREPARING' | 'PROCESSING' | 'STEFICON_COMPLETED' | 'STEFICON_ERROR' | 'STEFICON_RUN' | 'STEFICON_WAIT' | 'TP_LOCKED' | 'TP_OPEN',
        totalEntitledQuantityGte?: number,
        totalEntitledQuantityLte?: number,
    }): CancelablePromise<PaginatedTargetPopulationListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business-areas/{business_area_slug}/programs/{program_slug}/target-populations/',
            path: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
            query: {
                'dispersion_end_date__lte': dispersionEndDateLte,
                'dispersion_start_date__gte': dispersionStartDateGte,
                'is_follow_up': isFollowUp,
                'limit': limit,
                'name': name,
                'offset': offset,
                'ordering': ordering,
                'program': program,
                'status': status,
                'total_entitled_quantity__gte': totalEntitledQuantityGte,
                'total_entitled_quantity__lte': totalEntitledQuantityLte,
            },
        });
    }
    /**
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
     * @returns BusinessArea
     * @throws ApiError
     */
    public static restBusinessAreasRetrieve({
        slug,
    }: {
        /**
         * A UUID string identifying this business area.
         */
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
    /**
     * @returns Profile
     * @throws ApiError
     */
    public static restUsersProfileRetrieve({
        businessAreaSlug,
        programSlug,
    }: {
        businessAreaSlug?: string,
        programSlug?: string,
    }): CancelablePromise<Profile> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/users/profile/',
            query: {
                'business_area_slug': businessAreaSlug,
                'program_slug': programSlug,
            },
        });
    }
}
