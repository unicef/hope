import { MockedProvider } from '@apollo/client/testing';
import '@testing-library/jest-dom';
import { screen } from '@testing-library/react';
import { MeDocument } from 'src/__generated__/graphql';
import { renderWithProviders } from 'src/testUtils/testUtils';
import { expect, it } from 'vitest';
import { HouseholdTable } from './HouseholdTable';

const mocks = [
  {
    request: {
      query: MeDocument,
    },
    result: {
      data: {
        me: {
          id: '1',
          name: 'Test User',
          // Add other fields as required by your query
        },
      },
    },
  },
  // Add other mocks if needed
];

it('HouseholdTable renders correctly after data is fetched', async () => {
  const { asFragment } = renderWithProviders(
    <MockedProvider mocks={mocks} addTypename={false}>
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
      />
    </MockedProvider>,
  );

  const table = await screen.findByRole('table');
  const tableRows = await screen.findAllByRole('row');

  expect(table).toBeInTheDocument();
  expect(tableRows).toHaveLength(6);

  expect(asFragment()).toMatchSnapshot();
});
