import { filterEmptyParams } from './utils';

/**
 * Creates standardized API parameters with specified primary keys and filtered additional params
 * Optionally adds pagination parameters if withPagination is true
 *
 * @param primaryParams - Object with primary parameters (business area, program ID, etc.)
 * @param additionalParams - Any additional parameters to include after filtering empty values
 * @param options - Optional configuration
 * @param options.withPagination - Whether to add pagination parameters (default: false)
 * @param options.rowsPerPage - Number of items per page (default: 10)
 * @param options.pageNumber - Current page number, zero-based (default: 0)
 * @returns Combined object with primary parameters and filtered additional parameters
 */
export const createApiParams = <
  P extends Record<string, any>,
  T extends Record<string, any> = Record<string, never>,
>(
  primaryParams: P,
  additionalParams?: T,
  options?: {
    withPagination?: boolean;
    rowsPerPage?: number;
    pageNumber?: number;
  },
): P & Record<string, any> => {
  const filteredParams = additionalParams
    ? filterEmptyParams(additionalParams)
    : {};

  // Combine primary params with filtered additional params
  const combinedParams = {
    ...primaryParams,
    ...filteredParams,
  };

  // Add pagination if requested
  if (options?.withPagination) {
    const rowsPerPage = options.rowsPerPage || 10;
    const pageNumber = options.pageNumber || 0;

    return {
      ...combinedParams,
      limit:
        filteredParams.limit !== undefined ? filteredParams.limit : rowsPerPage,
      offset:
        filteredParams.offset !== undefined
          ? filteredParams.offset
          : pageNumber * rowsPerPage,
    };
  }

  return combinedParams;
};

/**
 * Adds pagination parameters to query variables if they're not already present
 *
 * @param queryVariables - The original query variables object
 * @param rowsPerPage - Number of items per page (defaults to 10)
 * @param pageNumber - Current page number, zero-based (defaults to 0)
 * @returns Query variables with pagination parameters added
 */
export const withPagination = <T extends Record<string, any>>(
  queryVariables: T,
  rowsPerPage: number = 10,
  pageNumber: number = 0,
): T & { limit: number; offset: number } => {
  return {
    ...queryVariables,
    limit:
      queryVariables.limit !== undefined ? queryVariables.limit : rowsPerPage,
    offset:
      queryVariables.offset !== undefined
        ? queryVariables.offset
        : pageNumber * rowsPerPage,
  };
};
