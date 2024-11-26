import { fakeIndividual } from '../../../../../../fixtures/population/fakeIndividual';
import { RegistrationIndividualAdditionalRegistrationInformation } from '.';
import { fakeAllIndividualsFlexFieldsAttributes } from '../../../../../../fixtures/core/fakeAllIndividualsFlexFieldsAttributes';
import { render } from '../../../../../testUtils/testUtils';

describe('components/rdi/details/individual/RegistrationIndividualAdditionalRegistrationInformation', () => {
  it('should render', () => {
    const { container } = render(
      <RegistrationIndividualAdditionalRegistrationInformation
        individual={fakeIndividual}
        flexFieldsData={fakeAllIndividualsFlexFieldsAttributes}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
