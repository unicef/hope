import { BaseSection } from '@components/core/BaseSection';
import { BlackLink } from '@components/core/BlackLink';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LabelizedField } from '@components/core/LabelizedField';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { StatusBox } from '@components/core/StatusBox';
import { UniversalMoment } from '@components/core/UniversalMoment';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid2 as Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
} from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  periodicDataUpdatesOnlineEditsStatusToColor,
  showApiErrorMessages,
} from '@utils/utils';
import { ReactElement, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from 'src/programContext';
import { ConfirmationDialog } from '../../components/core/ConfirmationDialog/ConfirmationDialog';
import PeriodicDataUpdateEditableTable from './PeriodicDataUpdateEditableTable';
import SentBackComment from './SentBackComment';

export type PduField = {
  value: any;
  subtype: string;
  roundName: string;
  isEditable: boolean;
  roundNumber: number;
  fieldName?: string;
  label?: string;
};

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
  const permissions = usePermissions();
  const canSave = hasPermissions(PERMISSIONS.PDU_ONLINE_SAVE_DATA, permissions);
  const canApprove = hasPermissions(
    PERMISSIONS.PDU_ONLINE_APPROVE,
    permissions,
  );
  const canMerge = hasPermissions(PERMISSIONS.PDU_ONLINE_MERGE, permissions);

  // Confirmation dialog state for Send Back
  const [sendBackDialogOpen, setSendBackDialogOpen] = useState(false);
  const [sendBackComment, setSendBackComment] = useState('');
  const [sendBackLoading, setSendBackLoading] = useState(false);
  const [sendForApprovalLoading, setSendForApprovalLoading] = useState(false);

  const { mutateAsync: bulkApprove } = useMutation({
    mutationFn: (ids: number[]) => {
      return RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsBulkApproveCreate(
        {
          businessAreaSlug: businessArea,
          programSlug: programId,
          requestBody: { ids },
        },
      );
    },
    onSuccess: () => {
      showMessage(t('Template approved successfully.'));
      queryClient.invalidateQueries({
        queryKey: [
          'onlineEditsTemplateDetails',
          businessArea,
          programId,
          numericId,
        ],
      });
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  const handleApprove = async () => {
    await bulkApprove([numericId]);
  };

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

  const { mutateAsync: bulkMerge } = useMutation({
    mutationFn: (ids: number[]) => {
      return RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsBulkMergeCreate(
        {
          businessAreaSlug: businessArea,
          programSlug: programId,
          requestBody: { ids },
        },
      );
    },
    onSuccess: () => {
      showMessage('Template merged successfully.');
      queryClient.invalidateQueries({
        queryKey: [
          'onlineEditsTemplateDetails',
          businessArea,
          programId,
          numericId,
        ],
      });
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  const handleMerge = async () => {
    await bulkMerge([numericId]);
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
    const fields: Array<{
      key: string;
      subtype: string;
      roundNumber: number;
      roundName: string;
      fieldName: string;
      label: string;
    }> = [];
    individuals.forEach((ind) => {
      if (ind.pduFields) {
        Object.entries(ind.pduFields).forEach(([objKey, _field]) => {
          const field = _field as PduField;
          if (!fields.some((f) => f.key === objKey)) {
            fields.push({
              key: objKey,
              subtype: field.subtype,
              roundNumber: field.roundNumber,
              roundName: field.roundName,
              fieldName: field.fieldName,
              label: field.label,
            });
          }
        });
      }
    });
    return fields;
  }, [individuals]);

  const [editRows, setEditRows] = useState(() => {
    return individuals.map((ind) => {
      // Remap pduFields to use backend fieldName as key
      const newPduFields: { [key: string]: PduField } = {};
      if (ind.pduFields) {
        Object.entries(ind.pduFields).forEach(([key, field]) => {
          const f = field as PduField;
          const backendKey = f.fieldName || key;
          newPduFields[backendKey] = { ...f, fieldName: backendKey };
        });
      }
      return {
        ...ind,
        pduFields: newPduFields,
      };
    });
  });

  // Track which rows are in edit mode
  const [editingRows, setEditingRows] = useState<Set<number>>(new Set());

  useEffect(() => {
    setEditRows(
      individuals.map((ind) => {
        // Remap pduFields to use backend fieldName as key
        const newPduFields: { [key: string]: PduField } = {};
        if (ind.pduFields) {
          Object.entries(ind.pduFields).forEach(([key, field]) => {
            const f = field as PduField;
            const backendKey = f.fieldName || key;
            newPduFields[backendKey] = { ...f, fieldName: backendKey };
          });
        }
        return {
          ...ind,
          pduFields: newPduFields,
        };
      }),
    );
    setEditingRows(new Set()); // Reset edit mode on data change
  }, [individuals]);

  // Save handler: call API and exit edit mode for row
  const handleSaveRow = async (rowIdx: number) => {
    const row = editRows[rowIdx];
    const payload = {
      individualUuid: row.individualUuid,
      pduFields: Object.entries(row.pduFields || {}).reduce(
        (acc, [, field]) => {
          const f = field as PduField;
          const backendKey = f.fieldName;
          acc[backendKey] = {
            roundNumber: f.roundNumber,
            value: f.value,
            subtype: f.subtype,
            isEditable: f.isEditable,
            fieldName: backendKey,
          };
          return acc;
        },
        {},
      ),
    };

    try {
      await RestService.restBusinessAreasProgramsPeriodicDataUpdateOnlineEditsSaveDataCreate(
        {
          businessAreaSlug: businessArea,
          programSlug: programId,
          id: numericId,
          requestBody: payload,
        },
      );
      setEditingRows((prev) => {
        const updated = new Set(prev);
        updated.delete(rowIdx);
        return updated;
      });
    } catch (e) {
      showApiErrorMessages(e, showMessage);
    }
  };

  if (isLoading) return <LoadingComponent />;
  if (!data) return null;

  const {
    status,
    statusDisplay,
    name,
    createdAt,
    numberOfRecords,
    authorizedUsers,
    approvedBy,
    approvedAt,
    createdBy,
    sentBackComment,
    isCreator,
    isAuthorized,
  } = data;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: `${beneficiaryGroup?.memberLabelPlural}`,
      to: `/${baseUrl}/population/individuals`,
    },
  ];

  return (
    <>
      <PageHeader
        title={`Online Edits Template Details: ${name}`}
        breadCrumbs={breadCrumbsItems}
      >
        <>
          {status === 'NEW' && canSave && isAuthorized && (
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
          {status === 'READY' && canApprove && isAuthorized && (
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
                onClick={handleApprove}
                data-cy="approve"
              >
                {t('Approve')}
              </Button>
            </Box>
          )}
          {status === 'APPROVED' && canMerge && isAuthorized && (
            <Box px={6} pt={2} pb={2} display="flex" gap={2}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleMerge}
                data-cy="merge"
              >
                {t('Merge')}
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
                statusToColor={periodicDataUpdatesOnlineEditsStatusToColor}
                statusDisplay={statusDisplay}
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
                {`${authorizedUsers && authorizedUsers.length ? authorizedUsers.length : 0} ${t(authorizedUsers && authorizedUsers.length === 1 ? 'Authorized User' : 'Authorized Users')}`}
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
              {isCreator && (
                <Button
                  component={Link}
                  to={`/${baseUrl}/population/individuals/online-templates/${numericId}/edit-authorised-users`}
                  variant="text"
                  color="primary"
                >
                  {t('Edit')}
                </Button>
              )}
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

      <Box pl={12} pt={6}>
        {sentBackComment &&
          typeof sentBackComment === 'object' &&
          sentBackComment.comment && (
            <SentBackComment
              key={sentBackComment.comment}
              comment={sentBackComment.comment}
              date={sentBackComment.createdAt}
              author={sentBackComment.createdBy}
            />
          )}
      </Box>

      {/* Periodic Data Update Table */}
      <Box p={3}>
        <PeriodicDataUpdateEditableTable
          allPduFields={allPduFields}
          editRows={editRows}
          setEditRows={setEditRows}
          editingRows={editingRows}
          setEditingRows={setEditingRows}
          handleSaveRow={handleSaveRow}
          canSave={canSave}
          templateStatus={status}
        />
      </Box>
    </>
  );
};

export default withErrorBoundary(
  PeriodicDataUpdatesOnlineEditsTemplateDetailsPage,
  'PeriodicDataUpdatesOnlineEditsTemplateDetailsPage',
);
