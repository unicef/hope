import * as React from 'react';
import { render } from '../../../../testUtils/testUtils';
import { fakeHousehold } from '../../../../../fixtures/population/fakeHousehold';
import { HouseholdCompositionTable } from '.';

describe('components/population/HouseholdCompositionTable', () => {
  it('should render', () => {
    const { container } = render(
      <HouseholdCompositionTable household={fakeHousehold} />,
    );
    expect(container).toMatchSnapshot();
  });
});
