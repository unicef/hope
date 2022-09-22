import { Grid, Typography } from '@material-ui/core';
import { Title } from '@material-ui/icons';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { GrievanceTicketQuery } from '../../../../__generated__/graphql';
import { ContainerColumnWithBorder } from '../../../core/ContainerColumnWithBorder';
import { LabelizedField } from '../../../core/LabelizedField';
import { Missing } from '../../../core/Missing';
import { OverviewContainer } from '../../../core/OverviewContainer';

interface LinkedGrievanceProps {
  ticket: GrievanceTicketQuery['grievanceTicket'];
}

export const LinkedGrievance = ({
  ticket,
}: LinkedGrievanceProps): React.ReactElement => {
  const { t } = useTranslation();

  return (
    <Grid item xs={4}>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant='h6'>{t('Linked Grievance')}</Typography>
        </Title>
        <OverviewContainer>
          <LabelizedField label={t('Ticket Id')}>
            <Missing />
          </LabelizedField>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </Grid>
  );
};
