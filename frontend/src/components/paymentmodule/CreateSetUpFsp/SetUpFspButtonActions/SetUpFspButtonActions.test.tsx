import { act } from '@testing-library/react';
import React from 'react';
import wait from 'waait';
import { render } from '../../../../testUtils/testUtils';
import { SetUpFspButtonActions } from './SetUpFspButtonActions';


describe('components/paymentmodule/CreateSetUpFsp/SetUpFspButtonActions', () => {
  it('should render', async () => {
    const step = 0;
    const setStep = jest.fn();
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const submitForm = (_values): Promise<void> => Promise.resolve();
    const { container } = render(
      <SetUpFspButtonActions
        step={step}
        submitForm={submitForm}
        businessArea='afghanistan'
        paymentPlanId='asdjkfhsakdjfsd76asdf0sdf=='
        handleBackStep={setStep} />,
    );
    await act(() => wait(0)); // wait for response
    expect(container).toMatchSnapshot();
  });
});
