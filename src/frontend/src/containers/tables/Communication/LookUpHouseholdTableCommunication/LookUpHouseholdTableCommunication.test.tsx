import { expect, it } from 'vitest';
import { screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MockedProvider } from '@apollo/client/testing';
import { renderWithProviders } from 'src/testUtils/testUtils';
import { MeDocument } from 'src/__generated__/graphql';
import LookUpHouseholdTableCommunication from './LookUpHouseholdTableCommunication';

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

it('LookUpHouseholdTableCommunication renders correctly after data is fetched', async () => {
  const { asFragment } = renderWithProviders(
    <MockedProvider mocks={mocks} addTypename={false}>
      <LookUpHouseholdTableCommunication
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

  const table = await screen.findByRole('table');
  const tableRows = await screen.findAllByRole('row');

  expect(table).toBeInTheDocument();
  expect(tableRows).toHaveLength(6);

  expect(asFragment()).toMatchSnapshot();
});
