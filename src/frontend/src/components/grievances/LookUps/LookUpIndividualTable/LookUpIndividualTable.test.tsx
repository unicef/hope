import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderWithProviders, waitFor } from 'src/testUtils/testUtils';
import { setupCommonMocks } from 'src/testUtils/commonMocks';
import { LookUpIndividualTable } from './LookUpIndividualTable';
import { RestService } from '@restgenerated/services/RestService';
import type { PaginatedIndividualListList } from '@restgenerated/models/PaginatedIndividualListList';

// Setup common mocks (useBaseUrl, useProgramContext, react-router-dom, utils, RestService)
setupCommonMocks();

describe('LookUpIndividualTable', () => {
  let queryClient: QueryClient;

  const mockIndividualsData: PaginatedIndividualListList = {
    next: null,
    previous: null,
    results: [],
  };

  const baseFilter = {
    search: '',
    phone: '',
    documentType: '',
    documentNumber: '',
    admin2: '',
    sex: '',
    ageMin: '',
    ageMax: '',
    birthDate: '',
    flags: [],
    status: '',
    lastRegistrationDateMin: '',
    lastRegistrationDateMax: '',
    orderBy: 'unicef_id',
  };

  const renderTable = (filter) =>
    renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <LookUpIndividualTable
          filter={filter}
          setFieldValue={vi.fn()}
          valuesInner={{}}
          selectedIndividual={null}
          selectedHousehold={null}
          setSelectedIndividual={vi.fn()}
          setSelectedHousehold={vi.fn()}
        />
      </QueryClientProvider>,
    );

  const lastListCallParams = () =>
    vi.mocked(RestService.restBusinessAreasProgramsIndividualsList).mock
      .calls[0][0];

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    vi.mocked(
      RestService.restBusinessAreasProgramsIndividualsList,
    ).mockResolvedValue(mockIndividualsData);
  });

  it('forwards filters using the REST parameter names', async () => {
    renderTable({
      ...baseFilter,
      ageMin: '18',
      ageMax: '65',
      admin2: 'admin-area-1',
      phone: '1234567',
      birthDate: '1998-01-15',
      lastRegistrationDateMin: '2023-01-01',
      lastRegistrationDateMax: '2023-12-31',
    });

    await waitFor(() =>
      expect(
        RestService.restBusinessAreasProgramsIndividualsList,
      ).toHaveBeenCalled(),
    );

    const params = lastListCallParams();

    expect(params).toMatchObject({
      ageMin: '18',
      ageMax: '65',
      admin2: 'admin-area-1',
      phone: '1234567',
      birthDate: '1998-01-15',
      // DateFromToRangeFilter: `after` is the lower bound, `before` the upper one
      lastRegistrationDateAfter: '2023-01-01',
      lastRegistrationDateBefore: '2023-12-31',
    });

    // Legacy GraphQL-shaped variables the REST endpoint does not accept
    expect(params).not.toHaveProperty('age');
    expect(params).not.toHaveProperty('lastRegistrationDate');
  });

  it('drops a phone search that is too short to be accepted', async () => {
    renderTable({ ...baseFilter, phone: '123' });

    await waitFor(() =>
      expect(
        RestService.restBusinessAreasProgramsIndividualsList,
      ).toHaveBeenCalled(),
    );

    // sanitized to '', then dropped by filterEmptyParams — nothing reaches the API
    expect(lastListCallParams()).not.toHaveProperty('phone');
  });

  it('does not throw when the filter omits phone and birthDate', async () => {
    const { phone, birthDate, ...filterWithoutNewFields } = baseFilter;
    void phone;
    void birthDate;

    renderTable(filterWithoutNewFields);

    await waitFor(() =>
      expect(
        RestService.restBusinessAreasProgramsIndividualsList,
      ).toHaveBeenCalled(),
    );

    const params = lastListCallParams();
    expect(params).not.toHaveProperty('phone');
    expect(params).not.toHaveProperty('birthDate');
  });
});
