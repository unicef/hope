import React from 'react';
import { Box, Grid } from '@material-ui/core';
import { FeedbackToHouseholdKind } from '../../../__generated__/graphql';
import { renderIndividualName, renderUserName } from '../../../utils/utils';
import { UniversalMoment } from '../../core/UniversalMoment';
import { Date, DescMargin, Name } from './styled';

export function Message({ message }): React.ReactElement {
  const renderName = (): string => {
    if (message.kind === FeedbackToHouseholdKind.Message) {
      return renderUserName(message.createdBy);
    }
    return renderIndividualName(message.individual);
  };

  return (
    <Grid container>
      <Grid item xs={12}>
        <Box display='flex' justifyContent='space-between'>
          <Name>{renderName()}</Name>
          <Date>
            <UniversalMoment withTime>{message.createdAt}</UniversalMoment>
          </Date>
        </Box>
        <Grid item xs={12}>
          <DescMargin>
            <p>{message.message}</p>
          </DescMargin>
        </Grid>
      </Grid>
    </Grid>
  );
}
