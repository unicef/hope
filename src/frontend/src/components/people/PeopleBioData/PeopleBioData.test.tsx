import { act } from 'react';
import wait from 'waait';
import { MockedProvider } from '@apollo/react-testing';
import { render } from '../../../testUtils/testUtils';
import { fakeHouseholdChoices } from '../../../../fixtures/population/fakeHouseholdChoices';
import { fakeIndividual } from '../../../../fixtures/population/fakeIndividual';
import { fakeApolloAllGrievances } from '../../../../fixtures/grievances/fakeApolloAllGrievances';
import { fakeGrievancesChoices } from '../../../../fixtures/grievances/fakeGrievancesChoices';
import { PeopleBioData } from './PeopleBioData';
import { fakeBaseUrl } from '../../../../fixtures/core/fakeBaseUrl';

describe('components/population/IndividualBioData', () => {
  it('should render', async () => {
    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeApolloAllGrievances}>
        <PeopleBioData
          baseUrl={fakeBaseUrl}
          businessArea="afghanistan"
          individual={fakeIndividual}
          choicesData={fakeHouseholdChoices}
          grievancesChoices={fakeGrievancesChoices}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response
    expect(container).toMatchSnapshot();
  });
});
