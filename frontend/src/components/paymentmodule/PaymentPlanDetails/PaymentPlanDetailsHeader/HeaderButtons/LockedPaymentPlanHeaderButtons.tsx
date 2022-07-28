import React, { useState } from 'react';
import styled from 'styled-components';
import { Box, Button } from '@material-ui/core';
import { EditRounded, Delete, FileCopy } from '@material-ui/icons';
import { useTranslation } from 'react-i18next';
import { PaymentPlanQuery } from '../../../../../__generated__/graphql';

const IconContainer = styled.span`
  button {
    color: #949494;
    min-width: 40px;
    svg {
      width: 20px;
      height: 20px;
    }
  }
`;

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

export interface LockedPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canDuplicate: boolean;
  canLock: boolean;
  canSendForApproval: boolean;
}

export const LockedPaymentPlanHeaderButtons = ({
  paymentPlan,
  canDuplicate,
  canLock,
  canSendForApproval,
}: LockedPaymentPlanHeaderButtonsProps): React.ReactElement => {
  const { t } = useTranslation();
  const [openApprove, setOpenApprove] = useState(false);
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  return (
    <Box display='flex' alignItems='center'>
      {canDuplicate && (
        <IconContainer>
          <Button onClick={() => setOpenDuplicate(true)}>
            <FileCopy />
          </Button>
        </IconContainer>
      )}
      {canLock && (
        <ButtonContainer>
          <Button
            variant='outlined'
            color='primary'
            onClick={() => setOpenApprove(true)}
          >
            {t('Unlock')}
          </Button>
        </ButtonContainer>
      )}
      {canSendForApproval && (
        <ButtonContainer>
          <Button
            variant='contained'
            color='primary'
            onClick={() => setOpenApprove(true)}
          >
            {t('Send For Approval')}
          </Button>
        </ButtonContainer>
      )}
    </Box>
  );
};
