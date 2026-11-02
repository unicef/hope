import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fireEvent } from '@testing-library/react';
import { renderWithProviders } from 'src/testUtils/testUtils';
import { PeopleFilter } from './PeopleFilter';

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    businessArea: 'afghanistan',
    programId: 'test-program',
    baseUrl: 'afghanistan/test-program',
    isAllPrograms: false,
  }),
}));

vi.mock('src/programContext', () => ({
  useProgramContext: () => ({
    selectedProgram: {
      dataCollectingType: { type: 'STANDARD' },
      beneficiaryGroup: {
        memberLabel: 'Individual',
        groupLabel: 'Household',
        groupLabelPlural: 'Households',
      },
    },
  }),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>(
    'react-router-dom',
  );
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    useLocation: () => ({
      pathname: '/test',
      search: '',
      hash: '',
      state: null,
      key: 'test',
    }),
  };
});

const initialFilter = {
  search: '',
  phone: '',
  documentType: '',
  documentNumber: '',
  admin1: '',
  admin2: '',
  sex: '',
  ageMin: '',
  ageMax: '',
  flags: [],
  orderBy: 'unicef_id',
  status: '',
  lastRegistrationDateMin: '',
  lastRegistrationDateMax: '',
  rdiId: '',
};

const choicesData = {
  documentTypeChoices: [],
  flagChoices: [],
  sexChoices: [],
  statusChoices: [],
} as any;

describe('PeopleFilter — phone input apply-gate', () => {
  let setFilter: (filter: any) => void;
  let setAppliedFilter: (filter: any) => void;

  beforeEach(() => {
    setFilter = vi.fn();
    setAppliedFilter = vi.fn();
  });

  it('blocks Apply and does NOT call setAppliedFilter when phone has < 4 digits', () => {
    const { container } = renderWithProviders(
      <PeopleFilter
        filter={{ ...initialFilter, phone: '123' }}
        choicesData={choicesData}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={initialFilter}
        setAppliedFilter={setAppliedFilter}
      />,
    );

    const applyButton = container.querySelector(
      '[data-cy="button-filters-apply"]',
    ) as HTMLElement;
    expect(applyButton).toBeTruthy();
    fireEvent.click(applyButton);

    expect(setAppliedFilter).not.toHaveBeenCalled();
  });

  it('blocks Apply when spaced digits total < 4 after stripping', () => {
    const { container } = renderWithProviders(
      <PeopleFilter
        filter={{ ...initialFilter, phone: ' 1 2 3 ' }}
        choicesData={choicesData}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={initialFilter}
        setAppliedFilter={setAppliedFilter}
      />,
    );

    const applyButton = container.querySelector(
      '[data-cy="button-filters-apply"]',
    ) as HTMLElement;
    fireEvent.click(applyButton);

    expect(setAppliedFilter).not.toHaveBeenCalled();
  });

  it('fires Apply (setAppliedFilter called) when phone has exactly 4 digits', () => {
    const { container } = renderWithProviders(
      <PeopleFilter
        filter={{ ...initialFilter, phone: '1234' }}
        choicesData={choicesData}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={initialFilter}
        setAppliedFilter={setAppliedFilter}
      />,
    );

    const applyButton = container.querySelector(
      '[data-cy="button-filters-apply"]',
    ) as HTMLElement;
    fireEvent.click(applyButton);

    expect(setAppliedFilter).toHaveBeenCalledTimes(1);
    expect(setAppliedFilter).toHaveBeenCalledWith(
      expect.objectContaining({ phone: '1234' }),
    );
  });

  it('fires Apply when phone is empty (unfiltered baseline, no gate)', () => {
    const { container } = renderWithProviders(
      <PeopleFilter
        filter={{ ...initialFilter, phone: '' }}
        choicesData={choicesData}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={initialFilter}
        setAppliedFilter={setAppliedFilter}
      />,
    );

    const applyButton = container.querySelector(
      '[data-cy="button-filters-apply"]',
    ) as HTMLElement;
    fireEvent.click(applyButton);

    expect(setAppliedFilter).toHaveBeenCalledTimes(1);
  });
});
