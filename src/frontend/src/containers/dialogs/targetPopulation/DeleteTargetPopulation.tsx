import { LoadingButton } from '@components/core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';

export interface DeleteTargetPopulationProps {
  open: boolean;
  setOpen: (open: boolean) => void;
  targetPopulationId: string;
}

export const DeleteTargetPopulation = ({
  open,
  setOpen,
  targetPopulationId,
}: DeleteTargetPopulationProps): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const { mutateAsync: mutate, isPending: loadingDelete } = useMutation({
    mutationFn: ({
      businessAreaSlug,
      programSlug,
      id,
    }: {
      businessAreaSlug: string;
      programSlug: string;
      id: string;
    }) =>
      RestService.restBusinessAreasProgramsTargetPopulationsDestroy({
        businessAreaSlug,
        programSlug,
        id,
      }),
  });
  const handleDelete = async (): Promise<void> => {
    try {
      await mutate({
        businessAreaSlug: businessArea,
        programSlug: programId,
        id: targetPopulationId,
      });
      showMessage(t('Target Population Deleted'));
      navigate(`/${baseUrl}/payment-module/payment-plans`);
    } catch (e) {
      showMessage(e.message);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      scroll="paper"
      aria-labelledby="form-dialog-title"
    >
      <>
        <DialogTitleWrapper>
          <DialogTitle>{t('Delete Target Population')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            {t('Are you sure you want to remove this Target Population?')}
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
            <LoadingButton
              color="primary"
              variant="contained"
              loading={loadingDelete}
              onClick={() => handleDelete()}
              data-cy="button-delete"
            >
              {t('Delete')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </>
    </Dialog>
  );
};
