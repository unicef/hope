import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { useTranslation } from 'react-i18next';
import { BlackLink } from '@core/BlackLink';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { getGrievanceDetailsPath } from '../../../grievances/utils/createGrievanceUtils';
import { useBaseUrl } from '@hooks/useBaseUrl';
import type { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import type { FeedbackDetail } from '@restgenerated/models/FeedbackDetail';
import { ResponsiveGrid } from 'src/responsive';

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
    <ResponsiveGrid size="third">
      {feedback.linkedGrievanceId ? (
        <Box
          sx={{
            p: 3,
          }}
        >
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
    </ResponsiveGrid>
  );
}
export default withErrorBoundary(LinkedGrievance, 'LinkedGrievance');
