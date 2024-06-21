import { Box, Grid, Paper, Typography } from '@mui/material';
import * as React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { renderUserName } from '@utils/utils';
import { AccountabilityCommunicationMessageQuery } from '@generated/graphql';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';

const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

interface CommunicationMessageDetailsProps {
  message: AccountabilityCommunicationMessageQuery['accountabilityCommunicationMessage'];
}

export const CommunicationMessageDetails = ({
  message,
}: CommunicationMessageDetailsProps): React.ReactElement => {
  const { t } = useTranslation();
  return (
    <Grid item xs={8} data-cy="communication-message-details">
      <Box p={5}>
        <StyledBox>
          <Title>
            <Typography variant="h6" data-cy="message-title">
              {t('Message')}
            </Typography>
          </Title>
          <OverviewContainer>
            <Grid container spacing={6}>
              <Grid item container justifyContent="space-between" xs={12}>
                <Box ml={2}>
                  <Typography variant="subtitle2" data-cy="message-created-by">
                    {renderUserName(message.createdBy)}
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
