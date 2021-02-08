import React, { useState } from 'react';
import {
  Button,
  DialogContent,
  DialogTitle,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Checkbox,
  Typography,
  Box,
} from '@material-ui/core';
import styled from 'styled-components';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogContainer = styled.div`
  width: 700px;
`;

export const ExportModal = (): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selected, setSelected] = useState([]);
  const numSelected = selected.length;
  const isSelected = (name: string): boolean => selected.includes(name);

  //TODO change line below
  const data = [
    { id: '1', name: 'Total Amount Transferred' },
    { id: '2', name: 'Total Amount Planned and Transferred by Country' },
    { id: '4', name: 'Beneficiaries Reached' },
    { id: '5', name: 'Individuals Reached by Age and Gender Groups' },
    { id: '6', name: 'Individuals with Disability Reached by Age Groups' },
    { id: '7', name: 'Volume by Delivery Mechanism' },
    { id: '8', name: 'Grievances' },
    { id: '9', name: 'Programmes by Sector' },
    { id: '10', name: 'Monthly Transfers' },
    { id: '11', name: 'Payments' },
    { id: '12', name: 'Payment Verification' },
  ];
  const rowCount = data.length;

  const onSelectAllClick = (event, rows): void => {
    if (event.target.checked) {
      const newSelecteds = rows.map((row) => row.id);
      setSelected(newSelecteds);
      return;
    }
    setSelected([]);
  };
  const onCheckboxClick = (name): void => {
    const selectedIndex = selected.indexOf(name);
    const newSelected = [];
    if (selectedIndex !== -1) {
      newSelected.splice(selectedIndex, 1);
    } else {
      newSelected.push(name);
    }
    setSelected(newSelected);
  };
  const renderRows = (): Array<React.ReactElement> => {
    return data.map((el) => {
      const isItemSelected = isSelected(el.id);
      return (
        <TableRow key={el.id}>
          <TableCell align='left'>
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
        fullWidth
        maxWidth='md'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>Export Data</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box mb={2}>
              <Typography variant='subtitle2'>
                Select types of reports to be exported
              </Typography>
            </Box>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>
                    <Checkbox
                      color='primary'
                      indeterminate={numSelected > 0 && numSelected < rowCount}
                      checked={rowCount > 0 && numSelected === rowCount}
                      onChange={(event) => onSelectAllClick(event, data)}
                      inputProps={{ 'aria-label': 'select all' }}
                    />
                  </TableCell>
                  <TableCell align='left'>Report Type</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>{renderRows()}</TableBody>
            </Table>
            <Box mt={2}>
              <Typography variant='subtitle2'>
                Upon clicking export button, report will be generated and send
                to your email address when ready
              </Typography>
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>CANCEL</Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => null}
              data-cy='button-submit'
            >
              Export
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
