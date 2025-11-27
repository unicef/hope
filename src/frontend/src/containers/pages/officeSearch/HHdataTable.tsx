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
import { PaginatedHouseholdListList } from '@restgenerated/models/PaginatedHouseholdListList';

interface HHDataTableProps {
  hhData: PaginatedHouseholdListList;
}

const HHDataTable: React.FC<HHDataTableProps> = ({ hhData }) => {
  const { businessArea, baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  return (
    <TableContainer component={Paper} sx={{ mt: 2 }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>{t('Household ID')}</TableCell>
            <TableCell>{t('Programme Name')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {hhData.results && hhData.results.length > 0 ? (
            hhData.results.map((household: any) => {
              const householdDetailsPath = `/${businessArea}/programs/${household.programSlug}/population/household/${household.id}`;
              const programDetailsPath = `/${baseUrl}/details/${household.programSlug}`;
              return (
                <TableRow key={household.id} hover>
                  <TableCell>
                    <BlackLink to={householdDetailsPath}>
                      {household.unicefId}
                    </BlackLink>
                  </TableCell>
                  <TableCell>
                    <BlackLink to={programDetailsPath}>
                      {household.programName}
                    </BlackLink>
                  </TableCell>
                </TableRow>
              );
            })
          ) : (
            <TableRow>
              <TableCell colSpan={1}>{t('No results found')}</TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default HHDataTable;
