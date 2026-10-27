import { Dialog } from '@containers/dialogs/Dialog';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Box,
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  Radio,
  RadioGroup,
} from '@mui/material';
import type { BulkUpdateGrievanceTicketsAssignees } from '@restgenerated/models/BulkUpdateGrievanceTicketsAssignees';
import type { User } from '@restgenerated/models/User';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import type { ApiErrorShape } from '@utils/utils';
import { showApiErrorMessages } from '@utils/utils';
import type { ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AssignedToDropdown } from '../GrievancesTable/AssignedToDropdown';

type AssignMode = 'me' | 'other';

interface AssignGrievanceDialogProps {
  ticketId: string;
  // status-change accepts the _AS_CREATOR/_AS_OWNER perms, the bulk endpoint only GRIEVANCES_UPDATE.
  onAssignToMe: () => Promise<boolean>;
  canAssignToOther: boolean;
  loading?: boolean;
  // The ticket's programme, not the URL's: the URL says `all` in the All Programmes view.
  programCode?: string;
  disabled?: boolean;
}

export function AssignGrievanceDialog({
  ticketId,
  onAssignToMe,
  canAssignToOther,
  loading,
  programCode,
  disabled,
}: AssignGrievanceDialogProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { businessAreaSlug } = useBaseUrl();
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<AssignMode>('me');
  const [assignee, setAssignee] = useState<User | null>(null);
  const [inputValue, setInputValue] = useState('');

  const { mutateAsync, isPending } = useMutation({
    mutationFn: (params: BulkUpdateGrievanceTicketsAssignees) =>
      RestService.restBusinessAreasGrievanceTicketsBulkUpdateAssigneeCreate({
        businessAreaSlug,
        formData: params,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasGrievanceTicketsRetrieve,
        ),
      });
      showMessage(t('Ticket assigned.'));
    },
    onError: (error: ApiErrorShape) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  const usersParams = {
    businessAreaSlug,
    limit: 20,
    orderBy: ['first_name', 'last_name', 'email'],
    ...(programCode && { program: programCode }),
    search: inputValue,
  } satisfies Parameters<typeof RestService.restBusinessAreasUsersList>[0];
  const { data: usersData } = useQuery({
    queryKey: restQueryKey(RestService.restBusinessAreasUsersList, usersParams),
    queryFn: () => RestService.restBusinessAreasUsersList(usersParams),
    enabled: open && mode === 'other',
  });

  const handleClose = (): void => {
    setOpen(false);
    setMode('me');
    setAssignee(null);
  };

  const onConfirm = async (): Promise<void> => {
    if (mode === 'me') {
      if (await onAssignToMe()) handleClose();
      return;
    }
    if (!assignee) return;
    try {
      await mutateAsync({
        assignedTo: assignee.id,
        grievanceTicketIds: [ticketId],
      });
      handleClose();
    } catch {
      // handled in onError
    }
  };

  return (
    <>
      <Button
        color="primary"
        variant="contained"
        onClick={() => setOpen(true)}
        data-cy="button-assign"
        disabled={disabled}
      >
        {t('ASSIGN')}
      </Button>
      <Dialog
        open={open}
        onClose={handleClose}
        scroll="paper"
        aria-labelledby="assign-grievance-dialog-title"
        data-cy="dialog-assign-grievance"
      >
        <DialogTitleWrapper>
          <DialogTitle id="assign-grievance-dialog-title">
            {t('Assign ticket')}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <Box sx={{ minWidth: 400, mt: 2, mb: 4 }}>
            <RadioGroup
              value={mode}
              onChange={(e) => setMode(e.target.value as AssignMode)}
            >
              <FormControlLabel
                value="me"
                control={<Radio data-cy="radio-assign-to-me" />}
                label={t('Assign to me')}
              />
              <FormControlLabel
                value="other"
                control={<Radio data-cy="radio-assign-to-other" />}
                label={t('Assign to another officer')}
                disabled={!canAssignToOther}
              />
            </RadioGroup>
            {mode === 'other' && (
              <Box sx={{ mt: 2 }}>
                <AssignedToDropdown
                  optionsData={usersData?.results || []}
                  value={assignee}
                  onFilterChange={setAssignee}
                  setInputValue={setInputValue}
                  label={t('Assignee')}
                  fullWidth
                />
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button data-cy="button-cancel" onClick={handleClose}>
              {t('CANCEL')}
            </Button>
            <LoadingButton
              loading={isPending || loading}
              data-cy="button-confirm-assign"
              variant="contained"
              color="primary"
              onClick={onConfirm}
              disabled={mode === 'other' && !assignee}
            >
              {t('ASSIGN')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}
