import React, { useState } from 'react';
import styled from 'styled-components';
import { Box, Button } from '@material-ui/core';
import { EditRounded, Delete, FileCopy } from '@material-ui/icons';
import { useTranslation } from 'react-i18next';
import { LockPaymentPlan } from '../LockPaymentPlan';
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

export interface OpenPaymentPlanHeaderButtonsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  setEditState: Function;
  canRemove: boolean;
  canEdit: boolean;
  canLock: boolean;
}

export const OpenPaymentPlanHeaderButtons = ({
  setEditState,
  canEdit,
  canLock,
  canRemove,
}: OpenPaymentPlanHeaderButtonsProps): React.ReactElement => {
  const { t } = useTranslation();
  const [openLock, setOpenLock] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  return (
    <Box display='flex' alignItems='center'>
      {canRemove && (
        <IconContainer>
          <Button onClick={() => setOpenDelete(true)}>
            <Delete />
          </Button>
        </IconContainer>
      )}
      {canEdit && (
        <ButtonContainer>
          <Button
            variant='outlined'
            color='primary'
            startIcon={<EditRounded />}
            onClick={() => setEditState(true)}
          >
            {t('Edit')}
          </Button>
        </ButtonContainer>
      )}
      {canLock && (
        <ButtonContainer>
          <LockPaymentPlan paymentPlanId='929292929' />
        </ButtonContainer>
      )}
    </Box>
  );
};
