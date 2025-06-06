import { vi } from 'vitest';
import React from 'react';

/**
 * Common mock for @hooks/useBaseUrl hook
 */
export const mockUseBaseUrl = (
  businessArea = 'afghanistan',
  programId = 'test-program',
  baseUrl = 'afghanistan/test-program',
) => {
  vi.mock('@hooks/useBaseUrl', () => ({
    useBaseUrl: () => ({ businessArea, programId, baseUrl }),
  }));
};

/**
 * Common mock for useProgramContext hook
 */
export const mockUseProgramContext = (
  groupLabel = 'Household',
  groupLabelPlural = 'Households',
) => {
  vi.mock('src/programContext', () => ({
    useProgramContext: () => ({
      selectedProgram: {
        beneficiaryGroup: {
          groupLabel,
          groupLabelPlural,
        },
      },
    }),
  }));
};

/**
 * Common mock for react-router-dom
 */
export const mockReactRouterDom = () => {
  vi.mock('react-router-dom', () => ({
    useNavigate: () => vi.fn(),
    useLocation: () => ({
      pathname: '/test-path',
      search: '',
      hash: '',
      state: null,
      key: 'test-key',
    }),
    Link: ({ children, to, ...props }: any) =>
      React.createElement('a', { href: to, ...props }, children),
  }));
};
/**
 * Common mock for @utils/utils module
 */
export const utilsMock = {
  createApiParams: vi.fn((baseParams, queryParams, options) => ({
    ...baseParams,
    ...queryParams,
    ...options,
  })),
  adjustHeadCells: vi.fn((headCells) => headCells),
  formatCurrencyWithSymbol: vi.fn(
    (amount, currency) => `${amount} ${currency}`,
  ),
  householdStatusToColor: vi.fn(() => '#000000'),
  filterEmptyParams: vi.fn((params) => {
    if (!params) return {};
    return Object.fromEntries(
      Object.entries(params).filter(([, value]) => {
        return value !== undefined && value !== null && value !== '';
      }),
    );
  }),
  opacityToHex: vi.fn((opacity) =>
    Math.round(opacity * 255)
      .toString(16)
      .padStart(2, '0'),
  ),
  isPermissionDeniedError: vi.fn((error) => error?.response?.status === 403),
  dateToIsoString: vi.fn((date) => date?.toISOString?.() || date),
  choicesToDict: vi.fn((choices) => {
    if (!choices) return {};
    return choices.reduce((acc, choice) => {
      acc[choice.value] = choice.name;
      return acc;
    }, {});
  }),
  populationStatusToColor: vi.fn(() => 'primary'),
  sexToCapitalize: vi.fn(
    (sex) => sex?.charAt(0).toUpperCase() + sex?.slice(1).toLowerCase(),
  ),
  programStatusToColor: vi.fn(() => 'primary'),
  formatCurrency: vi.fn((amount) => `$${amount?.toLocaleString() || '0'}`),
  columnToOrderBy: vi.fn((column) => column || 'name'),
};

/**
 * Helper function to mock the @utils/utils module
 */
export const mockUtils = () => {
  vi.mock('@utils/utils', () => utilsMock);
};

/**
 * Common mock for RestService
 */
export const mockRestService = () => {
  vi.mock('@restgenerated/services/RestService', () => ({
    RestService: {
      restBusinessAreasProgramsHouseholdsList: vi.fn(),
      restBusinessAreasProgramsHouseholdsCountRetrieve: vi.fn(),
      restBusinessAreasProgramsIndividualsList: vi.fn(),
      restBusinessAreasProgramsHouseholdsMembersList: vi.fn(),
      restBusinessAreasProgramsList: vi.fn(),
      restBusinessAreasProgramsCountRetrieve: vi.fn(),
      restBusinessAreasUsersProfileRetrieve: vi.fn(),
      // Add other commonly used RestService methods as needed
    },
  }));
};

/**
 * Helper function to set up all common mocks at once
 * Usage in test files:
 *
 * import { setupCommonMocks } from 'src/testUtils/commonMocks';
 *
 * // At the top level of your test file
 * setupCommonMocks();
 */
export const setupCommonMocks = () => {
  // Mock useBaseUrl
  vi.mock('@hooks/useBaseUrl', () => ({
    useBaseUrl: () => ({
      businessArea: 'afghanistan',
      programId: 'test-program',
      baseUrl: 'afghanistan/test-program',
    }),
  }));

  // Mock useProgramContext
  vi.mock('src/programContext', () => ({
    useProgramContext: () => ({
      selectedProgram: {
        beneficiaryGroup: {
          groupLabel: 'Household',
          groupLabelPlural: 'Households',
        },
      },
    }),
  }));

  mockReactRouterDom();
  mockUtils();
  mockRestService();
};
