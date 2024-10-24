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
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { Dialog } from '@containers/dialogs/Dialog';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { grievanceTicketStatusToColor, choicesToDict } from '@utils/utils';
import {
  GrievancesChoiceDataQuery,
  HouseholdNode,
  useAllGrievanceTicketQuery,
} from '@generated/graphql';
import { BlackLink } from '@core/BlackLink';
import { ContentLink } from '@core/ContentLink';
import { LabelizedField } from '@core/LabelizedField';
import { StatusBox } from '@core/StatusBox';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import { getGrievanceDetailsPath } from '../../grievances/utils/createGrievanceUtils';
import { Bold } from '@components/core/Bold';

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
  household: HouseholdNode;
  businessArea: string;
  baseUrl: string;
  grievancesChoices: GrievancesChoiceDataQuery;
}

export function LinkedGrievancesModal({
  household,
  businessArea,
  baseUrl,
  grievancesChoices,
}: LinkedGrievancesModalProps): React.ReactElement {
  const [dialogOpen, setDialogOpen] = useState(false);
  const navigate = useNavigate();
  const { t } = useTranslation();

  const { data: grievances } = useAllGrievanceTicketQuery({
    variables: { businessArea, household: household.unicefId },
    notifyOnNetworkStatusChange: true,
    fetchPolicy: 'network-only',
  });

  const statusChoices: {
    [id: number]: string;
  } = choicesToDict(grievancesChoices.grievanceTicketStatusChoices);

  const categoryChoices: {
    [id: number]: string;
  } = choicesToDict(grievancesChoices.grievanceTicketCategoryChoices);

  const renderRow = (row): React.ReactElement => {
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

  const allGrievances = grievances ? grievances.allGrievanceTicket.edges : [];

  const renderGrievances = (): Array<React.ReactElement> =>
    allGrievances.length
      ? allGrievances.map((el) => {
          const grievanceDetailsPath = getGrievanceDetailsPath(
            el.node.id,
            el.node.category,
            baseUrl,
          );
          return (
            <span key={el.node.id}>
              <ContentLink href={grievanceDetailsPath}>
                {`${el.node.unicefId} - ${
                  categoryChoices[el.node.category]
                } - ${statusChoices[el.node.status]}`}
              </ContentLink>{' '}
              <br />
            </span>
          );
        })
      : [<span key="empty">-</span>];

  const renderLink = (): React.ReactElement => {
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

  const renderRows = (): React.ReactElement => (
    <>{allGrievances.map((relatedTicket) => renderRow(relatedTicket.node))}</>
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
                Household ID
                {household.unicefId}
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
