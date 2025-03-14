import { expect, it } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MockedProvider } from '@apollo/client/testing';
import { renderWithProviders } from 'src/testUtils/testUtils';
import { LookUpHouseholdTable } from './LookUpHouseholdTable';
import { MeDocument } from 'src/__generated__/graphql';

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

it('LookUpHouseholdTable renders correctly after data is fetched', async () => {
  const { asFragment } = renderWithProviders(
    <MockedProvider mocks={mocks} addTypename={false}>
      <LookUpHouseholdTable
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
        businessArea="afghanistan"
        choicesData={{}}
        setFieldValue={() => {}}
      />
    </MockedProvider>,
  );

  await waitFor(() => {
    expect(screen.queryByText('No results')).not.toBeInTheDocument();
  });

  const table = await screen.findByRole('table');
  const tableRows = await screen.findAllByRole('row');

  expect(table).toBeInTheDocument();
  expect(tableRows).toHaveLength(6);

  expect(asFragment()).toMatchSnapshot();
});
