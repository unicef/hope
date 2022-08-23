import { MockedProvider } from '@apollo/react-testing';
import { act } from '@testing-library/react';
import React from 'react';
import wait from 'waait';
import { LockedTargetPopulationTable } from '.';
import { fakeApolloCandidateHouseholdsListByTargetingCriteria } from '../../../../../../fixtures/targeting/fakeApolloCandidateHouseholdsListByTargetingCriteria';
import { ApolloLoadingLink, render } from '../../../../../testUtils/testUtils';

describe('containers/tables/targeting/TargetPopulation/ApprovedTargeting', () => {
  it('should render with data', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeApolloCandidateHouseholdsListByTargetingCriteria}
      >
        <LockedTargetPopulationTable
          id={
            'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6ZDYzNWQ0ZDMtNGI1My00MTVkLTkzZWYtNjFlODhjZDg0MWMy'
          }
          canViewDetails={true}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });

  it('should render loading', () => {
    const { container } = render(
      <MockedProvider
        link={new ApolloLoadingLink()}
        addTypename={false}
        mocks={fakeApolloCandidateHouseholdsListByTargetingCriteria}
      >
        <LockedTargetPopulationTable
          id={
            'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6ZDYzNWQ0ZDMtNGI1My00MTVkLTkzZWYtNjFlODhjZDg0MWMy'
          }
          canViewDetails={true}
        />
      </MockedProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});
