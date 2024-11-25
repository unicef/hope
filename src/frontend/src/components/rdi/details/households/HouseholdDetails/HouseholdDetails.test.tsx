import { fakeHousehold } from 'fixtures/population/fakeHousehold';
import { fakeHouseholdChoices } from '../../../../../../fixtures/population/fakeHouseholdChoices';
import { render } from '../../../../../testUtils/testUtils';
import { HouseholdDetails } from './HouseholdDetails';

describe('components/rdi/details/households/HouseholdDetails', () => {
  it('should render', () => {
    const { container } = render(
      <HouseholdDetails
        household={fakeHousehold}
        choicesData={fakeHouseholdChoices}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
