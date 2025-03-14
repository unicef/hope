import '@testing-library/jest-dom';
import { screen } from '@testing-library/react';
import { renderWithProviders } from 'src/testUtils/testUtils';
import { expect, it } from 'vitest';
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

  const table = await screen.findByRole('table');
  const tableRows = await screen.findAllByRole('row');

  expect(table).toBeInTheDocument();
  expect(tableRows).toHaveLength(6);

  expect(asFragment()).toMatchSnapshot();
});
