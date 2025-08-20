import { BaseSection } from '@components/core/BaseSection';
import { LabelizedField } from '@components/core/LabelizedField';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { StatusBox } from '@components/core/StatusBox';
import { periodicDataUpdatesOnlineEditsStatusToColor } from '@utils/utils';
import {
  Table,
  TableRow,
  TableCell,
  TableHead,
  TableBody,
} from '@mui/material';
import { BlackLink } from '@components/core/BlackLink';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useParams } from 'react-router-dom';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

const PeriodicDataUpdatesOnlineEditsTemplateDetailsPage = (): ReactElement => {
  const { businessArea, programId, baseUrl } = useBaseUrl();
  const { id } = useParams();

  const numericId = id ? parseInt(id, 10) : undefined;
  const { data, isLoading } = useQuery({
    queryKey: [
      'onlineEditsTemplateDetails',
      businessArea,
      programId,
      numericId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsRetrieve(
        {
          businessAreaSlug: businessArea,
          programSlug: programId,
          id: numericId,
        },
      ),
    enabled: !!businessArea && !!programId && !!numericId,
  });

  if (isLoading) return <LoadingComponent />;
  if (!data) return null;

  const {
    status,
    name,
    createdAt,
    numberOfRecords,
    authorizedUsers,
    approvedBy,
    approvedAt,
    createdBy,
  } = data;

  // Removed duplicate useBaseUrl call; baseUrl is already available from the top-level hook

  // Table head cells
  const individualHeadCells = [
    { id: 'individualId', label: 'Individual ID' },
    { id: 'firstName', label: 'First Name' },
    { id: 'lastName', label: 'Last Name' },
    { id: 'columnName', label: 'Column Name' },
  ];

  // Extract individuals data from editData (if available)
  const individuals = Array.isArray(data?.editData) ? data.editData : [];

  return (
    <>
      <PageHeader title={`Online Edits Template Details: ${name}`} />
      <BaseSection
        title="Details"
        description="Details of the selected online edits template."
      >
        <LabelizedField label="Status">
          <StatusBox
            status={status}
            statusToColor={periodicDataUpdatesOnlineEditsStatusToColor}
          />
        </LabelizedField>
        <LabelizedField label="Template Name" value={name} />
        <LabelizedField label="Creation Date">
          <UniversalMoment>{createdAt}</UniversalMoment>
        </LabelizedField>
        <LabelizedField label="Number of Records" value={numberOfRecords} />
        <LabelizedField label="Created By" value={createdBy} />
        <LabelizedField
          label="Authorized Users"
          value={
            authorizedUsers && authorizedUsers.length > 0
              ? authorizedUsers.map((u) => u.username).join(', ')
              : '-'
          }
        />
        <LabelizedField label="Approval Date">
          {approvedAt ? <UniversalMoment>{approvedAt}</UniversalMoment> : '-'}
        </LabelizedField>
        <LabelizedField label="Approved By" value={approvedBy || '-'} />
      </BaseSection>

      {/* Periodic Data Update Table */}
      <BaseSection title="Periodic Data Update">
        <Table>
          <TableHead>
            <TableRow>
              {individualHeadCells.map((cell) => (
                <TableCell key={cell.id}>{cell.label}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {individuals.length === 0 ? (
              <TableRow>
                <TableCell colSpan={individualHeadCells.length} align="center">
                  No data available
                </TableCell>
              </TableRow>
            ) : (
              individuals.map((row, idx) => (
                <TableRow key={row.individualId || idx}>
                  <TableCell>
                    {row.individualId ? (
                      <BlackLink
                        to={`/${baseUrl}/population/individuals/${row.individualId}`}
                      >
                        {row.individualId}
                      </BlackLink>
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell>{row.firstName || '-'}</TableCell>
                  <TableCell>{row.lastName || '-'}</TableCell>
                  <TableCell>{row.columnName || '-'}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </BaseSection>
    </>
  );
};

export default withErrorBoundary(
  PeriodicDataUpdatesOnlineEditsTemplateDetailsPage,
  'PeriodicDataUpdatesOnlineEditsTemplateDetailsPage',
);
