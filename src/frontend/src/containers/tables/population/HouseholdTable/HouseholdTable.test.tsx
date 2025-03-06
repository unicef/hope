import { expect, it } from 'vitest';
import { waitFor, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { renderWithProviders } from 'src/testUtils/testUtils';
import { HouseholdTable } from './HouseholdTable';

it('HouseholdTable renders correctly after data is fetched', async () => {
  const { asFragment } = renderWithProviders(
    <HouseholdTable
      filter={{
        search: '',
        documentType: '',
        documentNumber: '',
        residenceStatus: '',
        admin1: '',
        admin2: '',
        householdSizeMin: '',
        householdSizeMax: '',
        orderBy: 'unicef_id',
        withdrawn: '',
      }}
      canViewDetails={true}
    />,
  );

  await waitFor(() => {
    expect(screen.getByTestId('universal-rest-table')).toBeInTheDocument();
  });

  await waitFor(() => {
    const rows = screen
      .getByTestId('universal-rest-table')
      .querySelectorAll('tr');
    expect(rows.length).toBeGreaterThan(0);
  });

  expect(asFragment()).toMatchSnapshot();
});
