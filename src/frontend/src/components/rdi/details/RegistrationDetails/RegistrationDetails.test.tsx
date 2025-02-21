import { MemoryRouter } from 'react-router-dom';
import { fakeRegistrationDetailedFragment } from '../../../../../fixtures/registration/fakeRegistrationDetailedFragment';
import { render } from '../../../../testUtils/testUtils';
import RegistrationDetails from './RegistrationDetails';

describe('components/rdi/details/RegistrationDetails', () => {
  it('should render', () => {
    const { container } = render(
      <RegistrationDetails registration={fakeRegistrationDetailedFragment} />,
    );
    expect(container).toMatchSnapshot();
  });
});
