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
import { PaginatedIndividualListList } from '@restgenerated/models/PaginatedIndividualListList';

interface INDDataTableProps {
  indData: PaginatedIndividualListList;
}

const INDDataTable: React.FC<INDDataTableProps> = ({ indData }) => {
  const { baseUrl, businessArea } = useBaseUrl();
  const { t } = useTranslation();
  return (
    <TableContainer component={Paper} sx={{ mt: 2 }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>{t('Individual ID')}</TableCell>
            <TableCell>{t('Household ID')}</TableCell>
            <TableCell>{t('Programme Name')}</TableCell>
            <TableCell>{t('Full Name')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {indData.results && indData.results.length > 0 ? (
            indData.results.map((individual: any) => {
              const individualDetailsPath = `/${businessArea}/programs/${individual.program.slug}/population/individuals/${individual.id}`;
              const householdDetailsPath = `/${businessArea}/programs/${individual.program.slug}/population/household/${individual.household.id}`;
              const programDetailsPath = `/${baseUrl}/details/${individual?.program?.slug}`;
              return (
                <TableRow key={individual.id} hover>
                  <TableCell>
                    <BlackLink to={individualDetailsPath}>
                      {individual.unicefId}
                    </BlackLink>
                  </TableCell>
                  <TableCell>
                    <BlackLink to={householdDetailsPath}>
                      {individual?.household?.unicefId}
                    </BlackLink>
                  </TableCell>
                  <TableCell>
                    <BlackLink to={programDetailsPath}>
                      {individual?.program?.name}
                    </BlackLink>
                  </TableCell>
                  <TableCell>{individual.fullName}</TableCell>
                </TableRow>
              );
            })
          ) : (
            <TableRow>
              <TableCell colSpan={2}>{t('No results found')}</TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default INDDataTable;
