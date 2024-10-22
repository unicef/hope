/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DelegatePeople } from '../models/DelegatePeople';
import type { PaginatedAreaList } from '../models/PaginatedAreaList';
import type { PaginatedAreaListList } from '../models/PaginatedAreaListList';
import type { PaginatedAreaTypeList } from '../models/PaginatedAreaTypeList';
import type { PaginatedBusinessAreaList } from '../models/PaginatedBusinessAreaList';
import type { PaginatedPaymentPlanList } from '../models/PaginatedPaymentPlanList';
import type { PaginatedPeriodicDataUpdateTemplateListList } from '../models/PaginatedPeriodicDataUpdateTemplateListList';
import type { PaginatedPeriodicDataUpdateUploadListList } from '../models/PaginatedPeriodicDataUpdateUploadListList';
import type { PaginatedPeriodicFieldList } from '../models/PaginatedPeriodicFieldList';
import type { PaginatedProgramCycleListList } from '../models/PaginatedProgramCycleListList';
import type { PaginatedProgramGlobalList } from '../models/PaginatedProgramGlobalList';
import type { PaginatedRegistrationDataImportListList } from '../models/PaginatedRegistrationDataImportListList';
import type { PaginatedTargetPopulationListList } from '../models/PaginatedTargetPopulationListList';
import type { PatchedProgramCycleUpdate } from '../models/PatchedProgramCycleUpdate';
import type { PatchedRDI } from '../models/PatchedRDI';
import type { PaymentPlanBulkAction } from '../models/PaymentPlanBulkAction';
import type { PeriodicDataUpdateTemplateCreate } from '../models/PeriodicDataUpdateTemplateCreate';
import type { PeriodicDataUpdateTemplateDetail } from '../models/PeriodicDataUpdateTemplateDetail';
import type { PeriodicDataUpdateUpload } from '../models/PeriodicDataUpdateUpload';
import type { PeriodicDataUpdateUploadDetail } from '../models/PeriodicDataUpdateUploadDetail';
import type { Program } from '../models/Program';
import type { ProgramCycleCreate } from '../models/ProgramCycleCreate';
import type { ProgramCycleList } from '../models/ProgramCycleList';
import type { ProgramCycleUpdate } from '../models/ProgramCycleUpdate';
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
     * @param format
     * @param lang
     * @returns any
     * @throws ApiError
     */
    public static restRetrieve(
        format?: 'json' | 'yaml',
        lang?: 'af' | 'ar' | 'ar-dz' | 'ast' | 'az' | 'be' | 'bg' | 'bn' | 'br' | 'bs' | 'ca' | 'cs' | 'cy' | 'da' | 'de' | 'dsb' | 'el' | 'en' | 'en-au' | 'en-gb' | 'eo' | 'es' | 'es-ar' | 'es-co' | 'es-mx' | 'es-ni' | 'es-ve' | 'et' | 'eu' | 'fa' | 'fi' | 'fr' | 'fy' | 'ga' | 'gd' | 'gl' | 'he' | 'hi' | 'hr' | 'hsb' | 'hu' | 'hy' | 'ia' | 'id' | 'ig' | 'io' | 'is' | 'it' | 'ja' | 'ka' | 'kab' | 'kk' | 'km' | 'kn' | 'ko' | 'ky' | 'lb' | 'lt' | 'lv' | 'mk' | 'ml' | 'mn' | 'mr' | 'my' | 'nb' | 'ne' | 'nl' | 'nn' | 'os' | 'pa' | 'pl' | 'pt' | 'pt-br' | 'ro' | 'ru' | 'sk' | 'sl' | 'sq' | 'sr' | 'sr-latn' | 'sv' | 'sw' | 'ta' | 'te' | 'tg' | 'th' | 'tk' | 'tr' | 'tt' | 'udm' | 'uk' | 'ur' | 'uz' | 'vi' | 'zh-hans' | 'zh-hant',
    ): CancelablePromise<Record<string, any>> {
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
     * @param businessArea
     * @param limit Number of results to return per page.
     * @param offset The initial index from which to return the results.
     * @param ordering Which field to use when ordering the results.
     * @returns PaginatedAreaListList
     * @throws ApiError
     */
    public static restGeoAreasList(
        businessArea: string,
        limit?: number,
        offset?: number,
        ordering?: string,
    ): CancelablePromise<PaginatedAreaListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/{business_area}/geo/areas/',
            path: {
                'business_area': businessArea,
            },
            query: {
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
            },
        });
    }
    /**
     * @param businessArea
     * @param limit Number of results to return per page.
     * @param offset The initial index from which to return the results.
     * @param ordering Which field to use when ordering the results.
     * @param search A search term.
     * @returns PaginatedPaymentPlanList
     * @throws ApiError
     */
    public static restPaymentsPaymentPlansManagerialList(
        businessArea: string,
        limit?: number,
        offset?: number,
        ordering?: string,
        search?: string,
    ): CancelablePromise<PaginatedPaymentPlanList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/{business_area}/payments/payment-plans-managerial/',
            path: {
                'business_area': businessArea,
            },
            query: {
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
                'search': search,
            },
        });
    }
    /**
     * @param businessArea
     * @param requestBody
     * @returns PaymentPlanBulkAction
     * @throws ApiError
     */
    public static restPaymentsPaymentPlansManagerialBulkActionCreate(
        businessArea: string,
        requestBody: PaymentPlanBulkAction,
    ): CancelablePromise<PaymentPlanBulkAction> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/{business_area}/payments/payment-plans-managerial/bulk-action/',
            path: {
                'business_area': businessArea,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param businessArea
     * @returns any No response body
     * @throws ApiError
     */
    public static restProgramRetrieve(
        businessArea: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/{business_area}/program/',
            path: {
                'business_area': businessArea,
            },
        });
    }
    /**
     * @param businessArea
     * @param requestBody
     * @returns any No response body
     * @throws ApiError
     */
    public static restProgramCreateCreate(
        businessArea: string,
        requestBody: Program,
    ): CancelablePromise<any> {
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
     * @param businessArea
     * @param programId
     * @param limit Number of results to return per page.
     * @param offset The initial index from which to return the results.
     * @param ordering Which field to use when ordering the results.
     * @returns PaginatedProgramCycleListList
     * @throws ApiError
     */
    public static restProgramsCyclesList(
        businessArea: string,
        programId: string,
        limit?: number,
        offset?: number,
        ordering?: string,
    ): CancelablePromise<PaginatedProgramCycleListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/{business_area}/programs/{program_id}/cycles/',
            path: {
                'business_area': businessArea,
                'program_id': programId,
            },
            query: {
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
            },
        });
    }
    /**
     * @param businessArea
     * @param programId
     * @param requestBody
     * @returns ProgramCycleCreate
     * @throws ApiError
     */
    public static restProgramsCyclesCreate(
        businessArea: string,
        programId: string,
        requestBody: ProgramCycleCreate,
    ): CancelablePromise<ProgramCycleCreate> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/{business_area}/programs/{program_id}/cycles/',
            path: {
                'business_area': businessArea,
                'program_id': programId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param businessArea
     * @param id
     * @param programId
     * @returns ProgramCycleList
     * @throws ApiError
     */
    public static restProgramsCyclesRetrieve(
        businessArea: string,
        id: string,
        programId: string,
    ): CancelablePromise<ProgramCycleList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/{business_area}/programs/{program_id}/cycles/{id}/',
            path: {
                'business_area': businessArea,
                'id': id,
                'program_id': programId,
            },
        });
    }
    /**
     * @param businessArea
     * @param id
     * @param programId
     * @param requestBody
     * @returns ProgramCycleUpdate
     * @throws ApiError
     */
    public static restProgramsCyclesUpdate(
        businessArea: string,
        id: string,
        programId: string,
        requestBody?: ProgramCycleUpdate,
    ): CancelablePromise<ProgramCycleUpdate> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/rest/{business_area}/programs/{program_id}/cycles/{id}/',
            path: {
                'business_area': businessArea,
                'id': id,
                'program_id': programId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param businessArea
     * @param id
     * @param programId
     * @param requestBody
     * @returns ProgramCycleUpdate
     * @throws ApiError
     */
    public static restProgramsCyclesPartialUpdate(
        businessArea: string,
        id: string,
        programId: string,
        requestBody?: PatchedProgramCycleUpdate,
    ): CancelablePromise<ProgramCycleUpdate> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/rest/{business_area}/programs/{program_id}/cycles/{id}/',
            path: {
                'business_area': businessArea,
                'id': id,
                'program_id': programId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param businessArea
     * @param id
     * @param programId
     * @returns void
     * @throws ApiError
     */
    public static restProgramsCyclesDestroy(
        businessArea: string,
        id: string,
        programId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/rest/{business_area}/programs/{program_id}/cycles/{id}/',
            path: {
                'business_area': businessArea,
                'id': id,
                'program_id': programId,
            },
        });
    }
    /**
     * @param businessArea
     * @param id
     * @param programId
     * @returns any No response body
     * @throws ApiError
     */
    public static restProgramsCyclesFinishCreate(
        businessArea: string,
        id: string,
        programId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/{business_area}/programs/{program_id}/cycles/{id}/finish/',
            path: {
                'business_area': businessArea,
                'id': id,
                'program_id': programId,
            },
        });
    }
    /**
     * @param businessArea
     * @param id
     * @param programId
     * @returns any No response body
     * @throws ApiError
     */
    public static restProgramsCyclesReactivateCreate(
        businessArea: string,
        id: string,
        programId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/{business_area}/programs/{program_id}/cycles/{id}/reactivate/',
            path: {
                'business_area': businessArea,
                'id': id,
                'program_id': programId,
            },
        });
    }
    /**
     * @param businessArea
     * @param paymentPlanId
     * @param programId
     * @returns any No response body
     * @throws ApiError
     */
    public static restProgramsPaymentPlansSupportingDocumentsUploadCreate(
        businessArea: string,
        paymentPlanId: string,
        programId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/{business_area}/programs/{program_id}/payment-plans/{payment_plan_id}/supporting-documents-upload/',
            path: {
                'business_area': businessArea,
                'payment_plan_id': paymentPlanId,
                'program_id': programId,
            },
        });
    }
    /**
     * @param businessArea
     * @param fileId
     * @param paymentPlanId
     * @param programId
     * @returns any No response body
     * @throws ApiError
     */
    public static restProgramsPaymentPlansSupportingDocumentsRetrieve(
        businessArea: string,
        fileId: string,
        paymentPlanId: string,
        programId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/{business_area}/programs/{program_id}/payment-plans/{payment_plan_id}/supporting-documents/{file_id}/',
            path: {
                'business_area': businessArea,
                'file_id': fileId,
                'payment_plan_id': paymentPlanId,
                'program_id': programId,
            },
        });
    }
    /**
     * @param businessArea
     * @param fileId
     * @param paymentPlanId
     * @param programId
     * @returns void
     * @throws ApiError
     */
    public static restProgramsPaymentPlansSupportingDocumentsDestroy(
        businessArea: string,
        fileId: string,
        paymentPlanId: string,
        programId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/rest/{business_area}/programs/{program_id}/payment-plans/{payment_plan_id}/supporting-documents/{file_id}/',
            path: {
                'business_area': businessArea,
                'file_id': fileId,
                'payment_plan_id': paymentPlanId,
                'program_id': programId,
            },
        });
    }
    /**
     * @param businessArea
     * @param programId
     * @param limit Number of results to return per page.
     * @param offset The initial index from which to return the results.
     * @param ordering Which field to use when ordering the results.
     * @returns PaginatedPeriodicDataUpdateTemplateListList
     * @throws ApiError
     */
    public static restProgramsPeriodicDataUpdatePeriodicDataUpdateTemplatesList(
        businessArea: string,
        programId: string,
        limit?: number,
        offset?: number,
        ordering?: string,
    ): CancelablePromise<PaginatedPeriodicDataUpdateTemplateListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/{business_area}/programs/{program_id}/periodic-data-update/periodic-data-update-templates/',
            path: {
                'business_area': businessArea,
                'program_id': programId,
            },
            query: {
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
            },
        });
    }
    /**
     * @param businessArea
     * @param programId
     * @param requestBody
     * @returns PeriodicDataUpdateTemplateCreate
     * @throws ApiError
     */
    public static restProgramsPeriodicDataUpdatePeriodicDataUpdateTemplatesCreate(
        businessArea: string,
        programId: string,
        requestBody: PeriodicDataUpdateTemplateCreate,
    ): CancelablePromise<PeriodicDataUpdateTemplateCreate> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/{business_area}/programs/{program_id}/periodic-data-update/periodic-data-update-templates/',
            path: {
                'business_area': businessArea,
                'program_id': programId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param businessArea
     * @param id
     * @param programId
     * @returns PeriodicDataUpdateTemplateDetail
     * @throws ApiError
     */
    public static restProgramsPeriodicDataUpdatePeriodicDataUpdateTemplatesRetrieve(
        businessArea: string,
        id: string,
        programId: string,
    ): CancelablePromise<PeriodicDataUpdateTemplateDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/{business_area}/programs/{program_id}/periodic-data-update/periodic-data-update-templates/{id}/',
            path: {
                'business_area': businessArea,
                'id': id,
                'program_id': programId,
            },
        });
    }
    /**
     * @param businessArea
     * @param id
     * @param programId
     * @returns any No response body
     * @throws ApiError
     */
    public static restProgramsPeriodicDataUpdatePeriodicDataUpdateTemplatesDownloadRetrieve(
        businessArea: string,
        id: string,
        programId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/{business_area}/programs/{program_id}/periodic-data-update/periodic-data-update-templates/{id}/download/',
            path: {
                'business_area': businessArea,
                'id': id,
                'program_id': programId,
            },
        });
    }
    /**
     * @param businessArea
     * @param id
     * @param programId
     * @returns any No response body
     * @throws ApiError
     */
    public static restProgramsPeriodicDataUpdatePeriodicDataUpdateTemplatesExportCreate(
        businessArea: string,
        id: string,
        programId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/{business_area}/programs/{program_id}/periodic-data-update/periodic-data-update-templates/{id}/export/',
            path: {
                'business_area': businessArea,
                'id': id,
                'program_id': programId,
            },
        });
    }
    /**
     * @param businessArea
     * @param programId
     * @param limit Number of results to return per page.
     * @param offset The initial index from which to return the results.
     * @param ordering Which field to use when ordering the results.
     * @returns PaginatedPeriodicDataUpdateUploadListList
     * @throws ApiError
     */
    public static restProgramsPeriodicDataUpdatePeriodicDataUpdateUploadsList(
        businessArea: string,
        programId: string,
        limit?: number,
        offset?: number,
        ordering?: string,
    ): CancelablePromise<PaginatedPeriodicDataUpdateUploadListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/{business_area}/programs/{program_id}/periodic-data-update/periodic-data-update-uploads/',
            path: {
                'business_area': businessArea,
                'program_id': programId,
            },
            query: {
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
            },
        });
    }
    /**
     * @param businessArea
     * @param id
     * @param programId
     * @returns PeriodicDataUpdateUploadDetail
     * @throws ApiError
     */
    public static restProgramsPeriodicDataUpdatePeriodicDataUpdateUploadsRetrieve(
        businessArea: string,
        id: string,
        programId: string,
    ): CancelablePromise<PeriodicDataUpdateUploadDetail> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/{business_area}/programs/{program_id}/periodic-data-update/periodic-data-update-uploads/{id}/',
            path: {
                'business_area': businessArea,
                'id': id,
                'program_id': programId,
            },
        });
    }
    /**
     * @param businessArea
     * @param programId
     * @param requestBody
     * @returns PeriodicDataUpdateUpload
     * @throws ApiError
     */
    public static restProgramsPeriodicDataUpdatePeriodicDataUpdateUploadsUploadCreate(
        businessArea: string,
        programId: string,
        requestBody: PeriodicDataUpdateUpload,
    ): CancelablePromise<PeriodicDataUpdateUpload> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/{business_area}/programs/{program_id}/periodic-data-update/periodic-data-update-uploads/upload/',
            path: {
                'business_area': businessArea,
                'program_id': programId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param businessArea
     * @param programId
     * @param limit Number of results to return per page.
     * @param offset The initial index from which to return the results.
     * @param ordering Which field to use when ordering the results.
     * @returns PaginatedPeriodicFieldList
     * @throws ApiError
     */
    public static restProgramsPeriodicDataUpdatePeriodicFieldsList(
        businessArea: string,
        programId: string,
        limit?: number,
        offset?: number,
        ordering?: string,
    ): CancelablePromise<PaginatedPeriodicFieldList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/{business_area}/programs/{program_id}/periodic-data-update/periodic-fields/',
            path: {
                'business_area': businessArea,
                'program_id': programId,
            },
            query: {
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
            },
        });
    }
    /**
     * @param businessArea
     * @param programId
     * @param limit Number of results to return per page.
     * @param offset The initial index from which to return the results.
     * @param ordering Which field to use when ordering the results.
     * @returns PaginatedRegistrationDataImportListList
     * @throws ApiError
     */
    public static restProgramsRegistrationDataRegistrationDataImportsList(
        businessArea: string,
        programId: string,
        limit?: number,
        offset?: number,
        ordering?: string,
    ): CancelablePromise<PaginatedRegistrationDataImportListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/{business_area}/programs/{program_id}/registration-data/registration-data-imports/',
            path: {
                'business_area': businessArea,
                'program_id': programId,
            },
            query: {
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
            },
        });
    }
    /**
     * @param businessArea
     * @param programId
     * @param requestBody
     * @returns RegistrationDataImportList
     * @throws ApiError
     */
    public static restProgramsRegistrationDataRegistrationDataImportsRunDeduplicationCreate(
        businessArea: string,
        programId: string,
        requestBody: RegistrationDataImportList,
    ): CancelablePromise<RegistrationDataImportList> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/rest/{business_area}/programs/{program_id}/registration-data/registration-data-imports/run-deduplication/',
            path: {
                'business_area': businessArea,
                'program_id': programId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * @param businessArea
     * @param programId
     * @returns any No response body
     * @throws ApiError
     */
    public static restProgramsRegistrationDataWebhookdeduplicationRetrieve(
        businessArea: string,
        programId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/{business_area}/programs/{program_id}/registration-data/webhookdeduplication/',
            path: {
                'business_area': businessArea,
                'program_id': programId,
            },
        });
    }
    /**
     * @param businessArea
     * @param programId
     * @param limit Number of results to return per page.
     * @param offset The initial index from which to return the results.
     * @param ordering Which field to use when ordering the results.
     * @returns PaginatedTargetPopulationListList
     * @throws ApiError
     */
    public static restProgramsTargetingTargetPopulationsList(
        businessArea: string,
        programId: string,
        limit?: number,
        offset?: number,
        ordering?: string,
    ): CancelablePromise<PaginatedTargetPopulationListList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/{business_area}/programs/{program_id}/targeting/target-populations/',
            path: {
                'business_area': businessArea,
                'program_id': programId,
            },
            query: {
                'limit': limit,
                'offset': offset,
                'ordering': ordering,
            },
        });
    }
    /**
     * Api to Create RDI for selected business area
     * @param businessArea
     * @param rdi
     * @param requestBody
     * @returns RDI
     * @throws ApiError
     */
    public static restRdiCompletedCreate(
        businessArea: string,
        rdi: string,
        requestBody: RDI,
    ): CancelablePromise<RDI> {
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
     * @param businessArea
     * @param rdi
     * @param requestBody
     * @returns RDI
     * @throws ApiError
     */
    public static restRdiCompletedUpdate(
        businessArea: string,
        rdi: string,
        requestBody: RDI,
    ): CancelablePromise<RDI> {
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
     * @param businessArea
     * @param rdi
     * @param requestBody
     * @returns RDI
     * @throws ApiError
     */
    public static restRdiCompletedPartialUpdate(
        businessArea: string,
        rdi: string,
        requestBody?: PatchedRDI,
    ): CancelablePromise<RDI> {
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
     * @param businessArea
     * @param rdi
     * @param requestBody
     * @returns any No response body
     * @throws ApiError
     */
    public static restRdiDelegatePeopleCreate(
        businessArea: string,
        rdi: string,
        requestBody: DelegatePeople,
    ): CancelablePromise<any> {
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
     * @param businessArea
     * @param rdi
     * @returns any No response body
     * @throws ApiError
     */
    public static restRdiPushCreate(
        businessArea: string,
        rdi: string,
    ): CancelablePromise<any> {
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
     * @param businessArea
     * @param rdi
     * @returns any No response body
     * @throws ApiError
     */
    public static restRdiPushLaxCreate(
        businessArea: string,
        rdi: string,
    ): CancelablePromise<any> {
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
     * @param businessArea
     * @param rdi
     * @param requestBody
     * @returns any No response body
     * @throws ApiError
     */
    public static restRdiPushPeopleCreate(
        businessArea: string,
        rdi: string,
        requestBody: PushPeople,
    ): CancelablePromise<any> {
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
     * @param businessArea
     * @param requestBody
     * @returns RDI
     * @throws ApiError
     */
    public static restRdiCreateCreate(
        businessArea: string,
        requestBody: RDI,
    ): CancelablePromise<RDI> {
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
     * @param businessArea
     * @param requestBody
     * @returns any No response body
     * @throws ApiError
     */
    public static restRdiUploadCreate(
        businessArea: string,
        requestBody: RDINested,
    ): CancelablePromise<any> {
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
     * @param limit Number of results to return per page.
     * @param offset The initial index from which to return the results.
     * @returns PaginatedAreaList
     * @throws ApiError
     */
    public static restAreasList(
        limit?: number,
        offset?: number,
    ): CancelablePromise<PaginatedAreaList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/areas/',
            query: {
                'limit': limit,
                'offset': offset,
            },
        });
    }
    /**
     * @param limit Number of results to return per page.
     * @param offset The initial index from which to return the results.
     * @returns PaginatedAreaTypeList
     * @throws ApiError
     */
    public static restAreatypesList(
        limit?: number,
        offset?: number,
    ): CancelablePromise<PaginatedAreaTypeList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/areatypes/',
            query: {
                'limit': limit,
                'offset': offset,
            },
        });
    }
    /**
     * @param limit Number of results to return per page.
     * @param offset The initial index from which to return the results.
     * @returns PaginatedBusinessAreaList
     * @throws ApiError
     */
    public static restBusinessAreasList(
        limit?: number,
        offset?: number,
    ): CancelablePromise<PaginatedBusinessAreaList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/business_areas/',
            query: {
                'limit': limit,
                'offset': offset,
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
     * @returns any No response body
     * @throws ApiError
     */
    public static restLookupsCountryRetrieve(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/lookups/country/',
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static restLookupsDatacollectingpolicyRetrieve(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/lookups/datacollectingpolicy/',
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
     * @param limit Number of results to return per page.
     * @param offset The initial index from which to return the results.
     * @returns PaginatedProgramGlobalList
     * @throws ApiError
     */
    public static restProgramsList(
        limit?: number,
        offset?: number,
    ): CancelablePromise<PaginatedProgramGlobalList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/rest/programs/',
            query: {
                'limit': limit,
                'offset': offset,
            },
        });
    }
}
