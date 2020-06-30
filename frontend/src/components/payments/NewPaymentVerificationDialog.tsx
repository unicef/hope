import React, { useState } from 'react';
import styled from 'styled-components';
import {
  Button,
  DialogContent,
  DialogTitle,
  Tabs,
  Tab,
  Typography,
} from '@material-ui/core';
import CheckRoundedIcon from '@material-ui/icons/CheckRounded';

import { useSnackbar } from '../../hooks/useSnackBar';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { TabPanel } from '../TabPanel';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

const StyledTabs = styled(Tabs)`
  && {
    max-width: 500px;
  }
`;
const TabsContainer = styled.div`
  border-bottom: 1px solid #e8e8e8;
`;

export function NewPaymentVerificationDialog(): React.ReactElement {
  const [open, setOpen] = useState(false);
  const [selectedTab, setSelectedTab] = useState(0);

  const { showMessage } = useSnackbar();

  // const submit = async (): Promise<void> => {
  //   // const { errors } = await mutate();
  //   const errors = [];
  //   if (errors) {
  //     showMessage('Error while submitting');
  //     return;
  //   }
  //   showMessage('New verification plan created.');
  // };

  const submit = () => console.log('submit');

  return (
    <span>
      <Button
        color='primary'
        variant='contained'
        onClick={() => setOpen(true)}
        data-cy='button-new-plan'
      >
        NEW VERIFICATION PLAN
      </Button>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            <Typography variant='h6'>Create Verification Plan</Typography>
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          {/* <DialogDescription>
            <div>description part</div>
          </DialogDescription> */}
          <TabsContainer>
            <StyledTabs
              value={selectedTab}
              onChange={(event: React.ChangeEvent<{}>, newValue: number) =>
                setSelectedTab(newValue)
              }
              indicatorColor='primary'
              textColor='primary'
              variant='fullWidth'
              aria-label='full width tabs example'
            >
              <Tab label='FULL LIST' />
              <Tab label='RANDOM SAMPLING' />
            </StyledTabs>
          </TabsContainer>
          <TabPanel value={selectedTab} index={0}>
            <div>full list here</div>
          </TabPanel>
          <TabPanel value={selectedTab} index={1}>
            <div>random sampling</div>
          </TabPanel>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>CANCEL</Button>
            <Button
              startIcon={<CheckRoundedIcon />}
              type='submit'
              color='primary'
              variant='contained'
              onClick={submit}
              data-cy='button-submit'
            >
              SAVE
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </span>
  );
}
