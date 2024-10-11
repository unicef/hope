import { Box, Grid, Typography } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { FeedbackQuery } from '@generated/graphql';
import { BlackLink } from '@core/BlackLink';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { getGrievanceDetailsPath } from '../../../grievances/utils/createGrievanceUtils';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface LinkedGrievanceProps {
  feedback: FeedbackQuery['feedback'];
}

export function LinkedGrievance({
  feedback,
}: LinkedGrievanceProps): React.ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const grievanceDetailsPath = getGrievanceDetailsPath(
    feedback.linkedGrievance?.id,
    feedback.linkedGrievance?.category,
    baseUrl,
  );
  return (
    <Grid item xs={4}>
      {feedback.linkedGrievance ? (
        <Box p={3}>
          <ContainerColumnWithBorder>
            <Title>
              <Typography variant="h6">{t('Linked Grievance')}</Typography>
            </Title>
            <OverviewContainer>
              <LabelizedField label={t('Ticket Id')}>
                <BlackLink to={grievanceDetailsPath}>
                  {feedback.linkedGrievance.unicefId}
                </BlackLink>
              </LabelizedField>
            </OverviewContainer>
          </ContainerColumnWithBorder>
        </Box>
      ) : null}
    </Grid>
  );
}
