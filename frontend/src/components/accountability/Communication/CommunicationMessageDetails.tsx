import { Box, Grid, Paper, Typography } from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { renderUserName } from '../../../utils/utils';
import { AccountabilityCommunicationMessageQuery } from '../../../__generated__/graphql';
import { OverviewContainer } from '../../core/OverviewContainer';
import { Title } from '../../core/Title';
import { UniversalMoment } from '../../core/UniversalMoment';

const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

interface CommunicationMessageDetailsProps {
  message: AccountabilityCommunicationMessageQuery['accountabilityCommunicationMessage'];
}

export function CommunicationMessageDetails({
  message,
}: CommunicationMessageDetailsProps): React.ReactElement {
  const { t } = useTranslation();
  return (
    <Grid item xs={8}>
      <Box p={5}>
        <StyledBox>
          <Title>
            <Typography variant='h6'>{t('Message')}</Typography>
          </Title>
          <OverviewContainer>
            <Grid container spacing={6}>
              <Grid item container justify='space-between' xs={12}>
                <Typography variant='subtitle2'>
                  {renderUserName(message.createdBy)}
                </Typography>
                <Typography color='textSecondary'>
                  <UniversalMoment withTime>
                    {message.createdAt}
                  </UniversalMoment>
                </Typography>
              </Grid>
              <Box px={3}>
                <div>{message.title}</div>
                <Box py={3}>
                  <div>{message.body}</div>
                </Box>
              </Box>
            </Grid>
          </OverviewContainer>
        </StyledBox>
      </Box>
    </Grid>
  );
}
