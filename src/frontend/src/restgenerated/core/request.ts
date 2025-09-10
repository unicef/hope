/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import { ApiError } from './ApiError';
import type { ApiRequestOptions } from './ApiRequestOptions';
import type { ApiResult } from './ApiResult';
import { CancelablePromise } from './CancelablePromise';
import type { OnCancel } from './CancelablePromise';
import type { OpenAPIConfig } from './OpenAPI';
import { deepCamelize, deepUnderscore } from '../../utils/utils';

export const isDefined = <T>(
  value: T | null | undefined,
): value is Exclude<T, null | undefined> => {
  return value !== undefined && value !== null;
};

export const isString = (value: any): value is string => {
  return typeof value === 'string';
};

export const isStringWithValue = (value: any): value is string => {
  return isString(value) && value !== '';
};

export const isBlob = (value: any): value is Blob => {
  return (
    typeof value === 'object' &&
    typeof value.type === 'string' &&
    typeof value.stream === 'function' &&
    typeof value.arrayBuffer === 'function' &&
    typeof value.constructor === 'function' &&
    typeof value.constructor.name === 'string' &&
    /^(Blob|File)$/.test(value.constructor.name) &&
    /^(Blob|File)$/.test(value[Symbol.toStringTag])
  );
};

export const isFormData = (value: any): value is FormData => {
  return value instanceof FormData;
};

export const base64 = (str: string): string => {
  try {
    return btoa(str);
  } catch (err) {
    // @ts-ignore
    return Buffer.from(str).toString('base64');
  }
};

export const getQueryString = (params: Record<string, any>): string => {
  const qs: string[] = [];

  const append = (key: string, value: any) => {
    qs.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`);
  };

  const process = (key: string, value: any) => {
    if (isDefined(value)) {
      if (Array.isArray(value)) {
        value.forEach((v) => {
          process(key, v);
        });
      } else if (typeof value === 'object') {
        Object.entries(value).forEach(([k, v]) => {
          process(`${key}[${k}]`, v);
        });
      } else {
        append(key, value);
      }
    }
  };

  Object.entries(params).forEach(([key, value]) => {
    process(key, value);
  });

  if (qs.length > 0) {
    return `?${qs.join('&')}`;
  }

  return '';
};

const getUrl = (config: OpenAPIConfig, options: ApiRequestOptions): string => {
  const encoder = config.ENCODE_PATH || encodeURI;

  const path = options.url
    .replace('{api-version}', config.VERSION)
    .replace(/{(.*?)}/g, (substring: string, group: string) => {
      if (options.path?.hasOwnProperty(group)) {
        return encoder(String(options.path[group]));
      }
      return substring;
    });

  const url = `${config.BASE}${path}`;
  if (options.query) {
    return `${url}${getQueryString(options.query)}`;
  }
  return url;
};

export function customSnakeCase(str: string): string {
  return (
    str
      // Insert _ between lowercase and uppercase
      .replace(/([a-z])([A-Z])/g, '$1_$2')
      // Insert _ between letter and number
      .replace(/([a-zA-Z])([0-9])/g, '$1_$2')
      // Insert _ between number and letter
      .replace(/([0-9])([a-zA-Z])/g, '$1_$2')
      // Replace age group numbers like 05, 611, 1217, 1859, 60 with correct underscores
      .replace(/_0(\d)(_|$)/g, '_0_$1$2') // 05 -> 0_5
      .replace(/_6(\d{2})(_|$)/g, '_6_$1$2') // 611 -> 6_11
      .replace(/_1(\d{2})(_|$)/g, '_1_$1$2') // 1217, 1859 -> 12_17, 18_59
      .replace(/_6_0(_|$)/g, '_60$1') // 60 stays as 60 (optional, if you want _60 not _6_0)
      .toLowerCase()
  );
}
export function processFormData(
  obj: any,
  form?: FormData,
  parentKey?: string,
): FormData {
  const formData = form || new FormData();

  // Handle primitive values directly
  if (typeof obj !== 'object' || obj === null || obj instanceof File) {
    if (parentKey) {
      if (obj instanceof File) {
        formData.append(parentKey, obj);
      } else if (typeof obj === 'boolean') {
        formData.append(parentKey, obj ? 'true' : 'false');
      } else if (obj !== null && obj !== undefined) {
        formData.append(parentKey, obj);
      }
    }
    return formData;
  }

  for (const key in obj) {
    if (obj[key] === undefined || obj[key] === null) continue;
    const value = obj[key];
    const snakeKey = customSnakeCase(key);
    let formKey;
    if (Array.isArray(obj)) {
      // Array: use bracket notation for index
      formKey = parentKey ? `${parentKey}[${key}]` : key;
    } else {
      // Object: use dot notation for nesting
      formKey = parentKey ? `${parentKey}.${snakeKey}` : snakeKey;
    }

    if (value instanceof File) {
      formData.append(formKey, value);
    } else if (Array.isArray(value)) {
      if (value.length === 0) {
        continue;
      } else {
        value.forEach((item, idx) => {
          processFormData(item, formData, `${formKey}[${idx}]`);
        });
      }
    } else if (typeof value === 'object' && value !== null) {
      if (Object.keys(value).length === 0) {
        // Do not send empty objects at all
        continue;
      } else {
        processFormData(value, formData, formKey);
      }
    } else if (typeof value === 'boolean') {
      formData.append(formKey, value ? 'true' : 'false');
    } else {
      formData.append(formKey, value);
    }
  }
  return formData;
}
export const getFormData = (
  options: ApiRequestOptions,
): FormData | undefined => {
  if (!options.formData) {
    return undefined;
  }
  return processFormData(options.formData);
};

type Resolver<T> = (options: ApiRequestOptions) => Promise<T>;

export const resolve = async <T>(
  options: ApiRequestOptions,
  resolver?: T | Resolver<T>,
): Promise<T | undefined> => {
  if (typeof resolver === 'function') {
    return (resolver as Resolver<T>)(options);
  }
  return resolver;
};

export const getHeaders = async (
  config: OpenAPIConfig,
  options: ApiRequestOptions,
): Promise<Headers> => {
  const [token, username, password, additionalHeaders] = await Promise.all([
    resolve(options, config.TOKEN),
    resolve(options, config.USERNAME),
    resolve(options, config.PASSWORD),
    resolve(options, config.HEADERS),
  ]);

  const headers = Object.entries({
    Accept: 'application/json',
    ...additionalHeaders,
    ...options.headers,
  })
    .filter(([_, value]) => isDefined(value))
    .reduce(
      (headers, [key, value]) => ({
        ...headers,
        [key]: String(value),
      }),
      {} as Record<string, string>,
    );

  if (isStringWithValue(token)) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  if (isStringWithValue(username) && isStringWithValue(password)) {
    const credentials = base64(`${username}:${password}`);
    headers['Authorization'] = `Basic ${credentials}`;
  }

  if (options.body !== undefined) {
    if (isFormData(options.body)) {
      // Do not set Content-Type for FormData; browser will set it
    } else if (options.mediaType) {
      headers['Content-Type'] = options.mediaType;
    } else if (isBlob(options.body)) {
      headers['Content-Type'] = options.body.type || 'application/octet-stream';
    } else if (isString(options.body)) {
      headers['Content-Type'] = 'text/plain';
    } else {
      headers['Content-Type'] = 'application/json';
    }
  }

  return new Headers(headers);
};

export const getRequestBody = (options: ApiRequestOptions): any => {
  if (options.body !== undefined) {
    if (isFormData(options.body)) {
      return options.body;
    } else if (options.mediaType?.includes('/json')) {
      return JSON.stringify(options.body);
    } else if (isString(options.body) || isBlob(options.body)) {
      return options.body;
    } else {
      return JSON.stringify(options.body);
    }
  }
  return undefined;
};

export const sendRequest = async (
  config: OpenAPIConfig,
  options: ApiRequestOptions,
  url: string,
  body: any,
  formData: FormData | undefined,
  headers: Headers,
  onCancel: OnCancel,
): Promise<Response> => {
  const controller = new AbortController();
  let requestBody = body;
  if (isFormData(formData)) {
    requestBody = formData; // send as-is
  } else if (body) {
    try {
      const parsedBody = JSON.parse(body);
      const transformedBody = deepUnderscore(parsedBody);

      // If pduFields exists, preserve its value under the transformed key
      if ('pduFields' in parsedBody && 'pdu_fields' in transformedBody) {
        transformedBody.pdu_fields = parsedBody.pduFields;
      }

      requestBody = JSON.stringify(transformedBody);
    } catch (e) {
      // fallback: send as-is if parsing fails
      requestBody = body;
    }
  }
  const request: RequestInit = {
    headers,
    body: requestBody,
    method: options.method,
    signal: controller.signal,
  };

  if (config.WITH_CREDENTIALS) {
    request.credentials = config.CREDENTIALS;
  }

  onCancel(() => controller.abort());
  let  response = await fetch(url, request);
  const content = await response.json();
  try {
    if (response?.status == 403&&content?.detail!=="Authentication credentials were not provided.") {
      window.location.href = '/access-denied/';
    }
  }catch (error) {
    console.error(error);
  }
  response.json = async () => {
    let camelized = deepCamelize(content);
    // Special handling for pdu_fields
    if ('pdu_fields' in content && 'pduFields' in camelized) {
      camelized.pduFields = content.pdu_fields;
    }
    // Special handling for flex_fields
    if ('flex_fields' in content && 'flexFields' in camelized) {
      camelized.flexFields = content.flex_fields;
    }
    return camelized;
  };
  return response;
};

export const getResponseHeader = (
  response: Response,
  responseHeader?: string,
): string | undefined => {
  if (responseHeader) {
    const content = response.headers.get(responseHeader);
    if (isString(content)) {
      return content;
    }
  }
  return undefined;
};

export const getResponseBody = async (response: Response): Promise<any> => {
  if (response.status !== 204) {
    try {
      const contentType = response.headers.get('Content-Type');
      if (contentType) {
        const jsonTypes = ['application/json', 'application/problem+json'];
        const isJSON = jsonTypes.some((type) =>
          contentType.toLowerCase().startsWith(type),
        );
        if (isJSON) {
          return await response.json();
        } else {
          return await response.text();
        }
      }
    } catch (error) {
      console.error(error);
    }
  }
  return undefined;
};

export const catchErrorCodes = (
  options: ApiRequestOptions,
  result: ApiResult,
): void => {
  const errors: Record<number, string> = {
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    500: 'Internal Server Error',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    ...options.errors,
  };

  const error = errors[result.status];
  if (error) {
    throw new ApiError(options, result, error);
  }

  if (!result.ok) {
    const errorStatus = result.status ?? 'unknown';
    const errorStatusText = result.statusText ?? 'unknown';
    const errorBody = (() => {
      try {
        return JSON.stringify(result.body, null, 2);
      } catch (e) {
        return undefined;
      }
    })();

    throw new ApiError(
      options,
      result,
      `Generic Error: status: ${errorStatus}; status text: ${errorStatusText}; body: ${errorBody}`,
    );
  }
};

/**
 * Request method
 * @param config The OpenAPI configuration object
 * @param options The request options from the service
 * @returns CancelablePromise<T>
 * @throws ApiError
 */
export const request = <T>(
  config: OpenAPIConfig,
  options: ApiRequestOptions,
): CancelablePromise<T> => {
  return new CancelablePromise(async (resolve, reject, onCancel) => {
    try {
      const url = getUrl(config, options);
      const formData = getFormData(options);
      const body = getRequestBody(options);
      const headers = await getHeaders(config, options);

      if (!onCancel.isCancelled) {
        const response = await sendRequest(
          config,
          options,
          url,
          body,
          formData,
          headers,
          onCancel,
        );
        const responseBody = await getResponseBody(response);
        const responseHeader = getResponseHeader(
          response,
          options.responseHeader,
        );

        const result: ApiResult = {
          url,
          ok: response.ok,
          status: response.status,
          statusText: response.statusText,
          body: responseHeader ?? responseBody,
        };

        catchErrorCodes(options, result);

        resolve(result.body);
      }
    } catch (error) {
      reject(error);
    }
  });
};
