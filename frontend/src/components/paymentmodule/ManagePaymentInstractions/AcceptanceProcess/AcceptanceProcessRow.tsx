import { Box, Grid } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { renderUserName } from '../../../../utils/utils';
import { DividerLine } from '../../../core/DividerLine';
import { AcceptanceProcessStepper } from './AcceptanceProcessStepper';
import { GreyInfoCard } from './GreyInfoCard';

interface AcceptanceProcessRowProps {
  acceptanceProcess;
  showDivider?: boolean;
}

export const AcceptanceProcessRow = ({
  acceptanceProcess,
  showDivider = false,
}: AcceptanceProcessRowProps): React.ReactElement => {
  const { t } = useTranslation();
  const {
    actions,
    sentForAuthorizationDate,
    sentForAuthorizationBy,
    sentForReleaseDate,
    sentForReleaseBy,
    rejectedOn,
  } = acceptanceProcess;

  return (
    <Box>
      <AcceptanceProcessStepper acceptanceProcess={acceptanceProcess} />
      <Grid container>
        <Grid item xs={6}>
          {actions.authorization.length > 0 && (
            <GreyInfoCard
              topMessage={`Sent for authorization by ${renderUserName(
                sentForAuthorizationBy,
              )}`}
              topDate={sentForAuthorizationDate}
              approvals={actions.authorization}
            />
          )}
        </Grid>
        <Grid item xs={6}>
          {actions.release.length > 0 && (
            <GreyInfoCard
              topMessage={`Sent for review by ${renderUserName(
                sentForReleaseBy,
              )}`}
              topDate={sentForReleaseDate}
              approvals={actions.release}
            />
          )}
        </Grid>
        {actions.reject.length > 0 && (
          <Grid container>
            <Grid item xs={4}>
              {rejectedOn === 'IN_AUTHORIZATION' && (
                <GreyInfoCard
                  topMessage={t('Rejected in Authorization stage')}
                  topDate={actions.reject[0]?.createdAt}
                  approvals={actions.reject}
                />
              )}
            </Grid>
            <Grid item xs={4}>
              {rejectedOn === 'IN_REVIEW' && (
                <GreyInfoCard
                  topMessage={t('Rejected in Release stage')}
                  topDate={actions.reject[0]?.createdAt}
                  approvals={actions.reject}
                />
              )}
            </Grid>
          </Grid>
        )}
      </Grid>
      {showDivider && <DividerLine />}
    </Box>
  );
};
