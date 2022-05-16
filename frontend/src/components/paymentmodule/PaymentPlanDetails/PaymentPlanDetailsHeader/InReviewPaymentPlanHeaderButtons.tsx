import React, { useState } from 'react';
import styled from 'styled-components';
import { Button } from '@material-ui/core';
import { EditRounded, Delete, FileCopy } from '@material-ui/icons';
import { useTranslation } from 'react-i18next';
import { ErrorButton } from '../../../core/ErrorButton';

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

export interface InReviewPaymentPlanHeaderButtonsProps {
  setEditState: Function;
  canDuplicate: boolean;
  canRemove: boolean;
  canEdit: boolean;
  canLock: boolean;
}

export function InReviewPaymentPlanHeaderButtons({
  setEditState,
  canDuplicate,
  canEdit,
  canLock,
  canRemove,
}: InReviewPaymentPlanHeaderButtonsProps): React.ReactElement {
  const { t } = useTranslation();
  const [openApprove, setOpenApprove] = useState(false);
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openDelete, setOpenDelete] = useState(false);
  return (
    <div>
      {canLock && (
        <ButtonContainer>
          <ErrorButton onClick={() => setOpenApprove(true)}>
            {t('Reject')}
          </ErrorButton>
        </ButtonContainer>
      )}
      {canLock && (
        <ButtonContainer>
          <Button
            variant='contained'
            color='primary'
            onClick={() => setOpenApprove(true)}
          >
            {t('Mark as Reviewed')}
          </Button>
        </ButtonContainer>
      )}
    </div>
  );
}
