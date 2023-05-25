import { MockedProvider } from '@apollo/react-testing';
import React from 'react';
import { fakeApolloPaymentPlan } from '../../../../../fixtures/paymentmodule/fakeApolloPaymentPlan';
import { fakeImportXlsxPpListMutation } from '../../../../../fixtures/paymentmodule/fakeImportXlsxPpListMutation';
import { render } from '../../../../testUtils/testUtils';
import { PERMISSIONS } from '../../../../config/permissions';
import { ImportXlsxPaymentPlanPaymentList } from './ImportXlsxPaymentPlanPaymentList';

describe('components/paymentmodule/PaymentPlanDetails/ImportXlsxPaymentPlanPaymentList', () => {
  it('should render', async () => {
    //TODO Fix this test

    const { container } = render(
      <MockedProvider addTypename={false} mocks={fakeImportXlsxPpListMutation}>
        <ImportXlsxPaymentPlanPaymentList
          permissions={[PERMISSIONS.PM_IMPORT_XLSX_WITH_ENTITLEMENTS]}
          paymentPlan={fakeApolloPaymentPlan}
        />
      </MockedProvider>,
    );
    expect(container).toMatchSnapshot();
    // await act(() => wait(0)); // wait for response
    //
    // const buttonImport = container.querySelector('[data-cy="button-import"]');
    // expect(buttonImport).toBeInTheDocument();
    // fireEvent.click(buttonImport);
    // //
    // // act(() => {
    // //   buttonImport.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    // // });
    // await act(() => wait(0));
    // const dialog = container.querySelector('[data-cy="dialog-import"]');
    // expect(dialog).toBeInTheDocument();

    // const inputFile = document.querySelector('[data-cy="file-input"]');
    // const buttonImportSubmit = document.querySelector(
    //   '[data-cy="button-import-entitlement"]',
    // );
    // const buttonClose = document.querySelector('[data-cy="close-button"]');
    //
    // expect(inputFile).toBeInTheDocument();
    // expect(buttonImportSubmit).toBeInTheDocument();
    // expect(buttonClose).toBeInTheDocument();
    //
    // const file = new File([new ArrayBuffer(210715200)], 'sample.xlsx', {
    //   type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    // });
    // Object.defineProperty(inputFile, 'files', {
    //   value: [file],
    // });
    //
    // act(() => {
    //   inputFile.dispatchEvent(new Event('change', { bubbles: true }));
    // });
    //
    // act(() => {
    //   buttonImportSubmit.dispatchEvent(
    //     new MouseEvent('click', { bubbles: true }),
    //   );
    // });
    //
    // act(() => {
    //   buttonClose.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    // });
    // expect(container).toMatchSnapshot();
  });
});
