import { Box, Grid2 as Grid, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { BlackLink } from '@core/BlackLink';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { getGrievanceDetailsPath } from '../../../grievances/utils/createGrievanceUtils';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { FeedbackDetail } from '@restgenerated/models/FeedbackDetail';

interface LinkedGrievanceProps {
  feedback: FeedbackDetail;
}

function LinkedGrievance({ feedback }: LinkedGrievanceProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const grievanceDetailsPath = getGrievanceDetailsPath(
    feedback.linkedGrievanceId,
    Number(feedback.linkedGrievanceCategory),
    baseUrl,
  );
  return (
    <Grid size={{ xs: 4 }}>
      {feedback.linkedGrievanceId ? (
        <Box p={3}>
          <ContainerColumnWithBorder>
            <Title>
              <Typography variant="h6">{t('Linked Grievance')}</Typography>
            </Title>
            <OverviewContainer>
              <LabelizedField label={t('Ticket Id')}>
                <BlackLink to={grievanceDetailsPath}>
                  {feedback.linkedGrievanceUnicefId}
                </BlackLink>
              </LabelizedField>
            </OverviewContainer>
          </ContainerColumnWithBorder>
        </Box>
      ) : null}
    </Grid>
  );
}
export default withErrorBoundary(LinkedGrievance, 'LinkedGrievance');
