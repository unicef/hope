import React from 'react';
import { ThemeProvider } from '@material-ui/core';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { theme } from '../../theme';
import { StatusBox } from './StatusBox';
import styled from 'styled-components';
import {
  programStatusToColor,
  cashPlanStatusToColor,
  paymentRecordStatusToColor,
} from '../../utils/utils';

export default {
  component: StatusBox,
  title: 'StatusBox',
};

const statuses = {
  programStatus: [
    { status: 'ACTIVE', function: programStatusToColor },
    { status: 'FINISHED', function: programStatusToColor },
    { status: 'DEFAULT', function: programStatusToColor },
  ],
  cashPlanStatus: [
    { status: 'STARTED', function: cashPlanStatusToColor },
    { status: 'COMPLETE', function: cashPlanStatusToColor },
    { status: 'DEFAULT', function: cashPlanStatusToColor },
  ],
  paymentRecordStatus: [
    { status: 'SUCCESS', function: paymentRecordStatusToColor },
    { status: 'PENDING', function: paymentRecordStatusToColor },
    { status: 'ERROR', function: paymentRecordStatusToColor },
  ],
};

const StatusWrapper = styled.div`
  width: 100px;
  margin: 2rem;
`;

export const ProgramStatuses = () => {
  return (
    <ThemeProvider theme={theme}>
      <StyledThemeProvider theme={theme}>
        {statuses.programStatus.map((each) => (
          <StatusWrapper>
            <StatusBox status={each.status} statusToColor={each.function} />
          </StatusWrapper>
        ))}
      </StyledThemeProvider>
    </ThemeProvider>
  );
};

export const CashPlanStatuses = () => {
  return (
    <ThemeProvider theme={theme}>
      <StyledThemeProvider theme={theme}>
        {statuses.cashPlanStatus.map((each) => (
          <StatusWrapper>
            <StatusBox status={each.status} statusToColor={each.function} />
          </StatusWrapper>
        ))}
      </StyledThemeProvider>
    </ThemeProvider>
  );
};

export const PaymentRecordStatuses = () => {
  return (
    <ThemeProvider theme={theme}>
      <StyledThemeProvider theme={theme}>
        {statuses.paymentRecordStatus.map((each) => (
          <StatusWrapper>
            <StatusBox status={each.status} statusToColor={each.function} />
          </StatusWrapper>
        ))}
      </StyledThemeProvider>
    </ThemeProvider>
  );
};
