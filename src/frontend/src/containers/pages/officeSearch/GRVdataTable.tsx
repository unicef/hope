import React from 'react';
import {
  TableContainer,
  Paper,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
} from '@mui/material';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useTranslation } from 'react-i18next';
import {
  GRIEVANCE_CATEGORIES_NAMES,
  GRIEVANCE_ISSUE_TYPES_NAMES,
  GRIEVANCE_TICKET_STATES_NAMES,
} from '@utils/constants';
import { getGrievanceDetailsPath } from '@components/grievances/utils/createGrievanceUtils';
import { PaginatedGrievanceTicketListList } from '@restgenerated/models/PaginatedGrievanceTicketListList';
import { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';

interface GRVDataTableProps {
  grvData: PaginatedGrievanceTicketListList;
}

const GRVDataTable: React.FC<GRVDataTableProps> = ({ grvData }) => {
  const { baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  return (
    <TableContainer component={Paper} sx={{ mt: 2 }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>{t('Ticket ID')}</TableCell>
            <TableCell>{t('Status')}</TableCell>
            <TableCell>{t('Category')}</TableCell>
            <TableCell>{t('Issue Type')}</TableCell>
            <TableCell>{t('Programme Name')}</TableCell>
            <TableCell>{t('Household ID')}</TableCell>
            <TableCell>{t('Individual ID')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {grvData.results && grvData.results.length > 0 ? (
            grvData.results.map((grv: GrievanceTicketList) => {
              const grvDetailsPath = getGrievanceDetailsPath(
                grv.id,
                grv.category,
                baseUrl,
              );
              const individualDetailsPath = `/${baseUrl}/population/individuals/${grv.individual.id}`;
              const householdDetailsPath = `/${baseUrl}/population/households/${grv.household.id}`;
              const programDetailsPath = `/${baseUrl}/programs/all/details/${grv.household.programSlug}`;
              return (
                <TableRow key={grv.id} hover>
                  <TableCell>
                    <BlackLink to={grvDetailsPath}>{grv.unicefId}</BlackLink>
                  </TableCell>
                  <TableCell>
                    {GRIEVANCE_TICKET_STATES_NAMES[grv.status]}
                  </TableCell>
                  <TableCell>
                    {GRIEVANCE_CATEGORIES_NAMES[grv.category]}
                  </TableCell>
                  <TableCell>
                    {GRIEVANCE_ISSUE_TYPES_NAMES[grv.issueType]}
                  </TableCell>
                  <TableCell>
                    <BlackLink to={programDetailsPath}>
                      {grv.programName}
                    </BlackLink>
                  </TableCell>
                  <TableCell>
                    <BlackLink to={householdDetailsPath}>
                      {grv.householdUnicefId}
                    </BlackLink>
                  </TableCell>
                  <TableCell>
                    <BlackLink to={individualDetailsPath}>
                      {grv.individualUnicefId}
                    </BlackLink>
                  </TableCell>
                </TableRow>
              );
            })
          ) : (
            <TableRow>
              <TableCell colSpan={4}>{t('No results found')}</TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default GRVDataTable;
