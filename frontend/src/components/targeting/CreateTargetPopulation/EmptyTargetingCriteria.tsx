import { Typography } from '@mui/material';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaperContainer } from '../PaperContainer';

const Label = styled.p`
  color: #b1b1b5;
`;

export function EmptyTargetingCriteria(): React.ReactElement {
  const { t } = useTranslation();
  return (
    <PaperContainer>
      <Typography variant="h6">
        {t('Target Population Entries (Households)')}
      </Typography>
      <Label>{t('Add targeting criteria to see results.')}</Label>
    </PaperContainer>
  );
}
