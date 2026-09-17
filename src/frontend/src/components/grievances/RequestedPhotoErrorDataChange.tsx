import { ApproveBox } from '@components/grievances/GrievancesApproveSection/ApproveSectionStyles';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import { Title } from '@core/Title';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import {
  Box,
  Button,
  Checkbox,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import type { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { restQueryKey } from '@utils/queryKeys';
import { showApiErrorMessages } from '@utils/utils';
import { Formik } from 'formik';
import type { ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PERMISSIONS } from 'src/config/permissions';

const PhotoPreview = styled.img`
  width: 120px;
  height: 120px;
  object-fit: cover;
  border: 1px solid ${({ theme }) => theme.palette.grey[300]};
  border-radius: 4px;
`;

const PlaceholderBox = styled(Box)`
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed ${({ theme }) => theme.palette.grey[400]};
  border-radius: 4px;
  color: ${({ theme }) => theme.palette.grey[600]};
  text-align: center;
`;

const GreenIcon = styled.div`
  color: #28cb15;
`;

const StyledTable = styled(Table)`
  min-width: 100px;
  width: 100%;
`;

function PhotoCell({ src }: { src?: string }): ReactElement {
  const { t } = useTranslation();
  if (!src) {
    return (
      <PlaceholderBox data-cy="photo-error-no-photo">
        {t('No photo')}
      </PlaceholderBox>
    );
  }
  return (
    <PhotoModal src={src} title={t('Photo')} alt={t('Photo')}>
      <PhotoPreview src={src} alt={t('Photo')} data-cy="photo-error-preview" />
    </PhotoModal>
  );
}

export function RequestedPhotoErrorDataChange({
  ticket,
  canApproveDataChange,
}: {
  ticket: GrievanceTicketDetail;
  canApproveDataChange: boolean;
}): ReactElement {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const photo = ticket.ticketDetails?.individualData?.photo ?? {};
  const isForApproval = ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;
  const [isEdit, setEdit] = useState(!photo.approveStatus);

  const { mutateAsync: mutate } = useMutation({
    mutationFn: (approved: boolean) =>
      RestService.restBusinessAreasGrievanceTicketsApproveIndividualDataChangeCreate(
        {
          businessAreaSlug: businessArea,
          id: ticket.id,
          formData: { individualApproveData: { photo: approved } },
        },
      ),
    onSuccess: () => {
      showMessage(t('Changes Approved'));
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasGrievanceTicketsRetrieve,
        ),
      });
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  return (
    <Formik
      initialValues={{ selected: photo.approveStatus ? ['photo'] : [] }}
      onSubmit={async (values) => {
        try {
          await mutate(values.selected.includes('photo'));
          setEdit(false);
        } catch {
          // Error handling is already in the mutation onError callback
        }
      }}
    >
      {({ submitForm, setFieldValue, values }) => {
        const isSelected = values.selected.includes('photo');
        const shouldShowEditButton = isSelected && !isEdit && isForApproval;
        return (
          <ApproveBox>
            <Title>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="h6">
                  {t('Requested Data Change')}
                </Typography>
                {shouldShowEditButton ? (
                  <Button
                    onClick={() => setEdit(true)}
                    variant="outlined"
                    color="primary"
                    disabled={ticket.status === GRIEVANCE_TICKET_STATES.CLOSED}
                  >
                    {t('EDIT')}
                  </Button>
                ) : (
                  canApproveDataChange && (
                    <Button
                      onClick={submitForm}
                      variant="contained"
                      color="primary"
                      disabled={!isForApproval}
                      data-cy="button-approve"
                      data-perm={PERMISSIONS.GRIEVANCES_APPROVE_DATA_CHANGE}
                    >
                      {t('Approve')}
                    </Button>
                  )
                )}
              </Box>
            </Title>
            <StyledTable>
              <TableHead>
                <TableRow>
                  <TableCell align="left" />
                  <TableCell data-cy="table-cell-type-of-data" align="left">
                    {t('Type of Data')}
                  </TableCell>
                  <TableCell
                    data-cy="table-cell-previous-current-value"
                    align="left"
                  >
                    {ticket.status === GRIEVANCE_TICKET_STATES.CLOSED
                      ? t('Previous')
                      : t('Current')}{' '}
                    {t('Value')}
                  </TableCell>
                  <TableCell data-cy="table-cell-new-value" align="left">
                    {t('New Value')}
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow role="checkbox" aria-checked={isSelected}>
                  <TableCell>
                    {isEdit ? (
                      <Checkbox
                        color="primary"
                        checked={isSelected}
                        disabled={!isForApproval}
                        onChange={() =>
                          setFieldValue('selected', isSelected ? [] : ['photo'])
                        }
                        data-cy="checkbox-requested-data-change"
                      />
                    ) : (
                      isSelected && (
                        <GreenIcon data-cy="green-tick">
                          <CheckCircleIcon />
                        </GreenIcon>
                      )
                    )}
                  </TableCell>
                  <TableCell scope="row" align="left">
                    {t('Biometric photo')}
                  </TableCell>
                  <TableCell align="left" data-cy="current-value">
                    <PhotoCell src={photo.previousValue} />
                  </TableCell>
                  <TableCell align="left" data-cy="new-value">
                    <PhotoCell src={photo.value} />
                  </TableCell>
                </TableRow>
              </TableBody>
            </StyledTable>
          </ApproveBox>
        );
      }}
    </Formik>
  );
}
