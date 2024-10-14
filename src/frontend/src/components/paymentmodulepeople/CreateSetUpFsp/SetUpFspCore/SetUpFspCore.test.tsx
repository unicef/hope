import { act } from 'react';
import * as React from 'react';
import wait from 'waait';
import { MockedProvider } from '@apollo/react-testing';
import { render } from '../../../../testUtils/testUtils';
import { fakeDeliveryMechanisms } from '../../../../../fixtures/paymentmodule/fakeDeliveryMechanisms';
import { fakeChooseDeliveryMechForPaymentPlanMutation } from '../../../../../fixtures/paymentmodule/fakeChooseDeliveryMechForPaymentPlanMutation';
import { PERMISSIONS } from '../../../../config/permissions';
import { SetUpFspCore } from './SetUpFspCore';

describe('components/paymentmodule/CreateSetUpFsp/SetUpFspCore', () => {
  it('should render', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeChooseDeliveryMechForPaymentPlanMutation}
      >
        <SetUpFspCore
          permissions={[PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP]}
          initialValues={{
            deliveryMechanisms: [
              {
                deliveryMechanism: '',
                fsp: '',
                chosenConfiguration: '',
              },
            ],
          }}
        />
      </MockedProvider>,
    );
    await act(() => wait(0)); // wait for response
    expect(container).toMatchSnapshot();
  });
});
