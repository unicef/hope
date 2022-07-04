import { Box, Button, DialogActions, DialogContent, DialogTitle, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { Dialog } from '../../../containers/dialogs/Dialog';
import { DialogFooter } from '../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../containers/dialogs/DialogTitleWrapper';
import { grievanceTicketStatusToColor, reduceChoices } from '../../../utils/utils';
import {
  GrievancesChoiceDataQuery,
  HouseholdNode,
  useAllGrievanceTicketQuery,
} from '../../../__generated__/graphql';
import { BlackLink } from '../../core/BlackLink';
import { ContentLink } from '../../core/ContentLink';
import { LabelizedField } from '../../core/LabelizedField';
import { StatusBox } from '../../core/StatusBox';
import { ClickableTableRow } from '../../core/Table/ClickableTableRow';

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

const Bold = styled.span`
  font-weight: bold;
`;

interface LinkedGrievancesModalProps {
  household: HouseholdNode;
  businessArea: string;
  grievancesChoices: GrievancesChoiceDataQuery;
}

export const LinkedGrievancesModal = ({
  household,
  businessArea,
  grievancesChoices
}: LinkedGrievancesModalProps): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const history = useHistory();
  const { t } = useTranslation();

  const {
    data: grievances
  } = useAllGrievanceTicketQuery({
    variables: { businessArea, household: household.unicefId },
    notifyOnNetworkStatusChange: true,
    fetchPolicy: 'network-only',
  });

  const statusChoices: {
    [id: number]: string;
  } = reduceChoices(grievancesChoices.grievanceTicketStatusChoices);

  const categoryChoices: {
    [id: number]: string;
  } = reduceChoices(grievancesChoices.grievanceTicketCategoryChoices);

  const renderRow = (row): React.ReactElement => {

    return (
      <ClickableTableRow
        hover
        onClick={() =>
          history.push(
            `/${businessArea}/grievance-and-feedback/${row.id}`,
          )
        }
        key={row.id}
      >
        <TableCell align='left'>
          <BlackLink to={`/${businessArea}/grievance-and-feedback/${row.id}`}>
            {row.unicefId}
          </BlackLink>
        </TableCell>
        <TableCell align='left'>{categoryChoices[row.category]}</TableCell>
        <TableCell align='left'>
          <StatusBox
            status={statusChoices[row.status]}
            statusToColor={grievanceTicketStatusToColor}
          />
        </TableCell>
      </ClickableTableRow>
    );
  };

  const allGrievances = grievances ? grievances.allGrievanceTicket.edges : []

  const renderGrievances = ():
    Array<React.ReactElement> => {
    return allGrievances.length ? (
      allGrievances.map((el) => (
        <span key={el.node.id}>
          <ContentLink href={`/${businessArea}/grievance-and-feedback/${el.node.id}`}>
            {`${el.node.unicefId} - ${categoryChoices[el.node.category]} - ${statusChoices[el.node.status]}`}
          </ContentLink> <br />
        </span>
      ))
    ) : (
      [<span>-</span>]
    );
  };

  const renderLink = (): React.ReactElement => {
    if (allGrievances.length === 0) {
      return <LabelizedField label={t('Linked Grievances')} value={<span>-</span>} />;
    }
    return (
      <>
        <LabelizedField label={t('Linked Grievances')} value={renderGrievances().slice(0, 3)} />
        {allGrievances.length > 3 && <StyledLink
          onClick={(e) => {
            e.stopPropagation();
            setDialogOpen(true);
          }}
        >
          See More
        </StyledLink>}
      </>
    );
  };

  const renderRows = (): React.ReactElement => {

    return (
      <>
        {allGrievances.map((relatedTicket) => renderRow(relatedTicket.node))}
      </>
    );
  };

  return (
    <>
      {renderLink()}
      <StyledDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
        maxWidth='lg'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            {t('Linked Grievances')}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <Box mt={2} mb={6}>
            <Typography>
              <Bold>Household ID {household.unicefId} </Bold>
              is linked to following Grievances.
            </Typography>
          </Box>
          <StyledTable>
            <TableHead>
              <TableRow>
                <TableCell align='left'>{t('Ticket Id')}</TableCell>
                <TableCell align='left'>{t('Category')}</TableCell>
                <TableCell align='left'>{t('Status')}</TableCell>
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
};
