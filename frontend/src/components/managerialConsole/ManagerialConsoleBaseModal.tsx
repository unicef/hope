import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import {
  Button,
  DialogTitle,
  DialogContent,
  Box,
  Typography,
  TableBody,
  DialogActions,
  Dialog,
  Table,
  TextField,
} from '@mui/material';
import styled from 'styled-components';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;
const StyledTable = styled(Table)`
  min-width: 400px;
  max-width: 800px;
`;
const StyledDialog = styled(Dialog)`
  max-height: 800px;
`;

const Bold = styled.span`
  font-weight: bold;
`;

interface ManagerialConsoleBaseModalProps {
  selectedPlansIds: string[];
  selectedPlansUnicefIds: string[];
  buttonTitle: string;
  dialogTitle: string;
  title: string;
  children?: React.ReactNode;
  onSave: (plans, comment) => Promise<void>;
  disabledSave?: boolean;
}

export const ManagerialConsoleBaseModal = ({
  selectedPlansIds,
  selectedPlansUnicefIds,
  buttonTitle,
  dialogTitle,
  title,
  children,
  onSave,
  disabledSave,
}: ManagerialConsoleBaseModalProps): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [comment, setComment] = useState('');
  const { t } = useTranslation();
  const { isActiveProgram } = useProgramContext();

  const renderButton = (): React.ReactElement => (
    <Button
      variant="outlined"
      color="primary"
      disabled={!selectedPlansIds.length || !isActiveProgram}
      onClick={() => setDialogOpen(true)}
      data-cy={`${buttonTitle.toLowerCase()}-button`}
    >
      {buttonTitle}
    </Button>
  );
  const onAccept = async (): Promise<void> => {
    try {
      await onSave(selectedPlansIds, comment);
    } catch (e) {
      // handled by inner function
    } finally {
      setDialogOpen(false);
    }
  };

  return (
    <>
      {renderButton()}
      <StyledDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        <DialogTitleWrapper>
          <DialogTitle id="dialog-title">{dialogTitle}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <Box mt={2} mb={6}>
            <Typography>{title}</Typography>
            <Typography>
              {t('Selected Plans IDs')}:{' '}
              <Bold data-cy="plans-ids">
                {selectedPlansUnicefIds?.join(', ')}
              </Bold>
            </Typography>
            <Box mt={4}>
              <TextField
                size="small"
                label={t('Comment')}
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                multiline
                inputProps={{ maxLength: 500 }}
                fullWidth
              />
            </Box>
          </Box>
          <StyledTable>
            <TableBody>{children}</TableBody>
          </StyledTable>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button
              onClick={() => {
                setDialogOpen(false);
              }}
              data-cy="button-cancel"
            >
              {t('CANCEL')}
            </Button>
            <Button
              variant="contained"
              color="primary"
              onClick={onAccept}
              disabled={disabledSave}
              data-cy="button-save"
            >
              {t('SAVE')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </StyledDialog>
    </>
  );
};
