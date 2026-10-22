import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { ErrorButton } from '@core/ErrorButton';
import { GreyText } from '@core/GreyText';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import type { ApprovalProcess } from '@restgenerated/models/ApprovalProcess';
import { RestService } from '@restgenerated/services/RestService';
import { FormikTextField } from '@shared/Formik/FormikTextField/FormikTextField';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { showApiErrorMessages } from '@utils/utils';
import { Field, Form, Formik } from 'formik';
import type { ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { useProgramContext } from '../../../../../programContext';
import type { PaymentPlanGroupDetail } from '../types';

export type GroupAcceptanceAction =
  'approve' | 'authorize' | 'markAsReleased' | 'reject';

interface ActionConfig {
  request: typeof RestService.restBusinessAreasProgramsPaymentPlanGroupsApproveCreate;
  label: string;
  title: string;
  question: string;
  successMessage: string;
  dataCy: string;
  // Shown when this action completes the stage.
  lastActionNote: string;
  isLastAction: (process: ApprovalProcess | undefined) => boolean;
}

const isLast = (
  done: unknown[] | undefined,
  required: number | undefined,
): boolean => (required ?? 0) - 1 === (done?.length ?? 0);

const ACTIONS: Record<GroupAcceptanceAction, ActionConfig> = {
  approve: {
    request: (args) =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsApproveCreate(args),
    label: 'Approve',
    title: 'Approve Payment Plan',
    question: 'Are you sure you want to approve this Payment Plan?',
    successMessage: 'Payment Plan has been approved.',
    dataCy: 'button-approve',
    lastActionNote:
      'Note: You are the last approver. Upon proceeding, this Payment Plan will be automatically moved to authorization stage.',
    isLastAction: (process) =>
      isLast(process?.actions?.approval, process?.approvalNumberRequired),
  },
  authorize: {
    request: (args) =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsAuthorizeCreate(
        args,
      ),
    label: 'Authorize',
    title: 'Authorize Payment Plan',
    question: 'Are you sure you want to authorize this Payment Plan?',
    successMessage: 'Payment Plan has been authorized.',
    dataCy: 'button-authorize',
    lastActionNote:
      'Note: Upon Proceeding, this Payment Plan will be automatically moved to Finance Release stage.',
    isLastAction: (process) =>
      isLast(
        process?.actions?.authorization,
        process?.authorizationNumberRequired,
      ),
  },
  markAsReleased: {
    request: (args) =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsMarkAsReleasedCreate(
        args,
      ),
    label: 'Mark as released',
    title: 'Mark as Released',
    question: 'Are you sure you want to mark this Payment Plan as released?',
    successMessage: 'Payment Plan has been marked as released.',
    dataCy: 'button-mark-as-released',
    lastActionNote:
      'Note: You are the last reviewer. Upon proceeding, this Payment Plan will be automatically moved to accepted status',
    isLastAction: (process) =>
      isLast(
        process?.actions?.financeRelease,
        process?.financeReleaseNumberRequired,
      ),
  },
  reject: {
    request: (args) =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsRejectCreate(args),
    label: 'Reject',
    title: 'Reject Payment Plan',
    question: 'Are you sure you want to reject this Payment Plan?',
    successMessage: 'Payment Plan has been rejected.',
    dataCy: 'button-reject',
    lastActionNote:
      'Note: Upon proceeding this Payment Plan will be automatically moved to locked status.',
    isLastAction: () => true,
  },
};

interface AcceptanceActionGroupButtonProps {
  group: PaymentPlanGroupDetail;
  action: GroupAcceptanceAction;
}

export function AcceptanceActionGroupButton({
  group,
  action,
}: AcceptanceActionGroupButtonProps): ReactElement {
  const { t } = useTranslation();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();
  const [dialogOpen, setDialogOpen] = useState(false);
  const config = ACTIONS[action];

  const { mutate, isPending } = useMutation({
    mutationFn: (comment: string) =>
      config.request({
        businessAreaSlug: businessArea,
        programCode: programId,
        id: group.id,
        // The API rejects a blank comment, so leave it out when empty.
        requestBody: comment ? { comment } : {},
      }),
    onSuccess: async () => {
      showMessage(t(config.successMessage));
      setDialogOpen(false);
      await Promise.all(
        [
          RestService.restBusinessAreasProgramsPaymentPlanGroupsRetrieve,
          RestService.restBusinessAreasProgramsPaymentPlanGroupsList,
          RestService.restBusinessAreasProgramsPaymentPlansList,
        ].map((fn) =>
          queryClient.invalidateQueries({ queryKey: restQueryKey(fn) }),
        ),
      );
    },
    onError: (error) => showApiErrorMessages(error, showMessage),
  });

  const validationSchema = Yup.object().shape({
    comment: Yup.string().min(4, 'Too short').max(255, 'Too long'),
  });
  const showLastActionNote = config.isLastAction(group.approvalProcess?.[0]);

  return (
    <Formik
      initialValues={{ comment: '' }}
      onSubmit={(values, { resetForm }) => {
        mutate(values.comment);
        resetForm({});
      }}
      validationSchema={validationSchema}
    >
      {({ submitForm }) => (
        <>
          {dialogOpen && <AutoSubmitFormOnEnter />}
          <Box sx={{ p: 2 }}>
            {action === 'reject' ? (
              <ErrorButton
                onClick={() => setDialogOpen(true)}
                data-cy={config.dataCy}
                disabled={!isActiveProgram}
              >
                {t(config.label)}
              </ErrorButton>
            ) : (
              <Button
                color="primary"
                variant="contained"
                onClick={() => setDialogOpen(true)}
                data-cy={config.dataCy}
                disabled={!isActiveProgram}
              >
                {t(config.label)}
              </Button>
            )}
          </Box>
          <Dialog
            open={dialogOpen}
            onClose={() => setDialogOpen(false)}
            scroll="paper"
            aria-labelledby="form-dialog-title"
            maxWidth="md"
          >
            <DialogTitleWrapper>
              <DialogTitle>{t(config.title)}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Box sx={{ p: 5 }}>{t(config.question)}</Box>
                {showLastActionNote && (
                  <Box sx={{ p: 5 }}>
                    <GreyText>{t(config.lastActionNote)}</GreyText>
                  </Box>
                )}
                <Form>
                  <Field
                    name="comment"
                    multiline
                    fullWidth
                    variant="filled"
                    label="Comment (optional)"
                    component={FormikTextField}
                  />
                </Form>
              </DialogContainer>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setDialogOpen(false)}>CANCEL</Button>
                <LoadingButton
                  loading={isPending}
                  type="submit"
                  color="primary"
                  variant="contained"
                  onClick={submitForm}
                  data-cy="button-submit"
                >
                  {t(config.label)}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </>
      )}
    </Formik>
  );
}
