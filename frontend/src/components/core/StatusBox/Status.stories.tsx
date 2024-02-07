import * as React from 'react';
import { ThemeProvider } from '@mui/material';
import styled, {
  ThemeProvider as StyledThemeProvider,
} from 'styled-components';
import { theme } from '../../../theme';
import { StatusBox } from './StatusBox';
import {
  programStatusToColor,
  cashPlanStatusToColor,
  paymentRecordStatusToColor,
} from '@utils/utils';

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

export function ProgramStatuses() {
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
}

export function CashPlanStatuses() {
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
}

export function PaymentRecordStatuses() {
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
}
