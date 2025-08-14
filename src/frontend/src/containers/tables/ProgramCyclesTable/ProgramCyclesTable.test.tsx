import { setupCommonMocks } from 'src/testUtils/commonMocks';
setupCommonMocks();

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderWithProviders } from 'src/testUtils/testUtils';
import { act } from '@testing-library/react';
import ProgramCyclesTablePaymentModule from './ProgramCyclesTable';
import { RestService } from '@restgenerated/services/RestService';
import { restBusinessAreasProgramsCyclesList } from 'src/mocks/responses/restBusinessAreasProgramsCyclesList';

describe('ProgramCyclesTable', () => {
  let queryClient: QueryClient;

  const mockProgram = {
    id: 'test-program-id',
    name: 'Test Program',
    status: 'ACTIVE',
  };

  const mockFilters = {
    search: '',
    status: '',
    startDate: null,
    endDate: null,
    totalEntitledQuantityFrom: null,
    totalEntitledQuantityTo: null,
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
      RestService.restBusinessAreasProgramsCyclesList,
    ).mockResolvedValue(restBusinessAreasProgramsCyclesList);

    // Set up mock implementations for program cycle actions on RestService
    vi.mocked(
      RestService.restBusinessAreasProgramsCyclesFinishCreate,
    ).mockResolvedValue({
      message: 'Programme Cycle Finished',
    });
    vi.mocked(
      RestService.restBusinessAreasProgramsCyclesReactivateCreate,
    ).mockResolvedValue({
      message: 'Programme Cycle Reactivated',
    });
  });

  it('renders program cycles table with data', async () => {
    const { findByText, getByText } = renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <ProgramCyclesTablePaymentModule
          program={mockProgram}
          filters={mockFilters}
        />
      </QueryClientProvider>,
    );

    // Wait for table to load and check for program cycle titles
    await findByText('Emergency Response Cycle Q1');
    expect(getByText('Education Support Cycle Q2')).toBeTruthy();
    expect(getByText('Health Initiative Cycle Q3')).toBeTruthy();

    // Check table headers
    expect(getByText('Programme Cycle Title')).toBeTruthy();
    expect(getByText('Status')).toBeTruthy();
    expect(getByText('Total Entitled Quantity (USD)')).toBeTruthy();

    // Verify REST service was called with correct parameters
    expect(
      RestService.restBusinessAreasProgramsCyclesList,
    ).toHaveBeenCalledWith(
      expect.objectContaining({
        businessAreaSlug: 'afghanistan',
        programSlug: undefined,
        offset: 0,
        limit: 5,
        ordering: 'created_at',
      }),
    );
  });

  it('renders empty table when no program cycles are available', async () => {
    const emptyData = {
      next: null,
      previous: null,
      results: [],
      count: 0,
    };

    vi.mocked(
      RestService.restBusinessAreasProgramsCyclesList,
    ).mockResolvedValue(emptyData);

    const { findByText } = renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <ProgramCyclesTablePaymentModule
          program={mockProgram}
          filters={mockFilters}
        />
      </QueryClientProvider>,
    );

    // Wait for the table headers to appear
    await findByText('Programme Cycle Title');

    // Verify REST service was called
    expect(RestService.restBusinessAreasProgramsCyclesList).toHaveBeenCalled();
  });

  it('displays correct action buttons based on cycle status', async () => {
    const { findByText, getByText, queryByText } = renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <ProgramCyclesTablePaymentModule
          program={mockProgram}
          filters={mockFilters}
        />
      </QueryClientProvider>,
    );

    // Wait for data to load
    await findByText('Emergency Response Cycle Q1');

    // Check that Active cycle has FINISH button
    expect(getByText('FINISH')).toBeTruthy();

    // Check that Finished cycle has REACTIVATE button
    expect(getByText('REACTIVATE')).toBeTruthy();

    // Verify there's only one FINISH button and one REACTIVATE button
    // (since we have one Active cycle and one Finished cycle)
    const allButtons = document.querySelectorAll('button');
    const finishButtons = Array.from(allButtons).filter(
      (button) => button.textContent === 'FINISH',
    );
    const reactivateButtons = Array.from(allButtons).filter(
      (button) => button.textContent === 'REACTIVATE',
    );

    expect(finishButtons.length).toBe(1);
    expect(reactivateButtons.length).toBe(1);
  });

  it('applies filters correctly to API calls', async () => {
    const filterWithData = {
      search: 'emergency',
      status: 'ACTIVE',
      startDate: '2023-01-01',
      endDate: '2023-12-31',
      totalEntitledQuantityFrom: 50000,
      totalEntitledQuantityTo: 500000,
    };

    renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <ProgramCyclesTablePaymentModule
          program={mockProgram}
          filters={filterWithData}
        />
      </QueryClientProvider>,
    );

    // Wait for API call
    await vi.waitFor(() => {
      expect(
        RestService.restBusinessAreasProgramsCyclesList,
      ).toHaveBeenCalledWith(
        expect.objectContaining({
          businessAreaSlug: 'afghanistan',
          programSlug: undefined,
          search: 'emergency',
          status: 'ACTIVE',
          startDate: '2023-01-01',
          endDate: '2023-12-31',
          totalEntitledQuantityFrom: 50000,
          totalEntitledQuantityTo: 500000,
          ordering: 'created_at',
        }),
      );
    });
  });

  it('handles finish program cycle action', async () => {
    const { findByText, getByText } = renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <ProgramCyclesTablePaymentModule
          program={mockProgram}
          filters={mockFilters}
        />
      </QueryClientProvider>,
    );

    // Wait for data to load
    await findByText('Emergency Response Cycle Q1');

    // Click the FINISH button
    const finishButton = getByText('FINISH');

    await act(async () => {
      finishButton.click();
    });

    // Wait for the mutation to complete and API to be called
    await vi.waitFor(() => {
      expect(
        RestService.restBusinessAreasProgramsCyclesFinishCreate,
      ).toHaveBeenCalledWith(
        expect.objectContaining({
          businessAreaSlug: 'afghanistan',
          programSlug: 'test-program',
          id: 'cycle-1',
        }),
      );
    });
  });

  it('handles reactivate program cycle action', async () => {
    const { findByText, getByText } = renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <ProgramCyclesTablePaymentModule
          program={mockProgram}
          filters={mockFilters}
        />
      </QueryClientProvider>,
    );

    // Wait for data to load
    await findByText('Emergency Response Cycle Q1');

    // Click the REACTIVATE button
    const reactivateButton = getByText('REACTIVATE');

    await act(async () => {
      reactivateButton.click();
    });

    // Wait for the mutation to complete and API to be called
    await vi.waitFor(() => {
      expect(
        RestService.restBusinessAreasProgramsCyclesReactivateCreate,
      ).toHaveBeenCalledWith(
        expect.objectContaining({
          businessAreaSlug: 'afghanistan',
          programSlug: 'test-program',
          id: 'cycle-2',
        }),
      );
    });
  });
});
