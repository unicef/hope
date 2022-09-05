import React from 'react';
import { MockedProvider } from '@apollo/react-testing';
import { act } from 'react-dom/test-utils';
import wait from 'waait';
import { fakeImportXlsxPpListMutation } from '../../../../../fixtures/payments/fakeImportXlsxPpListMutation';
import { fakeApolloPaymentPlan } from '../../../../../fixtures/payments/fakeApolloPaymentPlan';
import { render } from '../../../../testUtils/testUtils';
import { ImportXlsxPaymentPlanPaymentList } from './ImportXlsxPaymentPlanPaymentList';

describe('components/paymentmodule/PaymentPlanDetails/ImportXlsxPaymentPlanPaymentList', () => {
  it('should render', async () => {
    const { container } = render(
      <MockedProvider
        addTypename={false}
        mocks={fakeImportXlsxPpListMutation}
      >
        <ImportXlsxPaymentPlanPaymentList paymentPlan={fakeApolloPaymentPlan} />
      </MockedProvider>,
    );

    const buttonImport = container.querySelector('[data-cy="button-import"]');
    expect(buttonImport).toBeInTheDocument();

    act(() => {
      buttonImport.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });

    const inputFile = document.querySelector<HTMLInputElement>('input[type="file"]');
    const buttonImportSubmit = document.querySelector('[data-cy="button-import-submit"]');
    const buttonClose = document.querySelector('[data-cy="close-button"]');

    expect(inputFile).toBeInTheDocument();
    expect(buttonImportSubmit).toBeInTheDocument();
    expect(buttonClose).toBeInTheDocument();

    const file = new File([new ArrayBuffer(210715200)], 'sample.xlsx', {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    });
    Object.defineProperty(inputFile, 'files', {
      value: [file],
    });

    act(() => {
      inputFile.dispatchEvent(new Event('change', { bubbles: true }));
    });

    act(() => {
      buttonImportSubmit.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });

    act(() => {
      buttonClose.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });
    
    // expect(inputFile).not.toBeInTheDocument();

    await act(() => wait(0)); // wait for response

    expect(container).toMatchSnapshot();
  });
});
