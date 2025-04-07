/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class FieldsAttributesService {
    /**
     * Returns the list of FieldAttribute.
     * @returns any No response body
     * @throws ApiError
     */
    public static fieldsAttributesRetrieve(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/fields_attributes/',
        });
    }
}
