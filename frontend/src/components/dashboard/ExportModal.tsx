import {
  Box,
  Button,
  Checkbox,
  DialogContent,
  DialogTitle,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@material-ui/core';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { DialogContainer } from '../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '../../hooks/useSnackBar';
import {
  useCreateDashboardReportMutation,
  useDashboardReportChoiceDataQuery,
} from '../../__generated__/graphql';
import { LoadingComponent } from '../core/LoadingComponent';
import { useBaseUrl } from '../../hooks/useBaseUrl';

export const ExportModal = ({ filter, year }): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selected, setSelected] = useState([]);
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const { t } = useTranslation();
  const numSelected = selected.length;
  const isSelected = (id: string): boolean => selected.includes(id);

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useDashboardReportChoiceDataQuery({ variables: { businessArea } });
  const [mutate] = useCreateDashboardReportMutation();

  useEffect(() => {
    setSelected([]);
  }, [businessArea]);

  if (choicesLoading) return <LoadingComponent />;
  if (!choicesData) return null;

  const data = choicesData.dashboardReportTypesChoices.map((choice) => ({
    id: choice.value,
    name: choice.name,
  }));

  const rowCount = data.length;

  const onSelectAllClick = (event, rows): void => {
    if (event.target.checked) {
      const newSelecteds = rows.map((row) => row.id);
      setSelected(newSelecteds);
      return;
    }
    setSelected([]);
  };
  const onCheckboxClick = (id: string): void => {
    const selectedIndex = selected.indexOf(id);
    const newSelected = [...selected];
    if (selectedIndex !== -1) {
      newSelected.splice(selectedIndex, 1);
    } else {
      newSelected.push(id);
    }
    setSelected(newSelected);
  };

  const renderRows = (): Array<React.ReactElement> => {
    return data.map((el) => {
      const isItemSelected = isSelected(el.id);
      return (
        <TableRow onClick={() => onCheckboxClick(el.id)} key={el.id}>
          <TableCell align='left' padding='checkbox'>
            <Checkbox
              color='primary'
              onClick={() => onCheckboxClick(el.id)}
              checked={isItemSelected}
              inputProps={{ 'aria-labelledby': el.id }}
            />
          </TableCell>
          <TableCell align='left'>{el.name}</TableCell>
        </TableRow>
      );
    });
  };

  const submitFormHandler = async (): Promise<void> => {
    const response = await mutate({
      variables: {
        reportData: {
          businessAreaSlug: businessArea,
          reportTypes: selected,
          year: parseInt(year, 10),
          adminArea: filter.administrativeArea?.node?.id,
          program: programId,
        },
      },
    });
    if (!response.errors && response.data.createDashboardReport.success) {
      showMessage(t('Report was created.'));
    } else {
      showMessage(t('Report create action failed.'));
    }
    setSelected([]);
    setDialogOpen(false);
  };

  return (
    <>
      <Button
        color='primary'
        variant='contained'
        onClick={() => setDialogOpen(true)}
        data-cy='button-ed-plan'
      >
        Export
      </Button>
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
        maxWidth='md'
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Export Data')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box mb={6}>
              <Typography variant='body2'>
                {t(
                  'The filters applied on the dashboard will be used for the reports.',
                )}
              </Typography>
            </Box>
            <Box mb={2}>
              <Typography variant='subtitle2'>
                {t('Select types of reports to be exported')}:
              </Typography>
            </Box>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding='checkbox'>
                    <Checkbox
                      color='primary'
                      indeterminate={numSelected > 0 && numSelected < rowCount}
                      checked={rowCount > 0 && numSelected === rowCount}
                      onChange={(event) => onSelectAllClick(event, data)}
                      inputProps={{ 'aria-label': 'select all' }}
                    />
                  </TableCell>
                  <TableCell align='left'>{t('Report Type')}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>{renderRows()}</TableBody>
            </Table>
            <Box p={3} m={4} bgcolor='#F5F5F5'>
              <Typography variant='subtitle2'>
                {t(
                  'Upon clicking export button, report will be generated and send to your email address when ready.',
                )}
              </Typography>
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button
              onClick={() => {
                setDialogOpen(false);
                setSelected([]);
              }}
            >
              {t('CANCEL')}
            </Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={submitFormHandler}
              data-cy='button-submit'
            >
              {t('Export')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
