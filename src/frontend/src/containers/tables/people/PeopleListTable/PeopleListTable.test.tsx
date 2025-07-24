import { setupCommonMocks } from 'src/testUtils/commonMocks';
setupCommonMocks();

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderWithProviders } from 'src/testUtils/testUtils';
import { PeopleListTable } from './PeopleListTable';
import { RestService } from '@restgenerated/services/RestService';
import { restBusinessAreasProgramsIndividualsList } from 'src/mocks/responses/restBusinessAreasProgramsIndividualsList';

describe('PeopleListTable', () => {
  let queryClient: QueryClient;

  const mockFilter = {
    search: '',
    documentType: '',
    documentNumber: '',
    sex: '',
    ageMin: null,
    ageMax: null,
    admin1: '',
    admin2: '',
    flags: [],
    status: '',
    lastRegistrationDateMin: null,
    lastRegistrationDateMax: null,
    orderBy: 'unicef_id',
  };

  const defaultProps = {
    businessArea: 'afghanistan',
    filter: mockFilter,
    canViewDetails: true,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    // Mock RestService methods
    vi.mocked(
      RestService.restBusinessAreasProgramsIndividualsList,
    ).mockResolvedValue(restBusinessAreasProgramsIndividualsList as any);
  });

  it('renders people list table with data', async () => {
    const { container } = renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <PeopleListTable {...defaultProps} />
      </QueryClientProvider>,
    );

    // Wait for the component to render and make the API call
    await vi.waitFor(() => {
      expect(
        RestService.restBusinessAreasProgramsIndividualsList,
      ).toHaveBeenCalledWith(
        expect.objectContaining({
          businessAreaSlug: 'afghanistan',
          programSlug: 'test-program',
        }),
      );
    });

    // Verify the component rendered
    expect(container).toBeTruthy();
  });

  it('renders empty table when no individuals are available', async () => {
    const emptyData = {
      count: 0,
      next: null,
      previous: null,
      results: [],
    };

    vi.mocked(
      RestService.restBusinessAreasProgramsIndividualsList,
    ).mockResolvedValue(emptyData);

    const { container } = renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <PeopleListTable {...defaultProps} />
      </QueryClientProvider>,
    );

    // Wait for the API call to complete
    await vi.waitFor(() => {
      expect(
        RestService.restBusinessAreasProgramsIndividualsList,
      ).toHaveBeenCalled();
    });

    // Verify the component rendered
    expect(container).toBeTruthy();
  });
});
