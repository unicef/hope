import withErrorBoundary from '@components/core/withErrorBoundary';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { Box, Grid, Paper, Typography } from '@mui/material';
import { MessageDetail } from '@restgenerated/models/MessageDetail';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

interface CommunicationMessageDetailsProps {
  message: MessageDetail;
}

const CommunicationMessageDetails = ({
  message,
}: CommunicationMessageDetailsProps): ReactElement => {
  const { t } = useTranslation();
  return (
    <Grid size={{ xs: 8 }} data-cy="communication-message-details">
      <Box p={5}>
        <StyledBox>
          <Title>
            <Typography variant="h6" data-cy="message-title">
              {t('Message')}
            </Typography>
          </Title>
          <OverviewContainer>
            <Grid container spacing={6}>
              <Grid container justifyContent="space-between" size={{ xs: 12 }}>
                <Box ml={2}>
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
              <Box ml={6} p={3}>
                <Box data-cy="message-title-content">{message.title}</Box>
                <Box data-cy="message-body-content">{message.body}</Box>
              </Box>
            </Grid>
          </OverviewContainer>
        </StyledBox>
      </Box>
    </Grid>
  );
};

export default withErrorBoundary(
  CommunicationMessageDetails,
  'CommunicationMessageDetails',
);
