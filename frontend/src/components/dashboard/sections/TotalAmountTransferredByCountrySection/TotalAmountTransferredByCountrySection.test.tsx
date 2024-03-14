import * as React from 'react';
import { render } from '../../../../testUtils/testUtils';
import { TotalAmountTransferredByCountrySection } from './TotalAmountTransferredByCountrySection';
import { fakeChartTotalTransferredCashByCountry } from '../../../../../fixtures/dashboard/fakeChartTotalTransferredCashByCountry';

describe('components/dashboard/TotalAmountTransferredByCountrySection', () => {
  it('should render', () => {
    const { container } = render(
      <TotalAmountTransferredByCountrySection
        data={fakeChartTotalTransferredCashByCountry}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
