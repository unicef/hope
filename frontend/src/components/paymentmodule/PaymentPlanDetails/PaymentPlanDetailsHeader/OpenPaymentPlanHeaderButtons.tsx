import React, { useState } from 'react';
import styled from 'styled-components';
import { Button } from '@material-ui/core';
import { EditRounded, Delete, FileCopy } from '@material-ui/icons';
import { useTranslation } from 'react-i18next';
import { LockPaymentPlan } from './LockPaymentPlan';

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
  setEditState: Function;
  canDuplicate: boolean;
  canRemove: boolean;
  canEdit: boolean;
  canLock: boolean;
}

export function OpenPaymentPlanHeaderButtons({
  setEditState,
  canDuplicate,
  canEdit,
  canLock,
  canRemove,
}: OpenPaymentPlanHeaderButtonsProps): React.ReactElement {
  const { t } = useTranslation();
  const [openLock, setOpenLock] = useState(false);
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  return (
    <div>
      {canDuplicate && (
        <IconContainer>
          <Button onClick={() => setOpenDuplicate(true)}>
            <FileCopy />
          </Button>
        </IconContainer>
      )}
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
    </div>
  );
}
