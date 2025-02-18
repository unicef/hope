import { Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaperContainer } from '../PaperContainer';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

const Label = styled.p`
  color: #b1b1b5;
`;

function EmptyTargetingCriteria(): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  return (
    <PaperContainer>
      <Typography variant="h6">
        {t(`Target Population Entries (${beneficiaryGroup?.groupLabelPlural})`)}
      </Typography>
      <Label>{t('Add targeting criteria to see results.')}</Label>
    </PaperContainer>
  );
}

export default withErrorBoundary(
  EmptyTargetingCriteria,
  'EmptyTargetingCriteria',
);
