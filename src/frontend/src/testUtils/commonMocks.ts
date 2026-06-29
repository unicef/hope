import { vi } from 'vitest';
import React from 'react';

// vi.hoisted() values are initialized before any imports, making them safe for use
// in vi.mock() factory functions. Note: vi.hoisted() results cannot be directly
// exported — use a separate re-export below.
const _useBaseUrlState = vi.hoisted(() => ({
  businessArea: 'afghanistan',
  programId: 'test-program',
  baseUrl: 'afghanistan/test-program',
}));

const _programContextState = vi.hoisted(() => ({
  groupLabel: 'Household',
  groupLabelPlural: 'Households',
}));

const _utilsMock = vi.hoisted(() => ({
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
  decodeIdString: vi.fn((id) => id),
  programCycleStatusToColor: vi.fn(() => 'primary'),
  individualStatusToColor: vi.fn(() => '#000000'),
}));

const _restServiceMethods = vi.hoisted(() => ({
  restBusinessAreasProgramsHouseholdsList: vi.fn(),
  restBusinessAreasProgramsHouseholdsCountRetrieve: vi.fn(),
  restBusinessAreasProgramsIndividualsList: vi.fn(),
  restBusinessAreasProgramsHouseholdsMembersList: vi.fn(),
  restBusinessAreasProgramsList: vi.fn(),
  restBusinessAreasProgramsCountRetrieve: vi.fn(),
  restBusinessAreasUsersProfileRetrieve: vi.fn(() =>
    Promise.resolve({
      id: 'test-user',
      username: 'mock-user',
      permissions: ['can_view_programs'],
    }),
  ),
  restBusinessAreasProgramsCyclesList: vi.fn(),
  restBusinessAreasProgramsCyclesRetrieve: vi.fn(),
  restBusinessAreasProgramsCyclesCreate: vi.fn(),
  restBusinessAreasProgramsCyclesUpdate: vi.fn(),
  restBusinessAreasProgramsCyclesPartialUpdate: vi.fn(),
  restBusinessAreasProgramsCyclesDestroy: vi.fn(),
  restBusinessAreasProgramsCyclesFinishCreate: vi.fn(),
  restBusinessAreasProgramsCyclesReactivateCreate: vi.fn(),
  restBusinessAreasProgramsCyclesCountRetrieve: vi.fn(),
}));

// Top-level vi.mock() registrations — no hoisting warnings
vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({ ..._useBaseUrlState }),
}));

vi.mock('src/programContext', () => ({
  useProgramContext: () => ({
    selectedProgram: {
      beneficiaryGroup: { ..._programContextState },
    },
  }),
}));

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

vi.mock('@utils/utils', () => _utilsMock);

vi.mock('@restgenerated/services/RestService', () => ({
  RestService: _restServiceMethods,
}));

vi.mock('src/api/programCycleApi', () => ({
  finishProgramCycle: vi.fn(),
  reactivateProgramCycle: vi.fn(),
}));

vi.mock('@hooks/useSnackBar', () => ({
  useSnackbar: () => ({
    showMessage: vi.fn(),
  }),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: vi.fn((key) => key),
  }),
}));

// Re-export the hoisted mock object so tests can spy on individual methods
export const utilsMock = _utilsMock;

export const mockUseBaseUrl = (
  businessArea = 'afghanistan',
  programId = 'test-program',
  baseUrl = 'afghanistan/test-program',
) => {
  _useBaseUrlState.businessArea = businessArea;
  _useBaseUrlState.programId = programId;
  _useBaseUrlState.baseUrl = baseUrl;
};

export const mockUseProgramContext = (
  groupLabel = 'Household',
  groupLabelPlural = 'Households',
) => {
  _programContextState.groupLabel = groupLabel;
  _programContextState.groupLabelPlural = groupLabelPlural;
};

export const mockReactRouterDom = () => {
  // vi.mock('react-router-dom') is registered at the top level of this module.
};

export const mockUtils = () => {
  // vi.mock('@utils/utils') is registered at the top level of this module.
};

export const mockRestService = () => {
  // vi.mock('@restgenerated/services/RestService') is registered at the top level of this module.
};

export const setupCommonMocks = () => {
  // All vi.mock() registrations happen at module import time (top-level above).
  // This function resets parameterized mocks to their default values.
  _useBaseUrlState.businessArea = 'afghanistan';
  _useBaseUrlState.programId = 'test-program';
  _useBaseUrlState.baseUrl = 'afghanistan/test-program';
  _programContextState.groupLabel = 'Household';
  _programContextState.groupLabelPlural = 'Households';
};
