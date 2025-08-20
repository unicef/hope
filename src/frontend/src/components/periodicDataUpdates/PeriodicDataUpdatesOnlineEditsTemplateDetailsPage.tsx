import { BaseSection } from '@components/core/BaseSection';
import { LabelizedField } from '@components/core/LabelizedField';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { StatusBox } from '@components/core/StatusBox';
import { periodicDataUpdatesOnlineEditsStatusToColor } from '@utils/utils';
import {
  Table,
  Grid2 as Grid,
  TableRow,
  TableCell,
  TableHead,
  TableBody,
  TextField,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';

// StickyHeaderCell component for sticky table header cells
const StickyHeaderCell = ({ shouldScroll, children }) => (
  <TableCell
    style={
      shouldScroll
        ? {
            position: 'sticky',
            top: 0,
            background: '#fff',
            zIndex: 3,
          }
        : {}
    }
  >
    {children}
  </TableCell>
);
import { BlackLink } from '@components/core/BlackLink';
import React, { ReactElement, useMemo, useEffect, useState } from 'react';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useParams } from 'react-router-dom';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { useTranslation } from 'react-i18next';

const PeriodicDataUpdatesOnlineEditsTemplateDetailsPage = (): ReactElement => {
  const { businessArea, programId } = useBaseUrl();
  const { id } = useParams();
  const { t } = useTranslation();

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

  // All hooks must be called before any return
  const individuals = useMemo(() => {
    if (!data) return [];
    return Array.isArray(data.editData) ? data.editData : [];
  }, [data]);

  const allPduFields = useMemo(() => {
    const fields = [];
    individuals.forEach((ind) => {
      if (ind.pduFields) {
        ind.pduFields.forEach((field) => {
          const key = `${field.subtype}|${field.roundNumber}|${field.roundName}|${field.columnName || field.subtype}`;
          if (!fields.some((f) => f.key === key)) {
            fields.push({
              key,
              subtype: field.subtype,
              roundNumber: field.roundNumber,
              roundName: field.roundName,
              columnName: field.columnName || field.subtype,
            });
          }
        });
      }
    });
    return fields;
  }, [individuals]);

  const [editRows, setEditRows] = useState(() => {
    return individuals.map((ind) => ({
      ...ind,
      pduFields: ind.pduFields ? ind.pduFields.map((f) => ({ ...f })) : [],
    }));
  });

  useEffect(() => {
    setEditRows(
      individuals.map((ind) => ({
        ...ind,
        pduFields: ind.pduFields ? ind.pduFields.map((f) => ({ ...f })) : [],
      })),
    );
  }, [individuals]);

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
  return (
    <>
      <PageHeader title={`Online Edits Template Details: ${name}`} />
      <BaseSection title="Details">
        <Grid container spacing={2}>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Status')}>
              <StatusBox
                status={status}
                statusToColor={periodicDataUpdatesOnlineEditsStatusToColor}
              />
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Template Name')} value={name} />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Creation Date')}>
              <UniversalMoment>{createdAt}</UniversalMoment>
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('Number of Records')}
              value={numberOfRecords}
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Created By')} value={createdBy} />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('Authorized Users')}
              value={
                authorizedUsers && authorizedUsers.length > 0
                  ? authorizedUsers.map((u) => u.username).join(', ')
                  : t('-')
              }
            />
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Approval Date')}>
              {approvedAt ? (
                <UniversalMoment>{approvedAt}</UniversalMoment>
              ) : (
                t('-')
              )}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField
              label={t('Approved By')}
              value={approvedBy || t('-')}
            />
          </Grid>
        </Grid>
      </BaseSection>

      {/* Periodic Data Update Table */}
      <BaseSection title="Periodic Data Update">
        {(() => {
          const shouldScroll = editRows.length > 10 || allPduFields.length > 6;
          const TableContent = (
            <Table>
              <TableHead>
                <TableRow
                  style={
                    shouldScroll
                      ? {
                          position: 'sticky',
                          top: 0,
                          zIndex: 2,
                          background: '#fff',
                        }
                      : {}
                  }
                >
                  <StickyHeaderCell shouldScroll={shouldScroll}>
                    {t('Individual ID')}
                  </StickyHeaderCell>
                  <StickyHeaderCell shouldScroll={shouldScroll}>
                    {t('First Name')}
                  </StickyHeaderCell>
                  <StickyHeaderCell shouldScroll={shouldScroll}>
                    {t('Last Name')}
                  </StickyHeaderCell>
                  {allPduFields.map((field) => (
                    <StickyHeaderCell
                      shouldScroll={shouldScroll}
                      key={field.key}
                    >
                      <div
                        style={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          minWidth: 120,
                        }}
                      >
                        <span style={{ fontWeight: 600 }}>
                          {field.columnName}
                        </span>
                        <span>
                          {t('Round')} {field.roundNumber} ({field.roundName})
                        </span>
                        <span style={{ fontSize: 12, color: '#888' }}>
                          {field.subtype}
                        </span>
                      </div>
                    </StickyHeaderCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {editRows.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={3 + allPduFields.length} align="center">
                      {t('No data available')}
                    </TableCell>
                  </TableRow>
                ) : (
                  editRows.map((individual, idx) => (
                    <TableRow key={individual.individualUuid || idx}>
                      <TableCell>
                        {individual.individualUuid ? (
                          <BlackLink
                            to={`/population/individuals/${individual.individualUuid}`}
                          >
                            {individual.individualUuid}
                          </BlackLink>
                        ) : (
                          t('-')
                        )}
                      </TableCell>
                      <TableCell>{individual.firstName}</TableCell>
                      <TableCell>{individual.lastName}</TableCell>
                      {allPduFields.map((col) => {
                        // Find the matching pduField for this column
                        const fieldIdx = individual.pduFields
                          ? individual.pduFields.findIndex(
                              (f) =>
                                `${f.subtype}|${f.roundNumber}|${f.roundName}|${f.columnName || f.subtype}` ===
                                col.key,
                            )
                          : -1;
                        const field =
                          fieldIdx !== -1
                            ? individual.pduFields[fieldIdx]
                            : null;
                        return (
                          <TableCell key={col.key}>
                            {field ? (
                              field.subtype === 'date' ? (
                                <DatePicker
                                  value={field.value || null}
                                  disabled={!field.isEditable}
                                  onChange={(newValue) => {
                                    setEditRows((prev) => {
                                      const updated = [...prev];
                                      updated[idx] = {
                                        ...updated[idx],
                                        pduFields: updated[idx].pduFields.map(
                                          (f, i) =>
                                            i === fieldIdx
                                              ? { ...f, value: newValue }
                                              : f,
                                        ),
                                      };
                                      return updated;
                                    });
                                  }}
                                  slotProps={{
                                    textField: {
                                      variant: 'outlined',
                                      fullWidth: true,
                                      size: 'small',
                                    },
                                  }}
                                />
                              ) : (
                                <TextField
                                  variant="outlined"
                                  fullWidth
                                  size="small"
                                  type={
                                    field.subtype === 'number'
                                      ? 'number'
                                      : 'text'
                                  }
                                  value={field.value ?? ''}
                                  disabled={!field.isEditable}
                                  onChange={(e) => {
                                    const newValue =
                                      field.subtype === 'number'
                                        ? Number(e.target.value)
                                        : e.target.value;
                                    setEditRows((prev) => {
                                      const updated = [...prev];
                                      updated[idx] = {
                                        ...updated[idx],
                                        pduFields: updated[idx].pduFields.map(
                                          (f, i) =>
                                            i === fieldIdx
                                              ? { ...f, value: newValue }
                                              : f,
                                        ),
                                      };
                                      return updated;
                                    });
                                  }}
                                />
                              )
                            ) : (
                              <span style={{ color: '#aaa' }}>{t('-')}</span>
                            )}
                          </TableCell>
                        );
                      })}
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          );
          if (shouldScroll) {
            return (
              <div
                style={{
                  maxHeight: 800,
                  overflow: 'auto',
                  border: '1px solid #eee',
                }}
              >
                {TableContent}
              </div>
            );
          }
          return TableContent;
        })()}
      </BaseSection>
    </>
  );
};

export default withErrorBoundary(
  PeriodicDataUpdatesOnlineEditsTemplateDetailsPage,
  'PeriodicDataUpdatesOnlineEditsTemplateDetailsPage',
);
