import withErrorBoundary from '@components/core/withErrorBoundary';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { Box, Grid, Paper, Typography } from '@mui/material';
import type { MessageDetail } from '@restgenerated/models/MessageDetail';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { responsiveGridSize, responsiveValue } from 'src/responsive';

interface CommunicationMessageDetailsProps {
  message: MessageDetail;
}

const CommunicationMessageDetails = ({
  message,
}: CommunicationMessageDetailsProps): ReactElement => {
  const { t } = useTranslation();
  return (
    <Grid
      size={responsiveGridSize('twoThirds')}
      data-cy="communication-message-details"
    >
      <Box
        sx={{
          p: responsiveValue(2, 5),
        }}
      >
        <Paper
          sx={{
            display: 'flex',
            flexDirection: 'column',
            width: '100%',
            padding: responsiveValue('16px', '26px 22px'),
          }}
        >
          <Title>
            <Typography variant="h6" data-cy="message-title">
              {t('Message')}
            </Typography>
          </Title>
          <OverviewContainer>
            <Grid container spacing={6}>
              <Grid
                container
                size={{ xs: 12 }}
                sx={{
                  justifyContent: 'space-between',
                }}
              >
                <Box
                  sx={{
                    ml: 2,
                  }}
                >
                  <Typography variant="subtitle2" data-cy="message-created-by">
                    {message.createdBy}
                  </Typography>
                </Box>
                <Typography color="textSecondary" data-cy="message-created-at">
                  <UniversalMoment withTime>
                    {message.createdAt}
                  </UniversalMoment>
                </Typography>
              </Grid>
              <Box
                sx={{
                  ml: responsiveValue(0, 6),
                  p: 3,
                }}
              >
                <Box data-cy="message-title-content">{message.title}</Box>
                <Box data-cy="message-body-content">{message.body}</Box>
              </Box>
            </Grid>
          </OverviewContainer>
        </Paper>
      </Box>
    </Grid>
  );
};

export default withErrorBoundary(
  CommunicationMessageDetails,
  'CommunicationMessageDetails',
);
