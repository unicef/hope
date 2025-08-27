import { periodicDataUpdatesOnlineEditsStatusToColor } from 'src/utils/utils';
import { StatusBox } from '@components/core/StatusBox';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { TableCell, Button } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { UniversalRestTable } from '@components/rest/UniversalRestTable/UniversalRestTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { PaginatedPDUOnlineEditListList } from '@restgenerated/models/PaginatedPDUOnlineEditListList';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';

const onlineEditsHeadCells: HeadCell<any>[] = [
  {
    id: 'id',
    numeric: false,
    disablePadding: false,
    label: 'ID',
    dataCy: 'head-cell-id',
  },
  {
    id: 'name',
    numeric: false,
    disablePadding: false,
    label: 'Name',
    dataCy: 'head-cell-name',
  },
  {
    id: 'numberOfRecords',
    numeric: true,
    disablePadding: false,
    label: 'Number of Records',
    dataCy: 'head-cell-number-of-records',
  },
  {
    id: 'createdAt',
    numeric: false,
    disablePadding: false,
    label: 'Creation Date',
    dataCy: 'head-cell-creation-date',
  },
  {
    id: 'createdBy',
    numeric: false,
    disablePadding: false,
    label: 'Created by',
    dataCy: 'head-cell-created-by',
  },
  {
    id: 'status',
    numeric: false,
    disablePadding: false,
    label: 'Status',
    dataCy: 'head-cell-status',
  },
  {
    id: 'empty',
    numeric: false,
    disablePadding: false,
    label: '',
    dataCy: 'head-cell-empty',
  },
];

const NewPeriodicDataUpdates = (): ReactElement => {
  const { baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  const { businessArea: businessAreaSlug, programId } = useBaseUrl();
  const { isSocialDctType } = useProgramContext();

  const newTemplatePath = isSocialDctType
    ? `/${baseUrl}/population/people/new-online-template`
    : `/${baseUrl}/population/individuals/new-online-template`;
  const initialQueryVariables = useMemo(
    () => ({
      businessAreaSlug,
      programSlug: programId,
      ordering: '-created_at',
      status: ['NEW' as const],
    }),
    [businessAreaSlug, programId],
  );

  const [queryVariables, setQueryVariables] = useState(initialQueryVariables);
  useEffect(() => {
    setQueryVariables(initialQueryVariables);
  }, [initialQueryVariables]);

  const { data, isLoading, error } = useQuery<PaginatedPDUOnlineEditListList>({
    queryKey: [
      'periodicDataUpdateOnlineEdits',
      queryVariables,
      businessAreaSlug,
      programId,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsList({
        businessAreaSlug,
        programSlug: programId,
        ordering: queryVariables.ordering,
        status: queryVariables.status,
      }),
    enabled: !!queryVariables.businessAreaSlug && !!queryVariables.programSlug,
  });

  const navigate = useNavigate();
  const renderRow = (row: any): ReactElement => {
    const url = `/${baseUrl}/population/individuals/online-templates/${row.id}`;
    return (
      <ClickableTableRow
        key={row.id}
        data-cy={`online-edit-row-${row.id}`}
        onClick={() => navigate(url)}
        style={{ cursor: 'pointer' }}
      >
        <TableCell>{row.id}</TableCell>
        <TableCell>{row.name}</TableCell>
        <TableCell align="right">{row.numberOfRecords}</TableCell>
        <TableCell>
          <UniversalMoment>{row.createdAt}</UniversalMoment>
        </TableCell>
        <TableCell>{row.createdBy}</TableCell>
        <TableCell>
          <StatusBox
            status={row.status}
            statusToColor={periodicDataUpdatesOnlineEditsStatusToColor}
          />
        </TableCell>
        <TableCell />
      </ClickableTableRow>
    );
  };

  return (
    <UniversalRestTable
      isOnPaper={true}
      renderRow={renderRow}
      headCells={onlineEditsHeadCells}
      data={data ?? []}
      isLoading={isLoading}
      error={error}
      queryVariables={queryVariables}
      setQueryVariables={setQueryVariables}
      title="New Periodic Data Updates"
      hidePagination={true}
      actions={[
        <Button
          key="add-new-online-edit"
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          component={Link}
          to={newTemplatePath}
        >
          {t('New Online Edit')}
        </Button>,
      ]}
    />
  );
};

export default NewPeriodicDataUpdates;
