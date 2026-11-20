import { Box } from '@mui/material';
import { DeletePaymentList } from '../DeletePaymentList';
import { LockPaymentList } from '../LockPaymentList';
import type { ReactElement } from 'react';
import type { PaymentListDetail } from '@restgenerated/models/PaymentListDetail';
import { HeaderActions } from '@core/HeaderActions';

export interface OpenPaymentListHeaderButtonsProps {
  paymentList: PaymentListDetail;
  canRemove: boolean;
  canLock: boolean;
}

export function OpenPaymentListHeaderButtons({
  paymentList,
  canRemove,
  canLock,
}: OpenPaymentListHeaderButtonsProps): ReactElement {
  return (
    <HeaderActions spacing="none">
      {canRemove && <DeletePaymentList paymentList={paymentList} />}
      {canLock && (
        <Box
          sx={{
            m: 2,
          }}
        >
          <LockPaymentList paymentList={paymentList} />
        </Box>
      )}
    </HeaderActions>
  );
}
