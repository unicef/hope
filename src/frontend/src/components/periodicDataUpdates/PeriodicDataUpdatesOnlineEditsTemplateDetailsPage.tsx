import React, { ReactElement, useMemo, useEffect, useState } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Grid2 as Grid,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { BlackLink } from '@components/core/BlackLink';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { BaseSection } from '@components/core/BaseSection';
import { LabelizedField } from '@components/core/LabelizedField';
import { StatusBox } from '@components/core/StatusBox';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { useParams, Link } from 'react-router-dom';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { useTranslation } from 'react-i18next';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  showApiErrorMessages,
  periodicDataUpdateTemplateStatusToColor,
} from '@utils/utils';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { useProgramContext } from 'src/programContext';
import SentBackComment from './SentBackComment';
import { ConfirmationDialog } from '../../components/core/ConfirmationDialog/ConfirmationDialog';

type PduField = {
  value: any;
  subtype: string;
  roundName: string;
  isEditable: boolean;
  roundNumber: number;
  columnName?: string;
};

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

function getUserRoles(
  user: { pduPermissions?: string[] },
  t: (s: string) => string,
): string {
  if (!user || !Array.isArray(user.pduPermissions)) {
    return '-';
  }
  const roles: string[] = [];
  if (user.pduPermissions.indexOf('PDU_ONLINE_SAVE_DATA') !== -1) {
    roles.push(t('Edit'));
  }
  if (user.pduPermissions.indexOf('PDU_ONLINE_APPROVE') !== -1) {
    roles.push(t('Approve'));
  }
  if (user.pduPermissions.indexOf('PDU_ONLINE_MERGE') !== -1) {
    roles.push(t('Merge'));
  }
  return roles.length > 0 ? roles.join(', ') : '-';
}

const PeriodicDataUpdatesOnlineEditsTemplateDetailsPage = (): ReactElement => {
  const { businessArea, programId, baseUrl } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const { id } = useParams();
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const numericId = id ? parseInt(id, 10) : undefined;
  const queryClient = useQueryClient();

  // Confirmation dialog state for Send Back
  const [sendBackDialogOpen, setSendBackDialogOpen] = useState(false);
  const [sendBackComment, setSendBackComment] = useState('');
  const [sendBackLoading, setSendBackLoading] = useState(false);
  const [sendForApprovalLoading, setSendForApprovalLoading] = useState(false);

  const handleSendBackConfirm = async () => {
    setSendBackLoading(true);
    try {
      await RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsSendBackCreate(
        {
          businessAreaSlug: businessArea,
          programSlug: programId,
          id: numericId,
          requestBody: { comment: sendBackComment },
        },
      );
      showMessage(t('Periodic data update sent back successfully.'));
      setSendBackDialogOpen(false);
      setSendBackComment('');
      queryClient.invalidateQueries({
        queryKey: [
          'onlineEditsTemplateDetails',
          businessArea,
          programId,
          numericId,
        ],
      });
    } catch (e) {
      showApiErrorMessages(
        e,
        showMessage,
        t('Failed to send back periodic data update.'),
      );
    } finally {
      setSendBackLoading(false);
    }
  };

  const handleSendForApproval = async () => {
    setSendForApprovalLoading(true);
    try {
      await RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsSendForApprovalCreate(
        {
          businessAreaSlug: businessArea,
          programSlug: programId,
          id: numericId,
        },
      );
      showMessage(t('Periodic data update sent for approval.'));
      queryClient.invalidateQueries({
        queryKey: [
          'onlineEditsTemplateDetails',
          businessArea,
          programId,
          numericId,
        ],
      });
    } catch (e) {
      showApiErrorMessages(e, showMessage, t('Failed to send for approval.'));
    } finally {
      setSendForApprovalLoading(false);
    }
  };

  // Modal state for Authorized Users
  const [authorizedUsersModalOpen, setAuthorizedUsersModalOpen] =
    useState(false);

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
        Object.values(ind.pduFields).forEach((_field) => {
          const field = _field as PduField;
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
      pduFields: ind.pduFields ? { ...ind.pduFields } : {},
    }));
  });

  // Track which rows are in edit mode
  const [editingRows, setEditingRows] = useState<Set<number>>(new Set());

  useEffect(() => {
    setEditRows(
      individuals.map((ind) => ({
        ...ind,
        pduFields: ind.pduFields ? { ...ind.pduFields } : {},
      })),
    );
    setEditingRows(new Set()); // Reset edit mode on data change
  }, [individuals]);

  // Save handler: call API and exit edit mode for row
  const handleSaveRow = async (rowIdx: number) => {
    const rowData = editRows[rowIdx];
    try {
      await RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsUpdate(
        {
          businessAreaSlug: businessArea,
          programSlug: programId,
          id: numericId,
          ...rowData,
        },
      );
      setEditingRows((prev) => {
        const updated = new Set(prev);
        updated.delete(rowIdx);
        return updated;
      });
    } catch (e) {
      // @ts-ignore
      showMessage('An error occurred while updating the data');
    }
  };

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
    sentBackComment,
  } = data;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: `${beneficiaryGroup?.memberLabelPlural}`,
      to: `/${baseUrl}/population/individuals`,
    },
  ];

  // Fake sent back comments data
  // const sentBackComments = [
  //   {
  //     comment:
  //       'Missing Date for Individual ID: 69023-3455, please update before sending for approval again',
  //     date: '13 May 2025',
  //     author: 'Jon Snow',
  //   },
  //   {
  //     comment: 'Please verify the address for Individual ID: 69023-3456.',
  //     date: '10 May 2025',
  //     author: 'Arya Stark',
  //   },
  // ];

  return (
    <>
      <PageHeader
        title={`Online Edits Template Details: ${name}`}
        breadCrumbs={breadCrumbsItems}
      >
        <>
          {status === 'NEW' && (
            <Box px={6} pt={2} pb={2}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleSendForApproval}
                disabled={sendForApprovalLoading}
                data-cy="send-for-approval"
              >
                {t('Send for Approval')}
              </Button>
            </Box>
          )}
          {status === 'READY' && (
            <Box px={6} pt={2} pb={2} display="flex" gap={2}>
              <Button
                variant="contained"
                color="primary"
                onClick={() => setSendBackDialogOpen(true)}
                data-cy="send-back"
              >
                {t('Send Back')}
              </Button>
              <Button
                variant="contained"
                color="primary"
                // Add approve handler here
                data-cy="approve"
              >
                {t('Approve')}
              </Button>
            </Box>
          )}
          {/* Show Send for Approval button if status is OPEN */}
          {status === 'OPEN' && (
            <Box px={6} pt={2} pb={2}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleSendForApproval}
                disabled={sendForApprovalLoading}
                data-cy="send-for-approval"
              >
                {sendForApprovalLoading
                  ? t('Sending...')
                  : t('Send for Approval')}
              </Button>
            </Box>
          )}
        </>
      </PageHeader>
      {/* Confirmation Dialog for Send Back */}
      <ConfirmationDialog
        open={sendBackDialogOpen}
        title={t('Send Back Confirmation')}
        content={t(
          'Are you sure you want to send back this periodic data update? Please provide a comment.',
        )}
        continueText={t('Confirm')}
        onSubmit={handleSendBackConfirm}
        onClose={() => setSendBackDialogOpen(false)}
        disabled={sendBackLoading || !sendBackComment}
        extraContent={
          <TextField
            label={t('Comment')}
            multiline
            fullWidth
            minRows={3}
            value={sendBackComment}
            onChange={(e) => setSendBackComment(e.target.value)}
            disabled={sendBackLoading}
          />
        }
        type="primary"
      />
      <BaseSection title="Details">
        <Grid container spacing={6}>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Status')}>
              <StatusBox
                status={status}
                statusToColor={periodicDataUpdateTemplateStatusToColor}
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
            <LabelizedField label={t('Authorized Users')}>
              <BlackLink
                button
                style={{ cursor: 'pointer', textDecoration: 'underline' }}
                onClick={() => setAuthorizedUsersModalOpen(true)}
              >
                {`${authorizedUsers && authorizedUsers.length ? authorizedUsers.length : 0} ${t('Authorized Users')}`}
              </BlackLink>
            </LabelizedField>
          </Grid>
          {/* Authorized Users Modal */}
          <Dialog
            open={authorizedUsersModalOpen}
            onClose={() => setAuthorizedUsersModalOpen(false)}
            maxWidth="sm"
            fullWidth
          >
            <DialogTitle sx={{ pb: 0 }}>
              {t('Authorized Users for Online Editing')}
            </DialogTitle>
            <DialogContent>
              <div style={{ marginBottom: 16 }}>
                {t(
                  'Users who are allowed to add new values for this template during online updates.',
                )}
              </div>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>{t('Name')}</TableCell>
                      <TableCell>{t('Role')}</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(authorizedUsers && authorizedUsers.length > 0
                      ? authorizedUsers
                      : []
                    ).map((user, idx) => (
                      <TableRow key={user.id || user.username || idx}>
                        <TableCell>
                          {user.firstName && user.lastName
                            ? `${user.firstName} ${user.lastName}`
                            : user.username || user.email || user.id}
                        </TableCell>
                        <TableCell>{getUserRoles(user, t)}</TableCell>
                      </TableRow>
                    ))}
                    {(!authorizedUsers || authorizedUsers.length === 0) && (
                      <TableRow>
                        <TableCell colSpan={2} align="center">
                          {t('No authorized users found.')}
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </DialogContent>
            <DialogActions>
              <Button
                component={Link}
                to={`/${baseUrl}/population/individuals/online-templates/${numericId}/edit-authorised-users`}
                variant="text"
                color="primary"
              >
                {t('Edit')}
              </Button>
              <Button
                variant="contained"
                color="primary"
                onClick={() => setAuthorizedUsersModalOpen(false)}
              >
                {t('Close')}
              </Button>
            </DialogActions>
          </Dialog>
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

      {/* //TODO: example */}
      {/* Sent Back Comments */}
      {/* {sentBackComments.map((c, idx) => (
        <SentBackComment
          key={idx}
          comment={c.comment}
          date={c.date}
          author={c.author}
        />
      ))} */}
      {sendBackComment && (
        <SentBackComment
          key={sentBackComment.id}
          comment={sentBackComment.comment}
          date={sentBackComment.date}
          author={sentBackComment.author}
        />
      )}

      {/* Periodic Data Update Table */}
      <Box p={6}>
        <BaseSection title="Periodic Data Update">
          {(() => {
            const shouldScroll =
              editRows.length > 10 || allPduFields.length > 6;
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
                      <TableCell
                        colSpan={3 + allPduFields.length}
                        align="center"
                      >
                        {t('No data available')}
                      </TableCell>
                    </TableRow>
                  ) : (
                    editRows.map((individual, idx) => {
                      const isEditing = editingRows.has(idx);
                      // Only show Edit button if at least one PDU field is editable
                      const hasEditableField =
                        individual.pduFields &&
                        Object.values(individual.pduFields).some(
                          (f: any) => f.isEditable,
                        );
                      return (
                        <TableRow key={individual.individualUuid || idx}>
                          <TableCell>
                            {individual.individualUuid ? (
                              <BlackLink
                                to={`/population/individuals/${individual.individualUuid}`}
                              >
                                {individual.unicefId}
                              </BlackLink>
                            ) : (
                              t('-')
                            )}
                          </TableCell>
                          <TableCell>{individual.firstName}</TableCell>
                          <TableCell>{individual.lastName}</TableCell>
                          {allPduFields.map((col) => {
                            // Find the matching pduField for this column
                            const pduFieldArr: PduField[] = individual.pduFields
                              ? Object.values(individual.pduFields).map(
                                  (f) => f as PduField,
                                )
                              : [];
                            const fieldIdx = pduFieldArr.findIndex(
                              (f) =>
                                `${f.subtype}|${f.roundNumber}|${f.roundName}|${f.columnName || f.subtype}` ===
                                col.key,
                            );
                            const field =
                              fieldIdx !== -1 ? pduFieldArr[fieldIdx] : null;
                            return (
                              <TableCell key={col.key}>
                                {field ? (
                                  isEditing && field.isEditable ? (
                                    field.subtype === 'date' ? (
                                      <DatePicker
                                        value={field.value || null}
                                        onChange={(newValue) => {
                                          setEditRows((prev) => {
                                            const updated = [...prev];
                                            const pduFieldsObj = {
                                              ...updated[idx].pduFields,
                                            };
                                            const fieldKey =
                                              Object.keys(pduFieldsObj)[
                                                fieldIdx
                                              ];
                                            if (fieldKey) {
                                              pduFieldsObj[fieldKey] = {
                                                ...pduFieldsObj[fieldKey],
                                                value: newValue,
                                              };
                                              updated[idx] = {
                                                ...updated[idx],
                                                pduFields: pduFieldsObj,
                                              };
                                            }
                                            return updated;
                                          });
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
                                        onChange={(e) => {
                                          const newValue =
                                            field.subtype === 'number'
                                              ? Number(e.target.value)
                                              : e.target.value;
                                          setEditRows((prev) => {
                                            const updated = [...prev];
                                            const pduFieldsObj = {
                                              ...updated[idx].pduFields,
                                            };
                                            const fieldKey =
                                              Object.keys(pduFieldsObj)[
                                                fieldIdx
                                              ];
                                            if (fieldKey) {
                                              pduFieldsObj[fieldKey] = {
                                                ...pduFieldsObj[fieldKey],
                                                value: newValue,
                                              };
                                              updated[idx] = {
                                                ...updated[idx],
                                                pduFields: pduFieldsObj,
                                              };
                                            }
                                            return updated;
                                          });
                                        }}
                                      />
                                    )
                                  ) : // Display mode: show value as plain text for non-editable fields, and for editable fields when not editing
                                  field.subtype === 'date' ? (
                                    field.value ? (
                                      <UniversalMoment>
                                        {field.value}
                                      </UniversalMoment>
                                    ) : (
                                      <span style={{ color: '#aaa' }}>
                                        {t('-')}
                                      </span>
                                    )
                                  ) : field.value !== undefined &&
                                    field.value !== null &&
                                    field.value !== '' ? (
                                    String(field.value)
                                  ) : (
                                    <span style={{ color: '#aaa' }}>
                                      {t('-')}
                                    </span>
                                  )
                                ) : (
                                  <span style={{ color: '#aaa' }}>
                                    {t('-')}
                                  </span>
                                )}
                              </TableCell>
                            );
                          })}
                          <TableCell>
                            {hasEditableField ? (
                              isEditing ? (
                                <Button
                                  variant="contained"
                                  color="primary"
                                  size="small"
                                  onClick={() => handleSaveRow(idx)}
                                >
                                  {t('Save')}
                                </Button>
                              ) : (
                                <Button
                                  variant="outlined"
                                  color="primary"
                                  size="small"
                                  onClick={() =>
                                    setEditingRows((prev) => {
                                      const updated = new Set(prev);
                                      updated.add(idx);
                                      return updated;
                                    })
                                  }
                                >
                                  {t('Edit')}
                                </Button>
                              )
                            ) : null}
                          </TableCell>
                        </TableRow>
                      );
                    })
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
      </Box>
    </>
  );
};

export default withErrorBoundary(
  PeriodicDataUpdatesOnlineEditsTemplateDetailsPage,
  'PeriodicDataUpdatesOnlineEditsTemplateDetailsPage',
);
