import * as React from 'react';
import { render } from '../../../../testUtils/testUtils';
import { TotalNumberOfIndividualsReachedSection } from './TotalNumberOfIndividualsReachedSection';
import { fakeSectionIndividualsReached } from '../../../../../fixtures/dashboard/fakeSectionIndividualsReached';
import { fakeChartIndividualsReachedByAgeAndGender } from '../../../../../fixtures/dashboard/fakeChartIndividualsReachedByAgeAndGender';
import { fakeChartIndividualsWithDisabilityReachedByAge } from '../../../../../fixtures/dashboard/fakeChartIndividualsWithDisabilityReachedByAge';

describe('components/dashboard/TotalNumberOfIndividualsReachedSection', () => {
  it('should render', () => {
    const { container } = render(
      <TotalNumberOfIndividualsReachedSection
        data={fakeSectionIndividualsReached}
        chartDataIndividuals={fakeChartIndividualsReachedByAgeAndGender}
        chartDataIndividualsDisability={
          fakeChartIndividualsWithDisabilityReachedByAge
        }
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
