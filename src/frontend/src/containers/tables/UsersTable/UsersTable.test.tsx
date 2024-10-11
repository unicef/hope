import { MockedProvider } from '@apollo/react-testing';
import * as React from 'react';
import { act } from 'react';
import wait from 'waait';
import { UsersTable } from '.';
import { render, ApolloLoadingLink } from '../../../testUtils/testUtils';
import { fakeApolloAllUsers } from '../../../../fixtures/users/fakeApolloAllUsers';

describe('containers/tables/UsersTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllUsers}>
        <UsersTable filter={{}} />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllUsers}>
        <UsersTable filter={{}} />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
