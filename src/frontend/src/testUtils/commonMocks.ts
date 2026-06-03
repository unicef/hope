import { vi } from 'vitest';
import React from 'react';

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    businessArea: 'afghanistan',
    programId: 'test-program',
    baseUrl: 'afghanistan/test-program',
  }),
}));

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

vi.mock('@utils/utils', () => utilsMock);

vi.mock('@restgenerated/services/RestService', () => ({
  RestService: {
    restBusinessAreasProgramsHouseholdsList: vi.fn(),
    restBusinessAreasProgramsHouseholdsCountRetrieve: vi.fn(),
    restBusinessAreasProgramsIndividualsList: vi.fn(),
    restBusinessAreasProgramsHouseholdsMembersList: vi.fn(),
    restBusinessAreasProgramsList: vi.fn(),
    restBusinessAreasProgramsCountRetrieve: vi.fn(),
    restBusinessAreasUsersProfileRetrieve: vi.fn(() =>
      Promise.resolve({
        id: 'test-user',
        username: 'testuser',
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
  },
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
  decodeIdString: vi.fn((id) => id),
  programCycleStatusToColor: vi.fn(() => 'primary'),
  individualStatusToColor: vi.fn(() => '#000000'),
};

// All mocks are registered at module top-level above.
// This function is kept for backward compatibility.
export const setupCommonMocks = () => {};
