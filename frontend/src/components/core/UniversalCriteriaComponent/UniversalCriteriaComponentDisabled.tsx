import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { AddCircleOutline } from '@material-ui/icons';

const IconWrapper = styled.div`
  display: flex;
  color: #a0b6d6;
`;

const AddCriteria = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  color: #003c8f;
  border: 2px solid #a0b6d6;
  border-radius: 3px;
  font-size: 16px;
  padding: ${({ theme }) => theme.spacing(6)}px
    ${({ theme }) => theme.spacing(28)}px;
  cursor: pointer;
  p {
    font-weight: 500;
    margin: 0 0 0 ${({ theme }) => theme.spacing(2)}px;
  }
`;

export function UniversalCriteriaComponentDisabled(): React.ReactElement {
  const { t } = useTranslation();
  return (
    <AddCriteria
      onClick={() => null}
      data-cy='button-target-population-disabled-add-criteria'
    >
      <IconWrapper>
        <AddCircleOutline />
        <p>{t('Add Filter')}</p>
      </IconWrapper>
    </AddCriteria>
  );
}
