import { Bold } from '@components/core/Bold';
import { Dialog } from '@containers/dialogs/Dialog';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { BlackLink } from '@core/BlackLink';
import { ContentLink } from '@core/ContentLink';
import { LabelizedField } from '@core/LabelizedField';
import { StatusBox } from '@core/StatusBox';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import {
  Box,
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { HouseholdSimple } from '@restgenerated/models/HouseholdSimple';
import { PaginatedGrievanceTicketListList } from '@restgenerated/models/PaginatedGrievanceTicketListList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { choicesToDict, grievanceTicketStatusToColor } from '@utils/utils';
import { createApiParams } from '@utils/apiUtils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { getGrievanceDetailsPath } from '../../grievances/utils/createGrievanceUtils';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;
const StyledTable = styled(Table)`
  min-width: 100px;
`;
const StyledDialog = styled(Dialog)`
  max-height: 800px;
`;

interface LinkedGrievancesModalProps {
  household: HouseholdDetail | HouseholdSimple;
  businessArea: string;
  baseUrl: string;
  grievancesChoices: GrievanceChoices;
}

export function LinkedGrievancesModal({
  household,
  businessArea,
  baseUrl,
  grievancesChoices,
}: LinkedGrievancesModalProps): ReactElement {
  const [dialogOpen, setDialogOpen] = useState(false);
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const { data: grievances } = useQuery<PaginatedGrievanceTicketListList>({
    queryKey: [
      'linkedGrievanceTickets',
      businessArea,
      selectedProgram?.id,
      household.unicefId,
    ],
    queryFn: () => {
      const queryParams = {
        household: household.unicefId,
        limit: 1000, // Get all tickets for this household
      };

      if (selectedProgram?.id && selectedProgram.id !== 'all') {
        return RestService.restBusinessAreasProgramsGrievanceTicketsList(
          createApiParams(
            {
              businessAreaSlug: businessArea,
              programSlug: selectedProgram.slug,
            },
            queryParams,
            { withPagination: true },
          ),
        );
      }
    },
    refetchOnWindowFocus: false,
  });

  const statusChoices: {
    [id: number]: string;
  } = choicesToDict(grievancesChoices.grievanceTicketStatusChoices);

  const categoryChoices: {
    [id: number]: string;
  } = choicesToDict(grievancesChoices.grievanceTicketCategoryChoices);

  const renderRow = (row): ReactElement => {
    const grievanceDetailsPath = getGrievanceDetailsPath(
      row.id,
      row.category,
      baseUrl,
    );
    return (
      <ClickableTableRow
        hover
        onClick={() => navigate(grievanceDetailsPath)}
        key={row.id}
      >
        <TableCell align="left">
          <BlackLink to={grievanceDetailsPath}>{row.unicefId}</BlackLink>
        </TableCell>
        <TableCell align="left">{categoryChoices[row.category]}</TableCell>
        <TableCell align="left">
          <StatusBox
            status={statusChoices[row.status]}
            statusToColor={grievanceTicketStatusToColor}
          />
        </TableCell>
      </ClickableTableRow>
    );
  };

  const allGrievances = grievances ? grievances.results : [];

  const renderGrievances = (): Array<ReactElement> =>
    allGrievances.length
      ? allGrievances.map((el) => {
          const grievanceDetailsPath = getGrievanceDetailsPath(
            el.id,
            el.category,
            baseUrl,
          );
          return (
            <span key={el.id}>
              <ContentLink href={grievanceDetailsPath}>
                {`${el.unicefId} - ${
                  categoryChoices[el.category]
                } - ${statusChoices[el.status]}`}
              </ContentLink>{' '}
              <br />
            </span>
          );
        })
      : [<span key="empty">-</span>];

  const renderLink = (): ReactElement => {
    if (allGrievances.length === 0) {
      return (
        <LabelizedField label={t('Linked Grievances')} value={<span>-</span>} />
      );
    }
    return (
      <>
        <LabelizedField
          label={t('Linked Grievances')}
          value={renderGrievances().slice(0, 3)}
        />
        {allGrievances.length > 3 && (
          <StyledLink
            onClick={(e) => {
              e.stopPropagation();
              setDialogOpen(true);
            }}
          >
            See More
          </StyledLink>
        )}
      </>
    );
  };

  const renderRows = (): ReactElement => (
    <>{allGrievances.map((relatedTicket) => renderRow(relatedTicket))}</>
  );

  return (
    <>
      {renderLink()}
      <StyledDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
        maxWidth="lg"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Linked Grievances')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <Box mt={2} mb={6}>
            <Typography>
              <Bold>
                {beneficiaryGroup?.groupLabel} ID {household.unicefId}
              </Bold>
              is linked to following Grievances.
            </Typography>
          </Box>
          <StyledTable>
            <TableHead>
              <TableRow>
                <TableCell align="left">{t('Ticket Id')}</TableCell>
                <TableCell align="left">{t('Category')}</TableCell>
                <TableCell align="left">{t('Status')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>{renderRows()}</TableBody>
          </StyledTable>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button
              onClick={(e) => {
                e.stopPropagation();
                setDialogOpen(false);
              }}
            >
              {t('CANCEL')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </StyledDialog>
    </>
  );
}
