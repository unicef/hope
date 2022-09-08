import { Box, Grid, GridSize, Paper, Typography } from '@material-ui/core';
import WarningIcon from '@material-ui/icons/Warning';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { decodeIdString } from '../../utils/utils';
import { useExistingGrievanceTicketsQuery } from '../../__generated__/graphql';
import { ContentLink } from '../core/ContentLink';
import { LoadingComponent } from '../core/LoadingComponent';

const StyledBox = styled(Paper)`
  border: 1px solid ${({ theme }) => theme.hctPalette.oragne};
  border-radius: 3px;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;
const OrangeTitle = styled.div`
  color: ${({ theme }) => theme.hctPalette.oragne};
`;

const WarnIcon = styled(WarningIcon)`
  position: relative;
  top: 5px;
  margin-right: 10px;
`;

export function TicketsAlreadyExist({ values, size = 6 }): React.ReactElement {
  const businessArea = useBusinessArea();
  const { t } = useTranslation();
  const { data, loading } = useExistingGrievanceTicketsQuery({
    variables: {
      businessArea,
      category: values.category,
      issueType: values.issueType,
      household: decodeIdString(values.selectedHousehold?.id),
      individual: decodeIdString(values.selectedIndividual?.id),
      paymentRecord: values.selectedPaymentRecords,
    },
  });
  if (loading) return <LoadingComponent />;
  if (!data) return null;
  const { edges } = data.existingGrievanceTickets;
  const mappedTickets = edges?.map((edge) => (
    <Box key={edge.node.id} mb={1}>
      <ContentLink
        href={`/${businessArea}/grievance-and-feedback/${edge.node.id}`}
      >
        {edge.node.unicefId}
      </ContentLink>
    </Box>
  ));
  return edges.length ? (
    <Grid item xs={size as GridSize}>
      <StyledBox>
        <OrangeTitle>
          <Typography variant='h6'>
            <WarnIcon />
            {edges.length === 1
              ? t('Ticket already exists')
              : t('Tickets already exist')}
          </Typography>
        </OrangeTitle>
        <Typography variant='body2'>
          {t(
            'There is an open ticket(s) in the same category for the related entity. Please review them before proceeding.',
          )}
        </Typography>
        <Box mt={3} display='flex' flexDirection='column'>
          {mappedTickets}
        </Box>
      </StyledBox>
    </Grid>
  ) : null;
}
