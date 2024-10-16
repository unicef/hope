import { MockedProvider } from '@apollo/react-testing';
import { act } from 'react';
import * as React from 'react';
import wait from 'waait';
import { fakeApolloAllCommunicationMessages } from '../../../../../fixtures/communication/fakeApolloAllCommunicationMessages';
import { ApolloLoadingLink, render } from '../../../../testUtils/testUtils';
import { CommunicationTable } from './CommunicationTable';
import { useBaseUrl } from '@hooks/useBaseUrl';

describe('containers/tables//Communication/CommunicationTable', () => {
  it('should render with data', async () => {
    const { programId } = useBaseUrl();
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllCommunicationMessages}
      >
        <CommunicationTable
          filter={{
            targetPopulation: '',
            createdBy: '',
            first: 10,
            orderBy: '-created_at',
            program: programId,
          }}
          canViewDetails={false}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', () => {
    const { programId } = useBaseUrl();
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloAllCommunicationMessages}
      >
        <CommunicationTable
          filter={{
            targetPopulation: '',
            createdBy: '',
            first: 10,
            orderBy: '-created_at',
            program: programId,
          }}
          canViewDetails={false}
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
