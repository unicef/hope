import { Box, Typography } from '@mui/material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { decodeIdString } from '@utils/utils';
import { ContentLink } from '@core/ContentLink';
import { LabelizedField } from '@core/LabelizedField';
import { LoadingComponent } from '@core/LoadingComponent';
import { Title } from '@core/Title';
import {
  ApproveBox,
  BlueBold,
} from './GrievancesApproveSection/ApproveSectionStyles';
import { getGrievanceDetailsPath } from './utils/createGrievanceUtils';
import { useProgramContext } from 'src/programContext';

export function OtherRelatedTicketsCreate({ values }): ReactElement {
  const { t } = useTranslation();
  const { baseUrl, businessAreaSlug } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const [show, setShow] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: [
      'grievanceTickets',
      businessAreaSlug,
      values?.selectedHousehold?.id,
    ],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsList({
        businessAreaSlug,
        household:
          decodeIdString(values?.selectedHousehold?.id) ||
          '294cfa7e-b16f-4331-8014-a22ffb2b8b3c',
      }),
    enabled: !!businessAreaSlug,
  });
  if (isLoading) return <LoadingComponent />;
  if (!data) return null;

  const existingTickets = data.results || [];
  const renderIds = (tickets): ReactElement =>
    tickets.length ? (
      tickets.map((el) => {
        const grievanceDetailsPath = getGrievanceDetailsPath(
          el.id,
          el.category,
          baseUrl,
        );
        return (
          <Box key={el.id} mb={1}>
            <ContentLink href={grievanceDetailsPath}>{el.unicefId}</ContentLink>
          </Box>
        );
      })
    ) : (
      <>-</>
    );

  const openExistingTickets = existingTickets.length
    ? existingTickets.filter(
        (el) => el.status !== GRIEVANCE_TICKET_STATES.CLOSED,
      )
    : [];
  const closedExistingTickets = existingTickets.length
    ? existingTickets.filter(
        (el) => el.status === GRIEVANCE_TICKET_STATES.CLOSED,
      )
    : [];

  return existingTickets.length ? (
    <ApproveBox>
      <Title>
        <Typography variant="h6">{t('Other Related Tickets')}</Typography>
      </Title>
      <Box display="flex" flexDirection="column">
        <LabelizedField
          label={`For ${beneficiaryGroup?.groupLabel} ${values?.selectedHousehold?.unicefId || '-'}`}
        >
          <>{renderIds(openExistingTickets)}</>
        </LabelizedField>
        {!show && closedExistingTickets.length ? (
          <Box mt={3}>
            <BlueBold onClick={() => setShow(true)}>
              {t('SHOW CLOSED TICKETS')} ({closedExistingTickets.length})
            </BlueBold>
          </Box>
        ) : null}
        {show && (
          <Box mb={3} mt={3}>
            <Typography>{t('Closed Tickets')}</Typography>
            <LabelizedField
              label={`For ${beneficiaryGroup?.groupLabel} ${values?.selectedHousehold?.unicefId || '-'}`}
            >
              <>{renderIds(closedExistingTickets)}</>
            </LabelizedField>
          </Box>
        )}
        {show && closedExistingTickets.length ? (
          <BlueBold onClick={() => setShow(false)}>
            {t('HIDE CLOSED TICKETS')} ({closedExistingTickets.length})
          </BlueBold>
        ) : null}
      </Box>
    </ApproveBox>
  ) : null;
}
