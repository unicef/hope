import { Box, Grid2 as Grid, Paper, Typography } from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { decodeIdString } from '@utils/utils';
import { ContentLink } from '@core/ContentLink';
import { LoadingComponent } from '@core/LoadingComponent';
import { getGrievanceDetailsPath } from './utils/createGrievanceUtils';
import { ReactElement } from 'react';

const StyledBox = styled(Paper)`
  border: 1px solid ${({ theme }) => theme.hctPalette.orange};
  border-radius: 3px;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;
const OrangeTitle = styled.div`
  color: ${({ theme }) => theme.hctPalette.orange};
`;

const WarnIcon = styled(WarningIcon)`
  position: relative;
  top: 5px;
  margin-right: 10px;
`;

export function TicketsAlreadyExist({ values }): ReactElement {
  const { baseUrl, businessAreaSlug } = useBaseUrl();
  const { t } = useTranslation();

  const { data, isPending: loading } = useQuery({
    queryKey: [
      'existingGrievanceTickets',
      businessAreaSlug,
      values.category,
      values.issueType,
      values.selectedHousehold?.id,
      values.selectedIndividual?.id,
      values.selectedPaymentRecords,
    ],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsList({
        businessAreaSlug,
        category: values.category,
        issueType: values.issueType,
        household: decodeIdString(values.selectedHousehold?.id),
        //TODO: pass these when available
        //individual: decodeIdString(values.selectedIndividual?.id),
        // paymentRecord: values.selectedPaymentRecords,
      }),
    enabled: !!(businessAreaSlug && values.category),
  });

  if (loading) return <LoadingComponent />;
  if (!data) return null;

  const results = data.results || [];
  const mappedTickets = results?.map((ticket) => {
    const grievanceDetailsPath = getGrievanceDetailsPath(
      ticket.id,
      ticket.category,
      baseUrl,
    );
    return (
      <Box key={ticket.id} mb={1}>
        <ContentLink href={grievanceDetailsPath}>{ticket.unicefId}</ContentLink>
      </Box>
    );
  });
  const shouldShowBox =
    !!values.category &&
    (!!values.selectedHousehold?.id || !!values.selectedIndividual?.id);

  return results.length && shouldShowBox ? (
    <Grid size={{ xs: 6 }}>
      <StyledBox>
        <OrangeTitle>
          <Typography variant="h6">
            <WarnIcon />
            {results.length === 1
              ? t('Ticket already exists')
              : t('Tickets already exist')}
          </Typography>
        </OrangeTitle>
        <Typography variant="body2">
          {t(
            'There is an open ticket(s) in the same category for the related entity. Please review them before proceeding.',
          )}
        </Typography>
        <Box mt={3} display="flex" flexDirection="column">
          {mappedTickets}
        </Box>
      </StyledBox>
    </Grid>
  ) : null;
}
