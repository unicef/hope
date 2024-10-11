import { MockedProvider } from '@apollo/react-testing';
import * as React from 'react';
import { act } from 'react';
import wait from 'waait';
import { RegistrationDataImportTable } from '.';
import { render, ApolloLoadingLink } from '../../../../testUtils/testUtils';
import { fakeApolloAllRegistrationDataImports } from '../../../../../fixtures/registration/fakeApolloAllRegistrationDataImports';

const initialFilter = {
  search: '',
  importedBy: '',
  status: '',
  sizeMin: '',
  sizeMax: '',
  importDateRangeMin: '',
  importDateRangeMax: '',
};

describe('containers/tables/rdi/RegistrationDataImportTable', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider mocks={fakeApolloAllRegistrationDataImports}>
        <RegistrationDataImportTable filter={initialFilter} canViewDetails />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', () => {
    const { container } = render(
      <MockedProvider mocks={fakeApolloAllRegistrationDataImports}>
        <RegistrationDataImportTable filter={initialFilter} canViewDetails />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
